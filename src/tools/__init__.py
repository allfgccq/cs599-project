from .map_tools import get_route_info
from .weather_tools import get_weather_info
from .attraction_tools import search_attractions
from .restaurant_tools import search_restaurants
from .cost_tools import calculate_cost


TRAVEL_TOOLS = [
    {
        "name": "get_route_info",
        "description": "获取两地间路线信息（步行/驾车距离与时间）",
        "func": get_route_info,
        "parameters": {
            "origin": {"type": "string", "description": "出发地点"},
            "destination": {"type": "string", "description": "目的地点"},
            "transport_type": {"type": "string", "description": "交通方式: driving | walking | transit"}
        }
    },
    {
        "name": "get_weather_info",
        "description": "获取目的地天气信息",
        "func": get_weather_info,
        "parameters": {
            "city": {"type": "string", "description": "城市名称"},
            "date": {"type": "string", "description": "查询日期 (YYYY-MM-DD)"}
        }
    },
    {
        "name": "search_attractions",
        "description": "搜索目的地景点",
        "func": search_attractions,
        "parameters": {
            "city": {"type": "string", "description": "城市名称"},
            "keywords": {"type": "string", "description": "搜索关键词", "optional": True},
            "category": {"type": "string", "description": "景点类型: all | natural | cultural | entertainment"},
            "page_size": {"type": "number", "description": "返回数量"}
        }
    },
    {
        "name": "search_restaurants",
        "description": "搜索当地美食餐厅",
        "func": search_restaurants,
        "parameters": {
            "city": {"type": "string", "description": "城市名称"},
            "keywords": {"type": "string", "description": "搜索关键词", "optional": True},
            "cuisine": {"type": "string", "description": "菜系: all | local | chinese | western"},
            "price_range": {"type": "string", "description": "价格区间: all | budget | mid | luxury"},
            "page_size": {"type": "number", "description": "返回数量"}
        }
    },
    {
        "name": "calculate_cost",
        "description": "计算行程费用",
        "func": calculate_cost,
        "parameters": {
            "transport_cost": {"type": "number", "description": "交通费用"},
            "accommodation_cost": {"type": "number", "description": "住宿费用"},
            "attraction_cost": {"type": "number", "description": "景点门票费用"},
            "food_cost": {"type": "number", "description": "餐饮费用"},
            "shopping_cost": {"type": "number", "description": "购物费用"},
            "other_cost": {"type": "number", "description": "其他费用"},
            "budget": {"type": "number", "description": "用户预算", "optional": True}
        }
    }
]


def get_tool_by_name(name: str):
    """根据名称获取工具"""
    for tool in TRAVEL_TOOLS:
        if tool["name"] == name:
            return tool
    return None


def call_tool(name: str, **kwargs):
    """调用工具"""
    tool = get_tool_by_name(name)
    if tool:
        return tool["func"](**kwargs)
    return {"success": False, "data": None, "error": {"code": "NOT_FOUND", "message": f"工具 {name} 不存在"}}
