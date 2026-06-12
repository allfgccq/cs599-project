import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# 模拟酒店数据（当API调用失败时使用）
MOCK_HOTELS = {
    "杭州": [
        {"name": "西湖大酒店", "star": 5, "price": 800, "rating": 4.8, "location": "西湖附近", "address": "西湖区湖滨路12号"},
        {"name": "杭州国际酒店", "star": 4, "price": 500, "rating": 4.6, "location": "市中心", "address": "拱墅区延安路500号"},
        {"name": "如家快捷酒店", "star": 3, "price": 260, "rating": 4.3, "location": "火车站附近", "address": "江干区城站路20号"},
        {"name": "杭州香格里拉饭店", "star": 5, "price": 980, "rating": 4.9, "location": "西湖边", "address": "西湖区北山山路78号"},
        {"name": "全季酒店", "star": 4, "price": 420, "rating": 4.5, "location": "西溪湿地", "address": "西湖区文二西路803号"}
    ],
    "青岛": [
        {"name": "青岛海景花园大酒店", "star": 5, "price": 900, "rating": 4.9, "location": "八大关景区", "address": "市南区湛山二路2号"},
        {"name": "青岛颐中皇冠假日酒店", "star": 4, "price": 600, "rating": 4.7, "location": "五四广场", "address": "市南区香港中路76号"},
        {"name": "7天连锁酒店", "star": 3, "price": 280, "rating": 4.2, "location": "栈桥附近", "address": "市南区中山路31号"},
        {"name": "青岛海尔洲际酒店", "star": 5, "price": 1100, "rating": 4.8, "location": "奥帆中心", "address": "市南区澳门路98号"}
    ],
    "西安": [
        {"name": "西安索菲特传奇酒店", "star": 5, "price": 1000, "rating": 4.9, "location": "城墙内", "address": "新城区东新街319号"},
        {"name": "西安豪享来温德姆至尊公寓", "star": 4, "price": 550, "rating": 4.6, "location": "大雁塔附近", "address": "雁塔区慈恩路777号"},
        {"name": "汉庭酒店", "star": 3, "price": 240, "rating": 4.3, "location": "火车站", "address": "新城区解放路356号"},
        {"name": "西安威斯汀大酒店", "star": 5, "price": 1200, "rating": 4.8, "location": "大雁塔", "address": "雁塔区慈恩路66号"}
    ],
    "武汉": [
        {"name": "武汉万达瑞华酒店", "star": 5, "price": 850, "rating": 4.8, "location": "楚河汉街", "address": "武昌区东湖路138号"},
        {"name": "武汉华美达光谷大酒店", "star": 4, "price": 480, "rating": 4.5, "location": "光谷", "address": "洪山区珞瑜路726号"},
        {"name": "布丁酒店", "star": 3, "price": 220, "rating": 4.1, "location": "黄鹤楼附近", "address": "武昌区彭刘杨路232号"},
        {"name": "武汉泛海喜来登大酒店", "star": 5, "price": 920, "rating": 4.7, "location": "CBD", "address": "江汉区淮海路248号"}
    ],
    "北京": [
        {"name": "北京国贸大酒店", "star": 5, "price": 1500, "rating": 4.9, "location": "国贸CBD", "address": "朝阳区建国门外大街1号"},
        {"name": "北京王府井希尔顿酒店", "star": 5, "price": 1200, "rating": 4.8, "location": "王府井", "address": "东城区王府井东大街8号"},
        {"name": "如家精选酒店", "star": 3, "price": 380, "rating": 4.4, "location": "天安门附近", "address": "西城区前门西河沿街215号"},
        {"name": "北京四季酒店", "star": 5, "price": 2000, "rating": 4.9, "location": "亮马桥", "address": "朝阳区亮马桥路48号"}
    ],
    "上海": [
        {"name": "上海外滩华尔道夫酒店", "star": 5, "price": 2200, "rating": 4.9, "location": "外滩", "address": "黄浦区中山东一路2号"},
        {"name": "上海浦东丽思卡尔顿酒店", "star": 5, "price": 1800, "rating": 4.8, "location": "陆家嘴", "address": "浦东新区世纪大道8号"},
        {"name": "汉庭优佳酒店", "star": 3, "price": 320, "rating": 4.3, "location": "人民广场", "address": "黄浦区福州路105号"},
        {"name": "上海和平饭店", "star": 5, "price": 1600, "rating": 4.8, "location": "南京东路", "address": "黄浦区南京东路20号"}
    ]
}


