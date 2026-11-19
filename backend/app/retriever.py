from .knowledge_base import KNOWLEDGE_CHUNKS

def retrieve(query: str, top_k: int = 1) -> list:
    """
    极简版检索：计算问题中的字符在知识块中出现的频率作为基础打分
    """
    results = []
    for chunk in KNOWLEDGE_CHUNKS:
        # 简单计算重合度（实际企业级会用 BM25 或 向量相似度）
        score = 0
        for char in query:
            if char in chunk["content"] or char in chunk["title"]:
                score += 1
        
        # 如果匹配度大于 0，则视为命中
        if score > 0:
            results.append({"chunk": chunk, "score": score})
            
    # 按分数从高到低排序，取前 top_k 个
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]