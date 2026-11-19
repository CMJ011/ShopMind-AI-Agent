import json
import re
from .llm import llm_client

def extract_intent_and_slots(message: str) -> dict:
    # ==========================================
    # 🔥 第一道防线：正则硬拦截
    # ==========================================
    msg_upper = message.upper()
    
    # 1. 拦截单号（只要看到 SM+12位数字，直接抓出来）
    order_match = re.search(r'(SM\d{12})', msg_upper)
    order_no = order_match.group(1) if order_match else None
    
    if order_no:
        if "退款" in message or "退货" in message:
            return {"intent": "apply_refund", "slots": {"order_no": order_no}}
        return {"intent": "query_order", "slots": {"order_no": order_no}}

    # 2. 拦截转人工 / 投诉
    if any(k in message for k in ["转人工", "人工客服", "找真人", "真人客服", "人工"]):
        print(f"🔨 [NLU Rule] 命中转人工关键字！")
        return {"intent": "handoff", "slots": {}}
    if any(k in message for k in ["投诉", "骗子", "破东西", "太差了", "垃圾", "气死"]):
        print(f"🔨 [NLU Rule] 命中投诉关键字！")
        return {"intent": "complain", "slots": {}}

    # 3. 拦截知识/参数咨询
    if any(k in message for k in ["续航", "降噪", "参数", "多久", "几天", "政策", "退换", "规则"]):
        print(f"🔨 [NLU Rule] 命中政策/参数咨询关键字！")
        return {"intent": "query_policy", "slots": {}}
        
    # 4. 拦截未知（促销活动等）
    if "活动" in message or "优惠" in message:
        return {"intent": "unknown", "slots": {}}

    # ==========================================
    # 🔥 第二道防线：大模型 JSON 兜底
    # ==========================================
    prompt = f"""
    请分析用户的意图，并以纯 JSON 格式输出，不要包含任何其他废话。
    可选意图列表：
    - query_order (查询订单、物流)
    - apply_refund (申请退款/退货)
    - query_policy (咨询退换货政策、商品参数、规则)
    - unknown (其他)

    输出格式要求：
    {{"intent": "意图名", "slots": {{"order_no": "提取到的订单号，没有则为null"}}}}

    用户原话：{message}
    """
    messages = [{"role": "user", "content": prompt}]
    result = llm_client.generate(messages)
    
    try:
        text = result["reply"].strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        return json.loads(text)
    except Exception as e:
        print(f"❌ [NLU] JSON 解析失败: {e}")
        return {"intent": "unknown", "slots": {}}