def get_hotels(city: str, check_in_date: str = None, check_out_date: str = None, budget: float = None) -> dict:
    """
    获取酒店列表
    
    Args:
        city: 城市名称
        check_in_date: 入住日期（格式：YYYY-MM-DD）
        check_out_date: 退房日期（格式：YYYY-MM-DD）
        budget: 预算（每晚价格上限）
    
    Returns:
        酒店列表字典
    """
    # 优先尝试调用真实API（如果配置了API密钥）
    result = _try_rapid_api(city, check_in_date, check_out_date, budget)
    
    # 如果API调用失败或未配置，使用模拟数据
    if not result["success"]:
        result = _get_mock_hotels(city, budget)
    
    return result


def _try_rapid_api(city: str, check_in_date: str, check_out_date: str, budget: float) -> dict:
    """
    使用RapidAPI调用Booking.com酒店搜索API
    
    API文档: https://rapidapi.com/tipsters/api/booking-search/
    """
    rapid_api_key = os.getenv("RAPID_API_KEY", "ba591c6d29msh15e248fb85c59b4p17611cjsnffafd873503")
    
    if not rapid_api_key or rapid_api_key == "demo":
        return {
            "success": False,
            "hotels": [],
            "error": {"code": "NO_API_KEY", "message": "未配置RapidAPI密钥", "details": ""}
        }
    
    # 城市名称映射（英文名称用于API调用）
    city_mapping = {
        "杭州": "Hangzhou",
        "青岛": "Qingdao",
        "西安": "Xian",
        "武汉": "Wuhan",
        "北京": "Beijing",
        "上海": "Shanghai",
        "南京": "Nanjing",
        "成都": "Chengdu",
        "重庆": "Chongqing",
        "广州": "Guangzhou",
        "深圳": "Shenzhen"
    }
    
    city_en = city_mapping.get(city, city)
    
    # 设置默认日期（如果没有提供）
    if not check_in_date:
        check_in_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    if not check_out_date:
        check_out_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
    
    url = "https://booking-search.p.rapidapi.com/stays/search"
    
    querystring = {
        "city": city_en,
        "checkin": check_in_date,
        "checkout": check_out_date,
        "adults": "2",
        "currency": "CNY"
    }
    
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "booking-search.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # 解析API返回的数据
        hotels = []
        if isinstance(data, list) and data:
            for hotel_data in data[:10]:  # 最多返回10个酒店
                try:
                    hotel = {
                        "name": hotel_data.get("name", "未知酒店"),
                        "star": hotel_data.get("star_rating", 3),
                        "price": int(hotel_data.get("price", {}).get("current", 500)),
                        "rating": float(hotel_data.get("review_score", 4.0)),
                        "location": hotel_data.get("city", city),
                        "address": hotel_data.get("address", "")
                    }
                    hotels.append(hotel)
                except Exception as e:
                    continue
        
        if hotels:
            # 如果有预算限制，过滤酒店
            if budget:
                hotels = [h for h in hotels if h["price"] <= budget]
            
            return {
                "success": True,
                "hotels": hotels,
                "count": len(hotels),
                "city": city,
                "source": "RapidAPI-Booking.com",
                "error": None
            }
        else:
            return {
                "success": False,
                "hotels": [],
                "error": {"code": "NO_RESULTS", "message": "未找到酒店数据", "details": str(data)}
            }
    
    except Exception as e:
        return {
            "success": False,
            "hotels": [],
            "error": {"code": "API_ERROR", "message": str(e), "details": ""}
        }


def _get_mock_hotels(city: str, budget: float = None) -> dict:
    """
    获取模拟酒店数据
    
    Args:
        city: 城市名称
        budget: 预算（每晚价格上限）
    
    Returns:
        酒店列表字典
    """
    hotels = MOCK_HOTELS.get(city, MOCK_HOTELS["杭州"])
    
    # 如果有预算限制，过滤酒店
    if budget:
        hotels = [h for h in hotels if h["price"] <= budget]
    
    # 按价格排序
    hotels = sorted(hotels, key=lambda x: x["price"])
    
    return {
        "success": True,
        "hotels": hotels,
        "count": len(hotels),
        "city": city,
        "source": "Mock Data",
        "error": None
    }


def select_hotel_by_budget(city: str, daily_budget: float) -> dict:
    """
    根据预算选择合适的酒店
    
    Args:
        city: 城市名称
        daily_budget: 每晚预算
    
    Returns:
        选中的酒店信息
    """
    result = get_hotels(city, budget=daily_budget)
    
    if not result["success"] or not result["hotels"]:
        # 如果没有找到合适的酒店，返回默认酒店
        return MOCK_HOTELS.get(city, MOCK_HOTELS["杭州"])[0]
    
    # 选择价格最接近预算但不超过预算的酒店
    hotels = result["hotels"]
    
    if not hotels:
        return MOCK_HOTELS.get(city, MOCK_HOTELS["杭州"])[0]
    
    # 优先选择价格最高的（在预算内）
    selected_hotel = hotels[-1]
    
    return selected_hotel
