import re
import json
import time  # 🔥 必须有，用于计算总耗时
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .llm import llm_client
from .models import SessionLocal, User, ChatSession, ChatMessage, Trace  # 🔥 必须有 Trace
from .retriever import retrieve
from .nlu import extract_intent_and_slots
from .planner import execute_plan
from .ratelimit import check_rate_limit # 🔥 导入

router = APIRouter()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录或 Token 缺失")
    token = credentials.credentials 
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token 无效")
    return user

class ChatRequest(BaseModel):
    message: str
    session_id: str

@router.post("/chat")
def chat_endpoint(
    req: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🔥 触发限流检查
    check_rate_limit(current_user.token, limit=5, window=60) # 测试用，限制严一点：1分钟最多5次
    
    start_time = time.time()  # 🔥 记录请求开始时间

    # 1. 会话校验
    chat_session = db.query(ChatSession).filter(ChatSession.session_id == req.session_id).first()
    if chat_session:
        if chat_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="越权访问：您无权操作该会话")
    else:
        chat_session = ChatSession(session_id=req.session_id, user_id=current_user.id)
        db.add(chat_session)
        db.commit()

    # 2. 拉取历史
    db_messages = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id).all()
    
    # 3. NLU 意图识别 & Planner 规划
    nlu_result = extract_intent_and_slots(req.message)
    plan_result = execute_plan(nlu_result, current_user.id)
    
    print(f"\n🧠 [Orchestrator] 解析意图: {nlu_result}")
    print(f"🤖 [Orchestrator] 执行规划: {plan_result.get('action')}")

    # 4. 准备上下文变量
    context_text = ""
    valid_kb_ids = []
    reply_text = None
    latency = 0
    model_name = "System (Direct)"
    prompt_tokens = 0
    completion_tokens = 0

    # 5. 根据 Planner 结果处理
    if plan_result["action"] == "handoff":
        reply_text = plan_result["message"]
        chat_session.status = "human_handoff"
        db.commit()
    elif plan_result["action"] == "clarify":
        reply_text = plan_result["message"]
    elif plan_result["action"] == "tool_success":
        reply_text = plan_result["reply"]
    elif plan_result["action"] == "tool_fail":
        reply_text = f"查询失败，原因：{plan_result['error']}"
        
    # 6. 兜底：走 RAG + LLM 生成
    if reply_text is None:
        # 查询重写逻辑
        search_query = req.message
        if any(word in req.message for word in ["它", "那", "这个", "该", "刚才", "上一句"]):
            rewrite_prompt = f"结合以下历史对话，将用户的最新问题重写为一个独立完整的句子，直接输出重写后的话，不要任何废话。\n最新问题：{req.message}"
            messages_rewrite = [{"role": "user", "content": rewrite_prompt}]
            for msg in db_messages[-4:]:
                messages_rewrite.insert(-1, {"role": msg.role, "content": msg.content})
            rewrite_res = llm_client.generate(messages_rewrite)
            search_query = rewrite_res["reply"].strip()
            print(f"🔄 [Query Rewrite] '{req.message}' 重写为: '{search_query}'")

        hits = retrieve(search_query)
        if hits:
            for hit in hits:
                chunk = hit["chunk"]
                context_text += f"[{chunk['id']}] {chunk['title']}: {chunk['content']}\n"
                valid_kb_ids.append(chunk['id'])

        system_prompt = "你是电商客服小满。回答要简洁。"
        if context_text:
            system_prompt += f"\n请根据以下资料回答，不知道就说不知道：\n{context_text}\n引用时加编号如 [KB-001]。"
            
        messages = [{"role": "system", "content": system_prompt}]
        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": req.message})
        
        result = llm_client.generate(messages)
        reply_text = result["reply"]
        latency = result["latency_ms"]
        model_name = result["model"]
        
        # 提取 Token 消耗
        if "usage" in result:
            prompt_tokens = result["usage"].get("prompt_tokens", 0)
            completion_tokens = result["usage"].get("completion_tokens", 0)
        
        # 引用防伪校验
        cited_ids = re.findall(r'\[(KB-[A-Za-z0-9\-]+)\]', reply_text)
        for cid in cited_ids:
            if cid not in valid_kb_ids:
                reply_text = reply_text.replace(f"[{cid}]", "【该引用不存在已被系统拦截】")

    # 7. 落库
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.message)
    ai_msg = ChatMessage(session_id=req.session_id, role="assistant", content=reply_text)
    db.add(user_msg)
    db.add(ai_msg)
    
    # 🔥 记录 Trace
    total_latency = int((time.time() - start_time) * 1000)
    trace = Trace(
        session_id=req.session_id,
        user_message=req.message,
        nlu_intent=nlu_result.get("intent"),
        plan_action=plan_result.get("action"),
        latency_ms=total_latency,
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens
    )
    db.add(trace)
    db.commit()

    return {
        "reply": reply_text,
        "meta": {
            "nlu": nlu_result, 
            "plan": plan_result["action"],
            "model": model_name,
            "latency_ms": latency,
            "total_latency_ms": total_latency
        }
    }