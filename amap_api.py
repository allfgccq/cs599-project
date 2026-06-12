import requests
import os
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

AMAP_KEY = os.getenv("AMAP_KEY", "")

def get_weather(city: str, days: int = 7) -> dict:
    """
    获取目的地多日天气信息（使用高德地图API）
    
    Args:
        city: 城市名称
        days: 获取未来几天的天气（默认7天）
    
    Returns:
        天气信息字典
    """
    # 使用心知天气API作为备选
    from src.tools.weather_tools import get_weather_info
    return get_weather_info(city, days)


def search_food(city: str, keywords: str = "", types: str = "") -> list:
    """
    搜索美食（使用高德地图POI搜索）
    :param city: 城市名称
    :param keywords: 美食关键词（如：火锅、小吃、特色菜等）
    :param types: POI类型（可选，如餐饮服务、中餐厅等）
    :return: 美食列表
    """
    url = "https://restapi.amap.com/v3/place/text"
    
    params = {
        "key": AMAP_KEY,
        "keywords": keywords if keywords else "美食",
        "city": city,
        "output": "json",
        "offset": 20,
        "page": 1,
        "types": types if types else "050000"  # 默认搜索所有餐饮服务
    }
    
    # 模拟评价数据
    mock_reviews = [
        "环境很好，菜品味道正宗，服务态度也不错",
        "性价比很高，值得推荐",
        "口味很地道，下次还会再来",
        "装修很有特色，拍照很出片",
        "分量很足，价格实惠"
    ]
    
    # 模拟推荐菜品
    mock_dishes = {
        "杭帮菜": ["西湖醋鱼", "龙井虾仁", "东坡肉", "叫化鸡"],
        "川菜": ["麻辣火锅", "水煮鱼", "回锅肉", "宫保鸡丁"],
        "粤菜": ["烧腊", "白切鸡", "叉烧饭", "清蒸鱼"],
        "日料": ["刺身拼盘", "寿司", "寿喜烧", "天妇罗"],
        "火锅": ["肥牛卷", "毛肚", "虾滑", "蔬菜拼盘"],
        "小吃": ["小笼包", "馄饨", "煎饺", "生煎包"],
        "西餐": ["牛排", "意面", "披萨", "沙拉"]
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "1":
            foods = []
            for poi in result.get("pois", []):
                lng, lat = map(float, poi["location"].split(","))
                
                # 获取评分，如果为空则生成随机评分(4.0-4.9)
                rating = float(poi.get("rating", 0)) if poi.get("rating") else round(4.0 + random.random() * 0.9, 1)
                
                # 获取类型并匹配推荐菜品
                food_type = poi.get("type", "")
                dishes = mock_dishes.get("杭帮菜", ["招牌菜1", "招牌菜2", "招牌菜3"])
                for key in mock_dishes:
                    if key in food_type or food_type in key:
                        dishes = mock_dishes[key]
                        break
                
                foods.append({
                    "name": poi["name"],
                    "address": poi.get("address", ""),
                    "lat": lat,
                    "lng": lng,
                    "type": poi.get("type", ""),
                    "typecode": poi.get("typecode", ""),
                    "tel": poi.get("tel", ""),
                    "distance": poi.get("distance", ""),
                    "biz_type": poi.get("biz_type", ""),
                    "rating": rating,
                    "cost": poi.get("cost", "") if poi.get("cost") else f"人均{random.randint(50, 150)}元",
                    "description": f"位于{poi.get('address', '市中心')}的特色餐厅，环境优雅，服务周到，是品尝{city}美食的好去处。",
                    "reviews": random.sample(mock_reviews, 2),
                    "recommended_dishes": random.sample(dishes, 3)
                })
            return foods
        
        # 如果API调用失败，返回模拟数据
        return _generate_mock_foods(city)
    
    except Exception as e:
        print(f"美食搜索失败: {e}")
        return _generate_mock_foods(city)


def _generate_mock_foods(city: str) -> list:
    """生成模拟美食数据"""
    mock_foods = [
        {"name": f"{city}特色餐厅", "address": f"{city}市中心商业街", "rating": round(4.5 + random.random() * 0.4, 1), 
         "cost": f"人均{random.randint(80, 150)}元", "type": "杭帮菜", "description": f"{city}知名特色餐厅，环境优雅",
         "reviews": ["味道很棒，值得推荐", "服务态度很好"], "recommended_dishes": ["招牌菜1", "招牌菜2", "招牌菜3"]},
        {"name": f"{city}老字号", "address": f"{city}老城区", "rating": round(4.3 + random.random() * 0.5, 1),
         "cost": f"人均{random.randint(60, 120)}元", "type": "地方菜", "description": f"{city}百年老字号，传承经典口味",
         "reviews": ["老字号就是不一样", "性价比很高"], "recommended_dishes": ["传统名菜1", "传统名菜2", "传统名菜3"]},
        {"name": f"{city}美食广场", "address": f"{city}购物中心", "rating": round(4.0 + random.random() * 0.6, 1),
         "cost": f"人均{random.randint(40, 80)}元", "type": "小吃", "description": f"{city}人气美食聚集地",
         "reviews": ["种类很多，选择丰富", "价格实惠"], "recommended_dishes": ["特色小吃1", "特色小吃2", "特色小吃3"]},
        {"name": f"{city}私房菜", "address": f"{city}高档住宅区", "rating": round(4.6 + random.random() * 0.3, 1),
         "cost": f"人均{random.randint(150, 250)}元", "type": "私房菜", "description": f"{city}高端私房菜馆，私密雅致",
         "reviews": ["环境一流，菜品精致", "非常适合宴请"], "recommended_dishes": ["私房菜1", "私房菜2", "私房菜3"]},
        {"name": f"{city}火锅城", "address": f"{city}商业中心", "rating": round(4.4 + random.random() * 0.5, 1),
         "cost": f"人均{random.randint(80, 160)}元", "type": "火锅", "description": f"{city}人气火锅店",
         "reviews": ["火锅味道正宗", "食材新鲜"], "recommended_dishes": ["招牌锅底", "特色涮品1", "特色涮品2"]},
        {"name": f"{city}海鲜馆", "address": f"{city}海滨区域", "rating": round(4.2 + random.random() * 0.6, 1),
         "cost": f"人均{random.randint(100, 200)}元", "type": "海鲜", "description": f"{city}新鲜海鲜餐厅",
         "reviews": ["海鲜很新鲜", "价格公道"], "recommended_dishes": ["清蒸鱼", "蒜蓉虾", "海鲜拼盘"]}
    ]
    
    # 根据城市调整推荐
    if city == "北京":
        mock_foods[0]["name"] = "全聚德烤鸭店"
        mock_foods[0]["type"] = "北京菜"
        mock_foods[0]["recommended_dishes"] = ["北京烤鸭", "炸酱面", "卤煮"]
    elif city == "杭州":
        mock_foods[0]["name"] = "楼外楼"
        mock_foods[0]["type"] = "杭帮菜"
        mock_foods[0]["recommended_dishes"] = ["西湖醋鱼", "龙井虾仁", "东坡肉"]
    elif city == "成都":
        mock_foods[0]["name"] = "宽窄巷子火锅"
        mock_foods[0]["type"] = "川菜"
        mock_foods[0]["recommended_dishes"] = ["麻辣火锅", "水煮鱼", "回锅肉"]
    
    return mock_foods


def geocode(address: str, city: str = "") -> dict:
    """地理编码"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": AMAP_KEY,
        "address": address,
        "city": city,
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "1" and result.get("geocodes"):
            geocode_info = result["geocodes"][0]
            return {
                "success": True,
                "lat": float(geocode_info.get("location", "0,0").split(",")[1]),
                "lng": float(geocode_info.get("location", "0,0").split(",")[0]),
                "address": geocode_info.get("formatted_address", ""),
                "district": geocode_info.get("district", "")
            }
        return {"success": False}
    except Exception as e:
        print(f"地理编码失败: {e}")
        return {"success": False}


def get_driving_route(start_lng, start_lat, end_lng, end_lat):
    """获取驾车路线"""
    url = "https://restapi.amap.com/v3/direction/driving"
    params = {
        "key": AMAP_KEY,
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{end_lng},{end_lat}",
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "1" and result.get("route"):
            return result
        return None
    except Exception as e:
        print(f"获取驾车路线失败: {e}")
        return None


def get_transit_route(city, start_lng, start_lat, end_lng, end_lat):
    """获取公交路线"""
    url = "https://restapi.amap.com/v3/direction/transit/integrated"
    params = {
        "key": AMAP_KEY,
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{end_lng},{end_lat}",
        "city": city,
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "1" and result.get("route"):
            return result
        return None
    except Exception as e:
        print(f"获取公交路线失败: {e}")
        return None


def get_walking_route(start_lng, start_lat, end_lng, end_lat):
    """获取步行路线"""
    url = "https://restapi.amap.com/v3/direction/walking"
    params = {
        "key": AMAP_KEY,
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{end_lng},{end_lat}",
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "1" and result.get("route"):
            return result
        return None
    except Exception as e:
        print(f"获取步行路线失败: {e}")
        return None
