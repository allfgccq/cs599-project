from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any


class ShortTermMemory:
    """短期记忆系统 - 使用 LangGraph MemorySaver"""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def save(self, session_id: str, key: str, value: Any):
        """保存记忆"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id][key] = value
    
    def load(self, session_id: str, key: str = None) -> Any:
        """加载记忆"""
        if session_id not in self.sessions:
            return None
        
        if key is None:
            return self.sessions[session_id]
        
        return self.sessions[session_id].get(key)
    
    def delete(self, session_id: str):
        """删除会话记忆"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_memory_saver(self):
        """获取 MemorySaver 实例"""
        return self.memory
    
    def rollback(self, session_id: str, version: int = 1) -> bool:
        """回滚到上一个版本"""
        history = self.load(session_id, "itinerary_history")
        if history and len(history) > version:
            return True
        return False