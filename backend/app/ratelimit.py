import time
from fastapi import HTTPException

# 记录每个用户的请求时间戳: { "tokenA": [1690000000.0, 1690000005.0] }
request_records = {}

def check_rate_limit(user_token: str, limit: int = 10, window: int = 60):
    """
    滑动窗口限流：每 60 秒最多 10 次请求
    """
    now = time.time()
    if user_token not in request_records:
        request_records[user_token] = []
    
    # 清理过期的请求记录
    request_records[user_token] = [t for t in request_records[user_token] if now - t < window]
    
    # 检查是否超过限制
    if len(request_records[user_token]) >= limit:
        raise HTTPException(status_code=429, detail="请求太频繁，请稍后再试（429 Too Many Requests）")
    
    # 记录本次请求
    request_records[user_token].append(now)