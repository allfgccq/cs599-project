import requests
import os
from dotenv import load_dotenv

load_dotenv()

AMAP_API_KEY = os.getenv("AMAP_API_KEY", "demo")


def get_route_info(origin: str, destination: str, transport_type: str = "driving") -> dict:
    """
    获取两地间路线信息
    
    Args:
        origin: 出发地点
        destination: 目的地点
        transport_type: 交通方式: driving | walking | transit
    
    Returns:
        路线信息字典
    """
    base_url = "https://restapi.amap.com/v3/direction"
    
    params = {
        "key": AMAP_API_KEY,
        "origin": origin,
        "destination": destination,
        "type": _get_transport_type_code(transport_type),
        "output": "json"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1":
            route = data.get("route", {})
            paths = route.get("paths", [])
            
            if paths:
                path = paths[0]
                distance = int(path.get("distance", 0))
                duration = int(path.get("duration", 0))
                
                return {
                    "success": True,
                    "data": {
                        "origin": origin,
                        "destination": destination,
                        "transport_type": transport_type,
                        "distance": f"{distance / 1000:.1f}公里" if distance > 1000 else f"{distance}米",
                        "distance_meters": distance,
                        "duration": _format_duration(duration),
                        "duration_seconds": duration,
                        "route_summary": path.get("summary", "")
                    },
                    "error": None
                }
        
        return {
            "success": False,
            "data": None,
            "error": {"code": "API_ERROR", "message": "获取路线信息失败", "details": data.get("info", "")}
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "NETWORK_ERROR", "message": str(e), "details": ""}
        }


def _get_transport_type_code(transport_type: str) -> str:
    """获取交通方式对应的编码"""
    mapping = {
        "driving": "0",
        "walking": "1",
        "transit": "2",
        "bus": "2"
    }
    return mapping.get(transport_type, "0")


def _format_duration(seconds: int) -> str:
    """格式化时间"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    return f"{minutes}分钟"