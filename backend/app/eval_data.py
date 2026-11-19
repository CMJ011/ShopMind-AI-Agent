# 考卷：包含各种意图和期待的回答特征
EVAL_CASES = [
    {"message": "我的耳机续航多久？", "expected_intent": "query_policy", "expected_kb": "KB-003"},
    {"message": "退款几天到账？", "expected_intent": "query_policy", "expected_kb": "KB-002"},
    {"message": "查一下 SM202611100001", "expected_intent": "query_order", "expected_plan": "tool_success", "expected_text": "顺丰速运"},
    {"message": "转人工！", "expected_intent": "handoff", "expected_plan": "handoff"},
    {"message": "我要投诉！", "expected_intent": "complain", "expected_plan": "handoff"},
    {"message": "耳机降噪怎么样？", "expected_intent": "query_policy", "expected_kb": "KB-004"},
    {"message": "你们双十一有活动吗？", "expected_intent": "unknown", "expected_text": "不知道"},
    {"message": "订单 SM202611100002 到哪了", "expected_intent": "query_order", "expected_text": "无权查看"},
]