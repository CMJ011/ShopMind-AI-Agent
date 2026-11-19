from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# 使用 SQLite 数据库，文件名为 shopmind.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./shopmind_v2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    token = Column(String, unique=True, index=True) # 演示用简单的 token

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) 
    status = Column(String, default="active")  # 🔥 加上这行！

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))
    role = Column(String) # user 或 assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(String)
    nlu_intent = Column(String)
    plan_action = Column(String)
    latency_ms = Column(Integer)
    model_name = Column(String)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)    

# 自动建表
Base.metadata.create_all(bind=engine)