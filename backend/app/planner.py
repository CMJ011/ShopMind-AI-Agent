from .tools import query_order_tool

def execute_plan(nlu_result: dict, user_id: int) -> dict:
    intent = nlu_result.get("intent", "unknown")
    slots = nlu_result.get("slots", {})

    # 1. 转人工 / 投诉
    if intent == "handoff" or intent == "complain":
        return {
            "action": "handoff", 
            "reason": intent, 
            "message": "非常抱歉给您带来不好的体验。正在为您转接人工客服，请稍候..."
        }

    # 2. 查订单
    if intent == "query_order":
        order_no = slots.get("order_no")
        if not order_no:
            return {"action": "clarify", "message": "请问您要查询的订单号是多少？"}
        
        res = query_order_tool(order_no, user_id)
        if res["success"]:
            data = res["data"]
            reply_text = f"为您查到订单 {order_no} 的信息如下：\n- 商品：{data['product']}\n- 状态：{data['status']}\n- 物流：{data['logistics']}\n- 金额：{data['amount']} 元"
            return {"action": "tool_success", "tool_name": "query_order", "data": data, "reply": reply_text}
        else:
            return {"action": "tool_fail", "error": res["error"]}
            
    # 3. 申请退款（带单号或不带单号）
    if intent == "apply_refund":
        order_no = slots.get("order_no")
        if not order_no:
            return {"action": "rag_search"} # 没单号说明问的是政策
        return {"action": "policy_check", "message": "已为您记录退款申请意向，正在核实订单状态。"}

    # 4. 兜底：知识库检索
    return {"action": "rag_search"}