from typing import Dict, Any, List
from src.memory.long_term_memory import LongTermMemory
from mcp import MCP, MCPConfig, Resource
import json


class TravelMemoryMCP(MCP):
    """MCP Memory Server - 封装标准MCP接口"""
    
    def __init__(self):
        super().__init__(name="TravAgent Memory Server")
        self.long_term_memory = LongTermMemory()
    
    def load_resource(self, resource: Resource) -> Dict[str, Any]:
        """加载资源"""
        user_id = resource.name
        
        if user_id.startswith("memory://"):
            user_id = user_id.replace("memory://", "")
        
        return self.long_term_memory.load_user_memory(user_id)
    
    def list_resources(self) -> List[Resource]:
        """列出资源"""
        return []
    
    def get_config(self) -> MCPConfig:
        """获取配置"""
        return MCPConfig(
            name="TravAgent Memory Server",
            description="旅行助手长期记忆服务",
            version="1.0.0"
        )
    
    def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用方法"""
        if method == "load_long_term_memory":
            user_id = params.get("user_id", "default")
            return self.long_term_memory.load_user_memory(user_id)
        
        elif method == "save_long_term_memory":
            user_id = params.get("user_id", "default")
            preferences = params.get("preferences", {})
            new_trip = params.get("new_trip", {})
            
            if preferences.get("interests"):
                for interest in preferences["interests"]:
                    self.long_term_memory.add_memory(user_id, interest, "interest")
            
            if preferences.get("avoid_places"):
                for place in preferences["avoid_places"]:
                    self.long_term_memory.add_memory(user_id, place, "avoid")
            
            if preferences.get("dietary_restrictions"):
                for restriction in preferences["dietary_restrictions"]:
                    self.long_term_memory.add_memory(user_id, restriction, "dietary")
            
            if new_trip.get("destination"):
                content = f"目的地: {new_trip['destination']}, 评分: {new_trip.get('rating', 0)}"
                self.long_term_memory.add_memory(user_id, content, "trip")
            
            return {"success": True, "message": "记忆保存成功"}
        
        elif method == "search_memory":
            user_id = params.get("user_id", "default")
            query = params.get("query", "")
            top_k = params.get("top_k", 5)
            
            results = self.long_term_memory.search_memory(user_id, query, top_k)
            return {"success": True, "results": results}
        
        else:
            return {"error": f"Unknown method: {method}"}
    
    def shutdown(self):
        """关闭服务"""
        pass


def main():
    """启动MCP服务器"""
    mcp = TravelMemoryMCP()
    mcp.run()


if __name__ == "__main__":
    main()