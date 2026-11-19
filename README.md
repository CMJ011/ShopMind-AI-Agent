# ShopMind - 企业级 AI 客服电商平台 MVP

基于 FastAPI + OpenAI(DeepSeek) + SQLite + TailwindCSS 打造的智能客服系统。实现了从“裸模型问答”到“受控工具 Agent”再到“人工协同与自动化评估”的完整演进链。

## ✨ 核心特性
- 🧠 **RAG 知识检索**：支持文档引用、防伪校验、指代 Query 重写。
- 🛠️ **受控工具调用**：确定性 Planner 架构，防止越权查询，硬编码数据零幻觉。
- 🤝 **人机协同闭环**：用户一键转人工，人工坐席无缝接管（含工单列表与历史记录）。
- 🛡️ **企业级保障**：接口限流防刷、Trace 链路追踪、大模型 Fallback 降级。
- 📊 **自动化评估**：包含 8 大场景用例，自动跑分，保证迭代不降智。

## 🚀 快速启动
1. 安装依赖：`uv sync`
2. 配置环境变量：复制 `.env.example` 为 `.env`，填入真实的 LLM_API_KEY
3. 初始化数据库并创建测试用户：
   ```bash
   python -c "from backend.app.models import SessionLocal, User; db = SessionLocal(); db.add(User(username='userA', token='tokenA')); db.commit()"