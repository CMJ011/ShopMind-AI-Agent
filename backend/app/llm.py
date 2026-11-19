import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMProvider:
    def __init__(self):
        self.mode = os.getenv("LLM_MODE", "mock")
        self.model = os.getenv("LLM_MODEL", "deepseek-chat")
        
        if self.mode == "live":
            self.client = OpenAI(
                api_key=os.getenv("LLM_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL"),
                timeout=10.0
            )

    def generate(self, messages: list) -> dict:
        start_time = time.time()
        
        if self.mode == "mock":
            time.sleep(0.5)
            user_content = messages[-1]["content"]
            if "订单" in user_content:
                reply = "您的订单 SM999999999 已经发货了，预计明天送达哦！"
            else:
                reply = "您好，我是客服小满，请问有什么可以帮您？"
            latency = int((time.time() - start_time) * 1000)
            return {"reply": reply, "provider": "mock", "model": "mock-gpt", "latency_ms": latency}
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                timeout=8.0 # 🔥 缩短超时时间，8秒没响应就熔断
            )
            latency = int((time.time() - start_time) * 1000)
            reply = response.choices[0].message.content
            return {
                "reply": reply,
                "provider": "deepseek",
                "model": self.model,
                "latency_ms": latency,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
        except Exception as e:
            print(f"❌ [LLM Error] 主模型调用失败: {str(e)}，触发 Fallback 降级！")
            
            # 🔥 Fallback 降级逻辑
            # 在真实生产中，这里会去调另一个备用模型（比如千问、文心）
            # 这里我们演示降级到本地写死的兜底回复
            latency = int((time.time() - start_time) * 1000)
            return {
                "reply": "抱歉，当前咨询人数过多，系统正在升级维护中，请您稍后再试或转接人工客服。",
                "provider": "fallback",
                "model": "system_fallback",
                "latency_ms": latency,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0}
            }

llm_client = LLMProvider()