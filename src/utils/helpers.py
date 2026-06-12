import json
import os
from datetime import datetime


def save_itinerary(itinerary: dict, filepath: str = None):
    """保存行程到文件"""
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"itinerary_{timestamp}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(itinerary, f, ensure_ascii=False, indent=2)
    
    return filepath


def load_itinerary(filepath: str) -> dict:
    """从文件加载行程"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_currency(amount: float) -> str:
    """格式化货币显示"""
    return f"¥{amount:,.2f}"


def format_date(date_str: str) -> str:
    """格式化日期显示"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%Y年%m月%d日")
    except ValueError:
        return date_str


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点间距离（米）"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000
    
    lat1_rad = radians(lat1)
    lng1_rad = radians(lng1)
    lat2_rad = radians(lat2)
    lng2_rad = radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def generate_session_id() -> str:
    """生成唯一会话ID"""
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(os.getpid())


def validate_city_name(city: str) -> bool:
    """验证城市名称是否有效"""
    valid_cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "南京", "西安", "武汉", "重庆"]
    return city in valid_cities


def get_city_coordinates(city: str) -> tuple:
    """获取城市坐标"""
    coordinates = {
        "北京": (39.9042, 116.4074),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.5431, 114.0579),
        "杭州": (30.2741, 120.1552),
        "成都": (30.5728, 104.0668),
        "南京": (32.0603, 118.7969),
        "西安": (34.2619, 108.9463),
        "武汉": (30.5928, 114.3055),
        "重庆": (29.4316, 106.9123)
    }
    return coordinates.get(city, (0, 0))