from backend.app.nlu import extract_intent_and_slots
from backend.app.planner import execute_plan
from backend.app.eval_data import EVAL_CASES  # 🔥 加上这句导入

def run_eval():
    print("🚀 开始运行自动化评测...")
    passed = 0
    total = len(EVAL_CASES)
    
    for i, case in enumerate(EVAL_CASES):
        print(f"\n--- 测试用例 {i+1}: {case['message']} ---")
        
        # 1. 测 NLU 意图
        nlu_res = extract_intent_and_slots(case["message"])
        intent = nlu_res.get("intent")
        intent_pass = (intent == case["expected_intent"])
        print(f"  [意图] 期望: {case['expected_intent']}, 实际: {intent} -> {'✅' if intent_pass else '❌'}")
        
        # 2. 测 Planner
        plan_res = execute_plan(nlu_res, user_id=1)
        action = plan_res.get("action")
        plan_pass = True
        if "expected_plan" in case:
            plan_pass = (action == case["expected_plan"])
            print(f"  [动作] 期望: {case['expected_plan']}, 实际: {action} -> {'✅' if plan_pass else '❌'}")
            
        # 3. 简易文本断言
        text_pass = True
        if case.get("expected_text") and action == "tool_success":
            text_pass = case["expected_text"] in plan_res.get("reply", "")
            print(f"  [内容] 期望包含: '{case['expected_text']}' -> {'✅' if text_pass else '❌'}")
            
        if intent_pass and plan_pass and text_pass:
            passed += 1
            
    # 生成报告
    accuracy = (passed / total) * 100
    print("\n=========================================")
    print(f"📊 评估报告：通过 {passed}/{total}，总分: {accuracy:.1f}%")
    if accuracy >= 85:
        print("🎉 门禁结果：PASS（达到 85% 基线要求）")
    else:
        print("🚨 门禁结果：FAIL（低于 85% 基线，请检查代码！）")
    print("=========================================")

if __name__ == "__main__":
    run_eval() 