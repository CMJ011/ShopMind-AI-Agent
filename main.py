from fastapi import FastAPI
from backend.app.chat import router as chat_router
from backend.app.agent_api import router as agent_router  # 🔥 必须加上这句导入

app = FastAPI(title="ShopMind API")

app.include_router(chat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")  # 🔥 必须加上这句注册

@app.get("/")
def read_root():
    return {"message": "ShopMind 客服系统已就绪！"}