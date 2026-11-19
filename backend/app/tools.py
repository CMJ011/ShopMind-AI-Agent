import re
from .order_db import ORDERS

def extract_order_no(text: str) -> str:
    # 匹配类似 SM202611100001 的格式
    match = re.search(r'(SM\d{12})', text.upper())
    return match.group(1) if match else None

def query_order_tool(order_no: str, user_id: int):
    """查询订单，且自带权限校验"""
    order = ORDERS.get(order_no)
    if not order:
        return {"success": False, "error": "订单不存在"}
    if order["user_id"] != user_id:
        return {"success": False, "error": "无权查看他人订单"} # 防越权
    return {"success": True, "data": order}