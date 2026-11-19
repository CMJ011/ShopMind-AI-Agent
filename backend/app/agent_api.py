from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import SessionLocal, ChatSession, ChatMessage
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. 获取所有等待人工的会话
@router.get("/agent/sessions")
def get_pending_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.status == "human_handoff").all()
    return [{"session_id": s.session_id, "user_id": s.user_id} for s in sessions]

# 2. 获取某个会话的聊天记录
@router.get("/agent/sessions/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id).all()
    return [{"role": m.role, "content": m.content} for m in messages]

class AgentReply(BaseModel):
    content: str

# 3. 人工客服发送回复
@router.post("/agent/sessions/{session_id}/reply")
def send_reply(session_id: str, req: AgentReply, db: Session = Depends(get_db)):
    chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 将人工回复落库（role 设为 human）
    msg = ChatMessage(session_id=session_id, role="assistant", content=f"【人工客服】{req.content}")
    db.add(msg)
    db.commit()
    return {"status": "ok"}