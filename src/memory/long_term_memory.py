import faiss
import numpy as np
import os
from typing import List, Dict, Any
from langchain.embeddings import OpenAIEmbeddings


class LongTermMemory:
    """长期记忆系统 - 使用向量数据库"""
    
    def __init__(self, persist_dir: str = "./data/memory"):
        self.persist_dir = persist_dir
        self.embedding_model = OpenAIEmbeddings()
        self.index = None
        self.metadata = []
        self._init_faiss()
    
    def _init_faiss(self):
        """初始化 FAISS 索引"""
        os.makedirs(self.persist_dir, exist_ok=True)
        
        index_path = os.path.join(self.persist_dir, "memory.index")
        meta_path = os.path.join(self.persist_dir, "metadata.npy")
        
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            self.metadata = np.load(meta_path, allow_pickle=True).tolist()
        else:
            self.index = faiss.IndexFlatL2(1536)
    
    def _save(self):
        """保存索引和元数据"""
        faiss.write_index(self.index, os.path.join(self.persist_dir, "memory.index"))
        np.save(os.path.join(self.persist_dir, "metadata.npy"), np.array(self.metadata))
    
    def add_memory(self, user_id: str, content: str, memory_type: str = "preference"):
        """添加记忆"""
        embedding = self.embedding_model.embed_query(content)
        embedding = np.array([embedding]).astype('float32')
        
        self.index.add(embedding)
        self.metadata.append({
            "user_id": user_id,
            "content": content,
            "type": memory_type,
            "timestamp": len(self.metadata)
        })
        
        self._save()
    
    def search_memory(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索记忆"""
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.embedding_model.embed_query(query)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                meta = self.metadata[idx]
                if meta["user_id"] == user_id:
                    results.append({
                        "content": meta["content"],
                        "type": meta["type"],
                        "similarity": float(distances[0][i])
                    })
        
        return results
    
    def load_user_memory(self, user_id: str) -> Dict[str, Any]:
        """加载用户所有记忆"""
        user_memories = [m for m in self.metadata if m["user_id"] == user_id]
        
        preferences = {
            "interests": [],
            "avoid_places": [],
            "dietary_restrictions": []
        }
        history = []
        
        for mem in user_memories:
            if mem["type"] == "interest":
                preferences["interests"].append(mem["content"])
            elif mem["type"] == "avoid":
                preferences["avoid_places"].append(mem["content"])
            elif mem["type"] == "dietary":
                preferences["dietary_restrictions"].append(mem["content"])
            elif mem["type"] == "trip":
                history.append({
                    "timestamp": mem.get("timestamp", 0),
                    "content": mem["content"]
                })
        
        return {
            "user_id": user_id,
            "preferences": preferences,
            "history": history
        }
    
    def clear_user_memory(self, user_id: str):
        """清除用户记忆"""
        new_metadata = []
        kept_indices = []
        
        for i, meta in enumerate(self.metadata):
            if meta["user_id"] != user_id:
                new_metadata.append(meta)
                kept_indices.append(i)
        
        if kept_indices:
            kept_indices = np.array(kept_indices)
            self.index = faiss.index_select(self.index, kept_indices)
        
        self.metadata = new_metadata
        self._save()