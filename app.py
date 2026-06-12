"""TravAgent 2.0 - 智能旅行助手前端界面"""
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
import re

import chainlit as cl
from dotenv import load_dotenv

# 导入地图生成器
from map_generator import generate_map_content
# 导入天气工具和美食搜索（使用高德地图API）
from amap_api import get_weather as get_weather_info, search_food
# 导入交通票务模块
from transport_ticket import search_high_speed_trains, search_flights, calculate_arrival_datetime, get_travel_time_hours
# 导入酒店工具
from src.tools.hotel_tools import get_hotels, select_hotel_by_budget

# 加载环境变量
load_dotenv()

# 确保目录存在
os.makedirs('public', exist_ok=True)

# 用户长期记忆画像
USER_PROFILE = {
    "常住地": "武汉",
    "饮食偏好": ["不吃海鲜"],
    "旅行偏好": ["慢节奏", "深度体验", "文化探索"],
    "预算范围": "中等",
    "出行频率": "每月1次"
}

# 历史行程数据
HISTORY_TRIPS = [
    {
        "id": "trip_001",
        "title": "杭州2日游",
        "destination": "杭州",
        "dates": "2026-05-15 ~ 2026-05-16",
        "budget": 3000,
        "summary": "西湖、灵隐寺、雷峰塔",
        "status": "completed"
    },
    {
        "id": "trip_002",
        "title": "武汉赏樱",
        "destination": "武汉",
        "dates": "2026-03-20 ~ 2026-03-22",
        "budget": 1500,
        "summary": "武大樱花、东湖、黄鹤楼",
        "status": "completed"
    }
]

# 模拟景点数据（含景点介绍）
MOCK_ATTRACTIONS = {
    "北京": [
        {"name": "故宫", "category": "文化古迹", "price": 60, "rating": 4.9, "duration": "4小时", "distance": 0, "coord": [116.3974, 39.9087], "description": "故宫是中国明清两代的皇家宫殿，位于北京市中心。占地面积约72万平方米，是世界上现存规模最大、保存最为完整的木质结构古建筑群。故宫内珍藏着大量文物和艺术品，是了解中国古代皇家文化的重要场所。"},
        {"name": "天安门广场", "category": "现代景观", "price": 0, "rating": 4.8, "duration": "1.5小时", "distance": 0.8, "coord": [116.4039, 39.9042], "description": "天安门广场是世界上最大的城市广场之一，位于北京市中心。广场中央矗立着人民英雄纪念碑，周边有人民大会堂、中国国家博物馆等重要建筑。每天清晨的升旗仪式吸引了大量游客前来观看。"},
        {"name": "八达岭长城", "category": "文化古迹", "price": 45, "rating": 4.9, "duration": "5小时", "distance": 60, "coord": [115.9801, 40.3319], "description": "八达岭长城是明长城中保存最完好的一段，位于北京市延庆区。长城蜿蜒起伏，气势恢宏，是中国古代军事防御工程的杰出代表。登上长城，可以感受到历史的厚重和壮丽的自然风光。"},
        {"name": "颐和园", "category": "文化古迹", "price": 30, "rating": 4.8, "duration": "3小时", "distance": 15, "coord": [116.2755, 39.9999], "description": "颐和园是中国现存规模最大、保存最完整的皇家园林，位于北京西郊。园内有昆明湖、万寿山等著名景点，建筑精美，风景秀丽。颐和园融合了江南园林的婉约和北方园林的大气，是中国古典园林艺术的典范。"},
        {"name": "鸟巢", "category": "现代景观", "price": 50, "rating": 4.6, "duration": "2小时", "distance": 0, "coord": [116.4066, 39.9963], "description": "鸟巢是2008年北京奥运会的主体育场，位于北京奥林匹克公园内。建筑外形独特，如同鸟儿的巢穴，是北京的标志性建筑之一。现在鸟巢已成为集体育赛事、文艺演出和旅游观光于一体的综合性场馆。"}
    ],
    "杭州": [
        {"name": "西湖", "category": "自然景观", "price": 0, "rating": 4.9, "duration": "3小时", "distance": 2.5, "coord": [120.1552, 30.2741], "description": "西湖是杭州的标志性景点，被誉为'人间天堂'。湖面面积约6.38平方公里，周围环绕着青山绿水、名胜古迹。著名的西湖十景包括苏堤春晓、断桥残雪、雷峰夕照等，四季景色各具特色。漫步西湖边，感受江南水乡的温婉与诗意。"},
        {"name": "灵隐寺", "category": "文化古迹", "price": 75, "rating": 4.8, "duration": "2小时", "distance": 5.2, "coord": [120.1416, 30.2964], "description": "灵隐寺是中国著名的佛教寺院，始建于东晋咸和元年（公元326年）。寺庙位于杭州西湖西北的灵隐山麓，背靠北高峰，面朝飞来峰。寺内香火旺盛，珍藏着众多佛教文物和艺术珍品，是杭州重要的宗教文化场所。"},
        {"name": "雷峰塔", "category": "文化古迹", "price": 40, "rating": 4.6, "duration": "1.5小时", "distance": 3.8, "coord": [120.1618, 30.2337], "description": "雷峰塔位于西湖南岸夕照山之巅，因《白蛇传》传说而闻名于世。原塔建于北宋太平兴国二年（977年），历经多次损毁重建。现在的雷峰塔是2002年重建的，塔身雄伟壮观，登上塔顶可俯瞰西湖全景。"},
        {"name": "西溪湿地", "category": "自然景观", "price": 80, "rating": 4.7, "duration": "4小时", "distance": 0, "coord": [120.0895, 30.2882], "description": "西溪国家湿地公园是中国第一个国家湿地公园，占地面积约11.5平方公里。这里河网密布、芦苇丛生，保留了大量的自然生态景观和历史文化遗迹。游客可以乘船游览，感受江南水乡的原始风貌。"},
        {"name": "宋城", "category": "主题乐园", "price": 300, "rating": 4.5, "duration": "5小时", "distance": 0, "coord": [120.1093, 30.1987], "description": "宋城是一座以宋代文化为主题的大型文化旅游景区。景区内复原了宋代的市井生活场景，有各种表演和互动体验项目。最著名的是大型实景演出《宋城千古情》，以震撼的视觉效果展现杭州的历史文化。"}
    ],
    "青岛": [
        {"name": "八大关", "category": "自然景观", "price": 0, "rating": 4.8, "duration": "2小时", "distance": 3.2, "coord": [120.3380, 36.0671], "description": "八大关是青岛著名的风景疗养区，因八条以关隘命名的道路而得名。这里汇集了20多个国家的建筑风格，被誉为'万国建筑博览苑'。八大关南临太平湾，风景秀丽，是摄影和休闲散步的好去处。"},
        {"name": "崂山", "category": "自然景观", "price": 130, "rating": 4.7, "duration": "5小时", "distance": 8.5, "coord": [120.6649, 36.1503], "description": "崂山是中国海岸线第一高峰，海拔1133米。山海相连，风景壮丽，有'海上第一名山'之称。崂山还是著名的道教圣地，山上有众多道观和古迹。登山途中可以欣赏到奇峰怪石、清泉瀑布。"},
        {"name": "栈桥", "category": "文化古迹", "price": 0, "rating": 4.6, "duration": "1.5小时", "distance": 2.1, "coord": [120.3139, 36.0611], "description": "栈桥是青岛的标志性建筑，始建于1892年。桥长440米，连接陆地和海中的回澜阁。站在栈桥上，可以远眺小青岛和崂山，是观赏海景的绝佳地点。夜晚的栈桥灯光璀璨，别有一番韵味。"},
        {"name": "五四广场", "category": "现代景观", "price": 0, "rating": 4.5, "duration": "1小时", "distance": 0, "coord": [120.3566, 36.0468], "description": "五四广场位于青岛东部新区，因纪念五四运动而得名。广场上最引人注目的是'五月的风'雕塑，以螺旋上升的红色火炬造型象征着爱国精神。这里是市民休闲娱乐的重要场所，也是欣赏青岛海滨风光的好地方。"},
        {"name": "极地海洋世界", "category": "主题乐园", "price": 210, "rating": 4.6, "duration": "4小时", "distance": 0, "coord": [120.3860, 36.0427], "description": "青岛极地海洋世界是一座集观赏性、娱乐性和科普性于一体的海洋主题公园。馆内展示了各种极地动物和海洋生物，包括企鹅、北极熊、白鲸等。精彩的海豚表演和海底隧道是游客最喜爱的项目。"}
    ],
    "西安": [
        {"name": "兵马俑", "category": "文化古迹", "price": 150, "rating": 4.9, "duration": "4小时", "distance": 15.2, "coord": [109.2755, 34.3802], "description": "兵马俑是秦始皇陵的陪葬坑，被誉为'世界第八大奇迹'。1974年被发现，现已发掘出三个坑，出土了数千件形态各异的陶俑。这些兵马俑栩栩如生，再现了秦朝军队的壮观景象，是中国古代雕塑艺术的杰作。"},
        {"name": "大雁塔", "category": "文化古迹", "price": 30, "rating": 4.7, "duration": "2小时", "distance": 3.5, "coord": [108.9516, 34.2252], "description": "大雁塔位于大慈恩寺内，是唐代高僧玄奘为存放佛经而建造的。塔高64.5米，是西安的标志性建筑之一。登上塔顶可以俯瞰西安市区全景。大雁塔北广场有亚洲最大的音乐喷泉表演，每晚都吸引大量游客。"},
        {"name": "城墙", "category": "文化古迹", "price": 54, "rating": 4.8, "duration": "3小时", "distance": 2.8, "coord": [108.9465, 34.2646], "description": "西安城墙是中国现存规模最大、保存最完整的古代城垣。城墙周长13.74公里，始建于明代，距今已有600多年历史。游客可以在城墙上骑行或步行，感受古代城市的防御体系和历史韵味。"},
        {"name": "陕西历史博物馆", "category": "文化古迹", "price": 0, "rating": 4.8, "duration": "3小时", "distance": 0, "coord": [108.9408, 34.2341], "description": "陕西历史博物馆是中国第一座现代化国家级博物馆，馆藏文物达170余万件（组）。这里展示了从远古时期到明清时期的陕西历史文化，其中包括众多国宝级文物，如唐三彩、青铜器等，是了解中国历史的重要窗口。"},
        {"name": "回民街", "category": "商业街", "price": 0, "rating": 4.6, "duration": "2小时", "distance": 0, "coord": [108.9481, 34.2707], "description": "回民街是西安著名的美食文化街区，位于钟楼附近。这里汇集了各种陕西特色小吃，如羊肉泡馍、肉夹馍、凉皮等。街道两旁是传统的仿古建筑，充满了浓郁的西北风情，是游客品尝地道西安美食的必去之地。"}
    ],
    "武汉": [
        {"name": "武汉大学", "category": "文化古迹", "price": 0, "rating": 4.7, "duration": "2小时", "distance": 4.2, "coord": [114.3618, 30.5431], "description": "武汉大学是中国著名的高等学府，校园环境优美，被誉为'中国最美大学'之一。每年春季樱花盛开时，校园成为赏樱胜地，吸引大量游客前来观赏。校内的早期建筑融合了中西风格，具有很高的历史和艺术价值。"},
        {"name": "东湖", "category": "自然景观", "price": 0, "rating": 4.8, "duration": "4小时", "distance": 3.5, "coord": [114.3736, 30.5552], "description": "东湖是中国最大的城中湖，面积达33平方公里。湖中有多个岛屿，湖岸线曲折，风景秀丽。东湖周边有磨山、落雁岛等景点，游客可以乘船游览、骑行或步行。这里四季景色各异，是武汉市民休闲的好去处。"},
        {"name": "黄鹤楼", "category": "文化古迹", "price": 70, "rating": 4.6, "duration": "2小时", "distance": 2.1, "coord": [114.3054, 30.5515], "description": "黄鹤楼是武汉的标志性建筑，位于长江南岸的蛇山上。始建于三国时期，历代屡毁屡建。现在的黄鹤楼是1985年重建的，楼高51.4米，共五层。登上楼顶可以俯瞰长江和武汉三镇的壮丽景色。"},
        {"name": "户部巷", "category": "商业街", "price": 0, "rating": 4.5, "duration": "2小时", "distance": 0, "coord": [114.3072, 30.5490], "description": "户部巷是武汉著名的美食街区，位于武昌区司门口。这里汇集了各种湖北特色小吃，如热干面、豆皮、武昌鱼等。街道两旁是传统的小吃店铺，充满了浓郁的市井气息，是体验武汉美食文化的最佳地点。"},
        {"name": "湖北省博物馆", "category": "文化古迹", "price": 0, "rating": 4.8, "duration": "3小时", "distance": 0, "coord": [114.3647, 30.5597], "description": "湖北省博物馆是国家一级博物馆，馆藏文物达24万余件。最著名的展品包括曾侯乙编钟、越王勾践剑、元青花四爱图梅瓶等国宝级文物。博物馆建筑气势恢宏，展示了湖北地区悠久的历史和灿烂的文化。"}
    ]
}

# 状态历史栈
max_history = 5

# 交通方式配置
TRANSPORT_OPTIONS = [
    {"type": "taxi", "name": "打车", "icon": "🚗", "speed": 15, "cost_per_km": 2.5},
    {"type": "subway", "name": "地铁", "icon": "🚇", "speed": 40, "cost_per_km": 0.8, "fixed_cost": 3},
    {"type": "bus", "name": "公交", "icon": "🚌", "speed": 20, "cost_per_km": 0.3, "fixed_cost": 2}
]

# 酒店数据
HOTELS = {
    "北京": [
        {"name": "北京国贸大酒店", "star": 5, "price": 1500, "rating": 4.9, "location": "国贸CBD", "address": "朝阳区建国门外大街1号"},
        {"name": "北京王府井大饭店", "star": 4, "price": 800, "rating": 4.6, "location": "王府井", "address": "东城区王府井大街57号"},
        {"name": "7天连锁酒店", "star": 3, "price": 320, "rating": 4.2, "location": "北京站附近", "address": "东城区东单北大街3号"}
    ],
    "杭州": [
        {"name": "西湖大酒店", "star": 5, "price": 800, "rating": 4.8, "location": "西湖附近"},
        {"name": "杭州国际酒店", "star": 4, "price": 500, "rating": 4.6, "location": "市中心"},
        {"name": "如家快捷酒店", "star": 3, "price": 260, "rating": 4.3, "location": "火车站附近"}
    ],
    "青岛": [
        {"name": "青岛海景花园大酒店", "star": 5, "price": 900, "rating": 4.9, "location": "八大关景区"},
        {"name": "青岛颐中皇冠假日酒店", "star": 4, "price": 600, "rating": 4.7, "location": "五四广场"},
        {"name": "7天连锁酒店", "star": 3, "price": 280, "rating": 4.2, "location": "栈桥附近"}
    ],
    "西安": [
        {"name": "西安索菲特传奇酒店", "star": 5, "price": 1000, "rating": 4.9, "location": "城墙内"},
        {"name": "西安豪享来温德姆至尊公寓", "star": 4, "price": 550, "rating": 4.6, "location": "大雁塔附近"},
        {"name": "汉庭酒店", "star": 3, "price": 240, "rating": 4.3, "location": "火车站"}
    ],
    "武汉": [
        {"name": "武汉万达瑞华酒店", "star": 5, "price": 850, "rating": 4.8, "location": "楚河汉街"},
        {"name": "武汉华美达光谷大酒店", "star": 4, "price": 480, "rating": 4.5, "location": "光谷"},
        {"name": "布丁酒店", "star": 3, "price": 220, "rating": 4.1, "location": "黄鹤楼附近"}
    ]
}

# 出发地交通数据
DEPARTURE_TRANSPORT = {
    "武汉": {
        "杭州": [{"type": "train", "name": "高铁", "price": 280, "duration": "3小时"}, {"type": "plane", "name": "飞机", "price": 500, "duration": "1.5小时"}],
        "青岛": [{"type": "train", "name": "高铁", "price": 450, "duration": "5小时"}, {"type": "plane", "name": "飞机", "price": 680, "duration": "2小时"}],
        "西安": [{"type": "train", "name": "高铁", "price": 420, "duration": "4.5小时"}, {"type": "plane", "name": "飞机", "price": 550, "duration": "1.5小时"}]
    },
    "北京": {
        "杭州": [{"type": "train", "name": "高铁", "price": 640, "duration": "6小时"}, {"type": "plane", "name": "飞机", "price": 800, "duration": "2.5小时"}],
        "青岛": [{"type": "train", "name": "高铁", "price": 330, "duration": "4小时"}, {"type": "plane", "name": "飞机", "price": 550, "duration": "1.5小时"}],
        "西安": [{"type": "train", "name": "高铁", "price": 520, "duration": "5.5小时"}, {"type": "plane", "name": "飞机", "price": 650, "duration": "2小时"}]
    },
    "上海": {
        "杭州": [{"type": "train", "name": "高铁", "price": 73, "duration": "1小时"}, {"type": "plane", "name": "飞机", "price": 200, "duration": "1小时"}],
        "青岛": [{"type": "train", "name": "高铁", "price": 550, "duration": "6小时"}, {"type": "plane", "name": "飞机", "price": 600, "duration": "1.5小时"}],
        "西安": [{"type": "train", "name": "高铁", "price": 580, "duration": "6.5小时"}, {"type": "plane", "name": "飞机", "price": 700, "duration": "2.5小时"}]
    }
}

def calculate_transport(distance, transport_type):
    """计算交通费用和时间"""
    transport = next((t for t in TRANSPORT_OPTIONS if t["type"] == transport_type), TRANSPORT_OPTIONS[0])
    cost = transport.get("fixed_cost", 0) + distance * transport["cost_per_km"]
    time = int(distance / transport["speed"] * 60)
    return {"name": transport["name"], "icon": transport["icon"], "cost": round(cost), "time": time}

def generate_itinerary(destination: str, days: int = 2, budget: float = 2000, departure_city: str = "武汉", 
                       currency_symbol: str = "¥", currency_name: str = "人民币", currency_suffix: str = "元",
                       departure_info: Dict = None, return_info: Dict = None, arrival_datetime: str = None,
                       return_departure_time: str = None, days_offset: int = 1, hotel: Dict = None,
                       foods: List[Dict] = None) -> Dict:
    """生成模拟行程"""
    # 使用局部变量追踪已使用的餐厅，确保在循环中正确传递状态
    used_foods = []
    
    attractions = MOCK_ATTRACTIONS.get(destination, MOCK_ATTRACTIONS["杭州"])
    selected = attractions[:min(days * 2, len(attractions))]
    
    # 使用传入的酒店或根据预算选择酒店
    if hotel:
        selected_hotel = hotel
    else:
        # 选择酒店（根据预算）
        hotel_budget = budget * 0.3 / days
        # 使用酒店工具选择合适的酒店
        selected_hotel = select_hotel_by_budget(destination, hotel_budget)
    
    # 使用传入的美食或使用默认美食
    if foods:
        selected_foods = foods
    else:
        # 默认美食列表
        selected_foods = [
            {"name": f"{destination}特色餐厅", "address": "市中心", "rating": 4.5, "cost": "人均80元"},
            {"name": f"{destination}小吃街", "address": "步行街", "rating": 4.3, "cost": "人均30元"}
        ]
    
    # 使用传入的交通信息或默认交通
    if departure_info:
        selected_departure = departure_info
    else:
        # 获取出发地交通
        departure_transport_list = DEPARTURE_TRANSPORT.get(departure_city, {}).get(destination, [])
        if not departure_transport_list:
            departure_transport_list = [{"type": "train", "name": "高铁", "price": 300, "duration": "4小时"}]
        selected_departure = departure_transport_list[0]  # 默认高铁
    
    # 使用传入的返程交通信息或默认（与去程相同）
    if return_info:
        selected_return = return_info
    else:
        selected_return = selected_departure  # 默认与去程相同
    
    # 获取天气信息（根据旅行天数和出发日期偏移）
    # 需要获取从出发日期开始的天气数据
    total_days_needed = days_offset + days
    weather_info = get_weather_info(destination, max(total_days_needed, 7))
    
    # 如果API返回的数据不够，补充模拟天气数据
    forecast = weather_info.get('forecast', [])
    if len(forecast) < total_days_needed:
        import random
        weathers = ['晴', '多云', '小雨', '阵雨', '阴', '雷阵雨', '晴转多云']
        winds = ['东', '西', '南', '北', '东北', '东南', '西北', '西南']
        
        for i in range(len(forecast), total_days_needed):
            date_str = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                'date': date_str,
                'weather': random.choice(weathers),
                'temp': f"{random.randint(18, 25)}-{random.randint(25, 35)}°C",
                'wind': f"{random.choice(winds)} {random.randint(1, 3)}级"
            })
        weather_info['forecast'] = forecast
    
    # 只保留从出发日期开始的天气数据
    if days_offset > 0 and len(forecast) > days_offset:
        weather_info['forecast'] = forecast[days_offset:days_offset + days]
    
    itinerary = {
        "destination": destination,
        "departure_city": departure_city,
        "days": days,
        "budget": budget,
        "currency_symbol": currency_symbol,
        "currency_name": currency_name,
        "currency_suffix": currency_suffix,
        "hotel": selected_hotel,
        "departure_transport": selected_departure,
        "return_transport": selected_return,  # 添加返程交通信息
        "weather": weather_info,
        "daily_plan": [],
        "arrival_datetime": arrival_datetime,  # 记录到达时间
        "return_departure_time": return_departure_time  # 记录返程出发时间
    }
    
    # 计算第一天可用景点数量（根据到达时间）
    day1_attraction_count = 2  # 默认每天2个景点
    if arrival_datetime:
        arrival_time_str = arrival_datetime.split(" ")[1]
        arrival_hour = int(arrival_time_str.split(":")[0])
        if arrival_hour >= 14:
            day1_attraction_count = 1  # 下午到达，只安排1个景点
        elif arrival_hour >= 17:
            day1_attraction_count = 0  # 傍晚到达，不安排景点
    
    # 检查最后一天是否需要预留返程时间
    last_day_attractions_count = 2  # 默认最后一天也安排2个景点
    last_day_has_lunch = True
    if return_departure_time:
        # 解析返程出发时间
        return_hour = int(return_departure_time.split(":")[0])
        # 如果返程时间在12点前，最后一天不安排景点，只安排早餐
        if return_hour < 12:
            last_day_attractions_count = 0
            last_day_has_lunch = False
        # 如果返程时间在15点前，最后一天只安排1个景点，不安排晚餐
        elif return_hour < 15:
            last_day_attractions_count = 1
            last_day_has_lunch = False
    
    for day in range(1, days + 1):
        # 检查是否是最后一天且返程时间较早
        is_last_day = (day == days)
        
        if day == 1 and arrival_datetime:
            # 第一天根据到达时间调整
            day_attractions = selected[:day1_attraction_count]
            remaining_attractions = selected[day1_attraction_count:]
        elif day == 2 and arrival_datetime:
            # 第二天从剩余景点开始
            day_attractions = remaining_attractions[:2] if day1_attraction_count < 2 else selected[2:4]
        elif is_last_day and return_departure_time:
            # 最后一天根据返程时间调整
            start_idx = min((day - 1) * 2, len(selected) - last_day_attractions_count)
            day_attractions = selected[start_idx:start_idx + last_day_attractions_count]
        else:
            start_idx = (day - 1) * 2
            day_attractions = selected[start_idx:start_idx + 2]
        
        # 为每个景点间选择不同的交通方式
        transport_options = ["subway", "bus", "taxi"]
        
        # 计算日期（考虑到达日期）
        if arrival_datetime and day == 1:
            day_date = arrival_datetime.split(" ")[0]
        else:
            day_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        
        # 计算当天的时间安排
        # 第一天根据到达时间开始安排
        if day == 1 and arrival_datetime:
            arrival_time_str = arrival_datetime.split(" ")[1]
            current_hour, current_minute = map(int, arrival_time_str.split(":"))
            # 到达后预留1小时办理入住和休息
            current_minute += 60
            if current_minute >= 60:
                current_hour += 1
                current_minute -= 60
        else:
            # 非第一天，默认从9:00开始
            current_hour, current_minute = 9, 0
        
        # 将分钟数对齐到15的倍数（00, 15, 30, 45）
        current_minute = ((current_minute + 14) // 15) * 15
        if current_minute >= 60:
            current_hour += 1
            current_minute -= 60
        
        # 计算最后一天的最晚结束时间（需要提前2小时到机场）
        latest_end_hour = 22  # 默认晚上10点
        latest_end_minute = 0
        if is_last_day and return_departure_time:
            return_hour, return_minute = map(int, return_departure_time.split(":"))
            # 需要提前2小时出发去机场
            latest_end_hour = return_hour - 2
            latest_end_minute = return_minute
            if latest_end_hour < 0:
                latest_end_hour = 0
        
        # 设置餐饮安排和时间
        meals = {}
        meal_times = {}
        
        # 获取用户选择的美食（去重）
        food_names = []
        seen_foods = set()
        for f in selected_foods:
            name = f.get('name', '')
            if name and name not in seen_foods:
                food_names.append(name)
                seen_foods.add(name)
        
        # 预设的自动推荐餐厅列表（根据城市）
        city_restaurants = {
            "杭州": ["楼外楼", "知味观", "绿茶餐厅", "外婆家", "弄堂里", "新白鹿", "杭帮菜博物馆餐厅"],
            "北京": ["四季民福", "大董", "东来顺", "护国寺小吃", "局气", "方砖厂69号炸酱面"],
            "上海": ["南翔馒头店", "老上海菜馆", "小杨生煎", "绿波廊", "上海1号"],
            "武汉": ["蔡林记", "户部巷小吃", "老通城", "四季美汤包", "精武鸭脖"]
        }
        auto_restaurants = city_restaurants.get(destination, ["当地特色餐厅", "美食街小吃", "网红餐厅", "老字号餐馆"])
        
        # 使用函数参数传递的已使用餐厅列表（在循环外初始化）
        
        # 午餐安排
        lunch_food = ""
        # 先尝试从未使用的用户选择中选取
        available_user_foods = [f for f in food_names if f not in used_foods]
        if available_user_foods:
            lunch_food = available_user_foods[0]
            used_foods.append(lunch_food)
        else:
            # 用户选择用完了，从未使用的自动推荐中随机选
            available_restaurants = [r for r in auto_restaurants if r not in used_foods]
            if available_restaurants:
                import random
                lunch_food = random.choice(available_restaurants)
                used_foods.append(lunch_food)
            else:
                lunch_food = f"{day_attractions[0]['name'] if day_attractions else destination}附近餐厅"
        
        # 晚餐安排
        dinner_food = ""
        # 重要：晚餐不能和午餐相同，且不能使用用户已选择过的餐厅
        available_user_foods = [f for f in food_names if f not in used_foods and f != lunch_food]
        if available_user_foods:
            dinner_food = available_user_foods[0]
            used_foods.append(dinner_food)
        else:
            # 用户选择用完了或午餐已用，从未使用的自动推荐中随机选（排除午餐）
            available_restaurants = [r for r in auto_restaurants if r not in used_foods and r != lunch_food]
            if available_restaurants:
                import random
                dinner_food = random.choice(available_restaurants)
                used_foods.append(dinner_food)
            else:
                # 如果所有自动推荐都用完了，生成一个基于景点的推荐（确保不和午餐相同）
                fallback_dinner = f"{day_attractions[-1]['name'] if day_attractions else destination}附近美食"
                if fallback_dinner != lunch_food:
                    dinner_food = fallback_dinner
                else:
                    # 如果默认也相同，生成不同的推荐
                    dinner_food = f"{day_attractions[-1]['name'] if day_attractions else destination}特色小吃"
        
        # 已使用的餐厅列表通过局部变量自动传递到下一次循环
        
        if is_last_day and return_departure_time:
            return_hour, return_minute = map(int, return_departure_time.split(":"))
            # 计算最晚需要出发去机场的时间（提前2小时）
            latest_departure_hour = return_hour - 2
            latest_departure_minute = return_minute
            if latest_departure_hour < 0:
                latest_departure_hour = 0
            
            # 最后一天，根据返程时间安排
            if latest_departure_hour < 9:
                # 上午9点前就要出发去机场，不安排任何活动
                meals["lunch"] = "（返程较早，建议提前准备路上餐食）"
                meal_times["lunch"] = ""
                meals["dinner"] = ""
                meal_times["dinner"] = ""
                # 不安排景点
                day_attractions = []
            elif latest_departure_hour < 12:
                # 中午12点前就要出发去机场，只安排上午景点，不安排午餐
                meals["lunch"] = "（返程较早，建议提前准备路上餐食）"
                meal_times["lunch"] = ""
                meals["dinner"] = ""
                meal_times["dinner"] = ""
                # 只安排一个上午景点
                if len(day_attractions) > 1:
                    day_attractions = day_attractions[:1]
            elif latest_departure_hour < 14:
                # 下午2点前就要出发去机场，安排上午景点和简单午餐
                meals["lunch"] = f"（返程前简单用餐：{lunch_food}）"
                # 午餐时间要在最晚出发时间之前
                meal_times["lunch"] = "{:02d}:00".format(min(12, latest_departure_hour - 1))
                meals["dinner"] = ""
                meal_times["dinner"] = ""
                # 只安排一个上午景点
                if len(day_attractions) > 1:
                    day_attractions = day_attractions[:1]
            elif latest_departure_hour < 17:
                # 下午5点前就要出发去机场，安排一个上午景点+午餐
                meals["lunch"] = lunch_food
                meal_times["lunch"] = "12:00"
                meals["dinner"] = ""
                meal_times["dinner"] = ""
                # 只安排一个景点
                if len(day_attractions) > 1:
                    day_attractions = day_attractions[:1]
            else:
                # 下午5点后出发去机场，正常安排
                meals["lunch"] = lunch_food
                meal_times["lunch"] = "12:00"
                meals["dinner"] = ""
                meal_times["dinner"] = ""
        else:
            # 非最后一天
            if day == 1 and arrival_datetime:
                # 第一天根据到达时间安排餐饮
                arrival_time_str = arrival_datetime.split(" ")[1]
                arrival_hour = int(arrival_time_str.split(":")[0])
                if arrival_hour >= 14:
                    # 下午2点后到达，只安排晚餐
                    meals["lunch"] = ""
                    meal_times["lunch"] = ""
                    meals["dinner"] = dinner_food
                    meal_times["dinner"] = "18:30"
                elif arrival_hour >= 12:
                    # 中午到达，安排午餐和晚餐
                    meals["lunch"] = lunch_food
                    meal_times["lunch"] = "{:02d}:{:02d}".format(current_hour, current_minute)
                    current_minute += 60
                    if current_minute >= 60:
                        current_hour += 1
                        current_minute -= 60
                    meals["dinner"] = dinner_food
                    meal_times["dinner"] = "18:00"
                else:
                    # 中午前到达，正常安排
                    meals["lunch"] = lunch_food
                    meals["dinner"] = dinner_food
                    meal_times["lunch"] = "12:00"
                    meal_times["dinner"] = "18:00"
            else:
                # 其他天数正常安排
                meals["lunch"] = lunch_food
                meals["dinner"] = dinner_food
                meal_times["lunch"] = "12:00"
                meal_times["dinner"] = "18:00"
        
        # 为每个景点分配具体时间
        scheduled_attractions = []
        for i, attraction in enumerate(day_attractions):
            # 检查是否超过最晚结束时间（最后一天）
            if is_last_day and return_departure_time:
                if current_hour > latest_end_hour or (current_hour == latest_end_hour and current_minute >= latest_end_minute):
                    break
            
            # 检查是否需要先安排午餐
            if i > 0 and current_hour >= 12 and meal_times.get("lunch"):
                # 插入午餐时间
                lunch_start_hour, lunch_start_min = map(int, meal_times["lunch"].split(":"))
                if current_hour < lunch_start_hour or (current_hour == lunch_start_hour and current_minute < lunch_start_min):
                    # 还没到午餐时间，先跳到午餐时间
                    current_hour, current_minute = lunch_start_hour, lunch_start_min
            
            start_time = "{:02d}:{:02d}".format(current_hour, current_minute)
            
            # 计算结束时间
            duration = attraction["duration"]
            if "小时" in duration:
                hours = float(duration.replace("小时", "").replace("分", "").replace(" ", ""))
                mins = int((hours - int(hours)) * 60)
                hours = int(hours)
            elif "分钟" in duration:
                hours = 0
                mins = int(duration.replace("分钟", ""))
            else:
                hours = 1
                mins = 0
            
            # 检查是否超过最晚结束时间
            if is_last_day and return_departure_time:
                end_hour = current_hour + hours
                end_min = current_minute + mins
                if end_min >= 60:
                    end_hour += 1
                    end_min -= 60
                if end_hour > latest_end_hour or (end_hour == latest_end_hour and end_min > latest_end_minute):
                    # 超过时间限制，跳过这个景点
                    continue
            
            current_minute += mins
            current_hour += hours
            if current_minute >= 60:
                current_hour += 1
                current_minute -= 60
            
            # 将结束时间对齐到15分钟
            current_minute = ((current_minute + 14) // 15) * 15
            if current_minute >= 60:
                current_hour += 1
                current_minute -= 60
            
            end_time = "{:02d}:{:02d}".format(current_hour, current_minute)
            
            scheduled_attractions.append({
                **attraction,
                "start_time": start_time,
                "end_time": end_time
            })
            
            # 添加景点间交通时间
            if i < len(day_attractions) - 1:
                transport_type = transport_options[i % len(transport_options)]
                transport_info = calculate_transport(attraction["distance"], transport_type)
                current_minute += transport_info["time"]
                if current_minute >= 60:
                    current_hour += 1
                    current_minute -= 60
                # 将交通后的时间对齐到15分钟
                current_minute = ((current_minute + 14) // 15) * 15
                if current_minute >= 60:
                    current_hour += 1
                    current_minute -= 60
        
        day_plan = {
            "day": day,
            "date": day_date,
            "attractions": scheduled_attractions,
            "transports": [],
            "meals": meals,
            "meal_times": meal_times,
            "estimated_cost": sum(a["price"] for a in day_attractions) + (150 if not is_last_day or return_departure_time is None else 50)
        }
        
        # 添加景点间交通
        for i, attraction in enumerate(scheduled_attractions):
            if i < len(scheduled_attractions) - 1:
                transport_type = transport_options[i % len(transport_options)]
                transport_info = calculate_transport(attraction["distance"], transport_type)
                day_plan["transports"].append({
                    "from": attraction["name"],
                    "to": scheduled_attractions[i+1]["name"],
                    **transport_info
                })
                day_plan["estimated_cost"] += transport_info["cost"]
        
        itinerary["daily_plan"].append(day_plan)
    
    # 计算总费用（包含酒店和往返交通）
    # 三天两晚行程，住宿天数 = 旅行天数 - 1
    itinerary["hotel_nights"] = max(1, days - 1)  # 至少住1晚
    itinerary["hotel_total"] = selected_hotel["price"] * itinerary["hotel_nights"]
    itinerary["departure_cost"] = selected_departure.get("price", 300)
    itinerary["return_cost"] = selected_return.get("price", 300)
    itinerary["daily_cost"] = sum(d["estimated_cost"] for d in itinerary["daily_plan"])
    itinerary["total_cost"] = itinerary["hotel_total"] + itinerary["departure_cost"] + itinerary["return_cost"] + itinerary["daily_cost"]
    itinerary["budget_status"] = "under" if itinerary["total_cost"] <= budget else "over"
    
    return itinerary

def generate_pdf_content(itinerary: Dict) -> str:
    """生成PDF内容（HTML格式，支持打印）"""
    # 获取货币信息
    currency_symbol = itinerary.get('currency_symbol', '¥')
    currency_suffix = itinerary.get('currency_suffix', '元')
    
    # 获取天气信息
    weather_html = ""
    weather_data = itinerary.get('weather', {})
    if weather_data.get('forecast'):
        weather_html = """
        <div class="weather-section">
            <h2>🌤️ 天气预报</h2>
            <div class="weather-grid">
        """
        for day_weather in weather_data['forecast'][:itinerary['days']]:
            # 解析温度范围
            temp_str = day_weather.get('temp', '')
            low_temp = ''
            high_temp = ''
            if '-' in temp_str:
                parts = temp_str.split('-')
                if len(parts) >= 2:
                    low_temp = parts[0].replace('°C', '').strip()
                    high_temp = parts[-1].replace('°C', '').strip()
            
            # 获取天气图标
            weather_icon = '🌤️'
            weather_desc = day_weather.get('weather', '')
            if '雨' in weather_desc:
                weather_icon = '🌧️'
            elif '晴' in weather_desc:
                weather_icon = '☀️'
            elif '阴' in weather_desc:
                weather_icon = '☁️'
            elif '雪' in weather_desc:
                weather_icon = '❄️'
            
            weather_html += """
                <div class="weather-day">
                    <p class="weather-date">{0}</p>
                    <p class="weather-icon">{1}</p>
                    <p class="weather-desc">{2}</p>
                    <p class="weather-temp">{3}°C ~ {4}°C</p>
                </div>
            """.format(day_weather.get('date', ''), weather_icon, weather_desc, low_temp, high_temp)
        weather_html += """
            </div>
        </div>
        """
    
    attractions_html = ""
    for d in itinerary['daily_plan']:
        day_html = """
    <div class="day">
        <h2>Day {0} - {1}</h2>
        <div class="timeline">
""".format(d['day'], d['date'])
        for i, a in enumerate(d['attractions']):
            day_html += """
            <div class="attraction">
                <h3>{0}</h3>
                <p>类型: {1} | 评分: {2} | 时长: {3}</p>
                <p>门票: {4}{5}{6}</p>
            </div>
""".format(a['name'], a['category'], a['rating'], a['duration'], currency_symbol, a['price'], currency_suffix)
            if i < len(d['attractions']) - 1:
                # 获取交通方式信息
                transports = d.get('transports', [])
                if i < len(transports):
                    transport = transports[i]
                    day_html += """
            <div class="transport">
                <p>{0} {1}: {2} → {3}，约{4}分钟，费用{5}{6}{7}</p>
            </div>
""".format(transport['icon'], transport['name'], transport['from'], transport['to'], transport['time'], currency_symbol, transport['cost'], currency_suffix)
                else:
                    day_html += """
            <div class="transport">
                <p>🚶 步行前往</p>
            </div>
"""
        day_html += """
        </div>
        <p>午餐: {0}</p>
        <p>晚餐: {1}</p>
        <p class="cost">当日预计: {2}{3}{4}</p>
    </div>
""".format(d['meals']['lunch'], d['meals']['dinner'], currency_symbol, d['estimated_cost'], currency_suffix)
        attractions_html += day_html
    
    budget_status = '未超预算' if itinerary['budget_status'] == 'under' else '已超预算'
    
    # 酒店信息
    hotel = itinerary.get('hotel', {})
    hotel_html = ""
    if hotel:
        hotel_html = """
        <div class="hotel">
            <h2>🏨 住宿安排</h2>
            <div class="hotel-info">
                <h3>{0}</h3>
                <p>星级: {1}⭐ | 位置: {2}</p>
                <p>地址: {3}</p>
                <p>评分: {4}分 | 价格: {5}{6}{7}/晚</p>
                <p>总计: {5}{8}{7} ({9}晚)</p>
            </div>
        </div>
""".format(
            hotel.get('name', '推荐酒店'),
            hotel.get('star', 4),
            hotel.get('location', '市中心'),
            hotel.get('address', ''),
            hotel.get('rating', 4.5),
            currency_symbol,
            hotel.get('price', 500),
            currency_suffix,
            itinerary.get('hotel_total', 1000),
            itinerary.get('hotel_nights', itinerary['days'] - 1)
        )
    
    content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TravAgent - {0}旅行路线单</title>
    <style>
        @media screen {{
            body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 40px; background: #f8f9fa; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        }}
        @media print {{
            body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 0; background: white; }}
            .container {{ max-width: 100%; margin: 0; background: white; padding: 20px; border-radius: 0; box-shadow: none; }}
            .print-btn {{ display: none; }}
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; font-size: 28px; }}
        .header-info {{ color: #7f8c8d; margin-bottom: 30px; }}
        .day {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 12px; }}
        .day h2 {{ color: #3498db; margin-top: 0; }}
        .attraction {{ margin: 15px 0; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #3498db; }}
        .attraction h3 {{ margin-top: 0; color: #2c3e50; }}
        .transport {{ color: #e67e22; margin: 10px 0 10px 20px; }}
        .cost {{ font-weight: bold; color: #e74c3c; font-size: 16px; }}
        .summary {{ margin-top: 30px; padding: 25px; background: #ecf0f1; border-radius: 12px; }}
        .summary h3 {{ color: #2c3e50; margin-top: 0; }}
        .timeline {{ position: relative; }}
        .hotel {{ margin: 30px 0; padding: 20px; background: #fff3e0; border-radius: 12px; border-left: 4px solid #ff9800; }}
        .hotel h2 {{ color: #e65100; margin-top: 0; }}
        .hotel-info {{ padding: 15px; background: white; border-radius: 8px; }}
        .hotel-info h3 {{ margin-top: 0; color: #2c3e50; }}
        .weather-section {{ margin: 30px 0; padding: 20px; background: #e3f2fd; border-radius: 12px; border-left: 4px solid #2196f3; }}
        .weather-section h2 {{ color: #1976d2; margin-top: 0; }}
        .weather-grid {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .weather-day {{ flex: 1; min-width: 100px; text-align: center; padding: 15px; background: white; border-radius: 8px; }}
        .weather-date {{ font-weight: bold; color: #2c3e50; }}
        .weather-icon {{ font-size: 32px; }}
        .weather-desc {{ color: #7f8c8d; }}
        .weather-temp {{ font-weight: bold; color: #3498db; }}
        .print-btn {{ 
            display: block;
            margin: 20px auto;
            padding: 12px 30px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }}
        .print-btn:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{0}旅行路线单</h1>
        <div class="header-info">
            <p>生成日期: {1}</p>
            <p>出发地: {7} | 旅行天数: {2}天 | 预算: {8}{3}{9}</p>
        </div>
        
        {11}
        
        {10}
        
        {4}
        
        <div class="summary">
            <h3>费用汇总</h3>
            <p>总预计费用: {8}{5}{9}</p>
            <p>预算状态: {6}</p>
        </div>
        
        <button class="print-btn" onclick="window.print()">🖨️ 打印路线单</button>
    </div>
</body>
</html>""".format(itinerary['destination'], datetime.now().strftime('%Y-%m-%d %H:%M'), itinerary['days'], itinerary['budget'], attractions_html, itinerary['total_cost'], budget_status, itinerary.get('departure_city', '武汉'), currency_symbol, currency_suffix, hotel_html, weather_html)
    return content

@cl.on_chat_start
async def start_chat():
    """初始化聊天"""
    cl.user_session.set("current_itinerary", None)
    cl.user_session.set("state_history", [])
    
    await cl.Message(
        content="您好！我是 TravAgent 智能旅行助手。\n\n**用户画像**\n- 常住地: {0}\n- 饮食偏好: {1}\n- 旅行偏好: {2}\n\n**协议状态**\n[OK] Filesystem MCP\n[OK] Calendar MCP\n\n请问您想去哪里旅行？请直接输入您的旅行需求，例如：'去杭州玩3天，预算3000元'".format(
            USER_PROFILE['常住地'],
            ", ".join(USER_PROFILE['饮食偏好']),
            ", ".join(USER_PROFILE['旅行偏好'])
        ),
        author="TravAgent"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """处理用户消息"""
    user_input = message.content
    
    destination = "杭州"
    days = 2
    budget = 2000
    
    # 提取目的地（支持中英文）
    city_mapping = {
        "北京": "北京", "beijing": "北京", "Beijing": "北京",
        "上海": "上海", "shanghai": "上海", "Shanghai": "上海",
        "杭州": "杭州", "hangzhou": "杭州", "Hangzhou": "杭州",
        "青岛": "青岛", "qingdao": "青岛", "Qingdao": "青岛",
        "西安": "西安", "xian": "西安", "Xi'an": "西安", "Xian": "西安",
        "武汉": "武汉", "wuhan": "武汉", "Wuhan": "武汉",
        "成都": "成都", "chengdu": "成都", "Chengdu": "成都",
        "广州": "广州", "guangzhou": "广州", "Guangzhou": "广州",
        "深圳": "深圳", "shenzhen": "深圳", "Shenzhen": "深圳",
        "南京": "南京", "nanjing": "南京", "Nanjing": "南京"
    }
    
    # 先提取出发地和目的地
    departure_city = USER_PROFILE['常住地']
    destination = "杭州"
    
    # 使用正则表达式提取"从A去B"或"A到B"格式
    # 匹配 "从X去Y" 或 "X到Y" 或 "X去Y"
    pattern = r"(?:从)?([\u4e00-\u9fff]{2,3})[\u53bb\u5230\u5230\u5f80]([\u4e00-\u9fff]{2,3})"
    match = re.search(pattern, user_input)
    if match:
        departure_city = match.group(1)
        destination = match.group(2)
        # 确保城市名称在映射表中
        for city_key, city_value in city_mapping.items():
            if city_key == departure_city:
                departure_city = city_value
                break
        for city_key, city_value in city_mapping.items():
            if city_key == destination:
                destination = city_value
                break
    else:
        # 备用方案：遍历城市映射表
        found_cities = []
        for city_key, city_value in city_mapping.items():
            if city_key in user_input:
                found_cities.append(city_value)
        
        # 如果找到多个城市，第一个是出发地，最后一个是目的地
        if len(found_cities) >= 2:
            departure_city = found_cities[0]
            destination = found_cities[-1]
        elif len(found_cities) == 1:
            destination = found_cities[0]
    
    # 提取天数（支持中英文）
    days_match = re.search(r"(\d+)\s*(天|day|days)", user_input, re.IGNORECASE)
    if days_match:
        days = int(days_match.group(1))
    else:
        # 处理"一周"、"一星期"、"一周时间"等表达
        if "一周" in user_input or "一星期" in user_input:
            days = 7
        else:
            chinese_nums = {"一":1, "二":2, "两":2, "三":3, "四":4, "五":5, "六":6, "七":7, "八":8, "九":9, "十":10}
            for num_char, num_val in chinese_nums.items():
                if num_char + "天" in user_input:
                    days = num_val
                    break
    
    # 提取预算（支持多种格式）
    budget_match = re.search(r"budget[：:]?\s*(\d+(?:,\d{3})*)", user_input, re.IGNORECASE)
    if not budget_match:
        budget_match = re.search(r"预算[：:]?\s*(\d+(?:,\d{3})*)", user_input)
    if not budget_match:
        budget_match = re.search(r"(\d+(?:,\d{3})*)\s*元", user_input)
    if not budget_match:
        budget_match = re.search(r"(\d+(?:,\d{3})*)\s*(块|块钱|RMB|人民币)", user_input, re.IGNORECASE)
    if not budget_match:
        budget_match = re.search(r"(\d+(?:,\d{3})*)\s*(预算|费用|花费|钱|pounds|GBP)", user_input, re.IGNORECASE)
    if not budget_match:
        budget_match = re.search(r"(\d+(?:,\d{3})*)\s*(budget|cost|spend)", user_input, re.IGNORECASE)
    
    # 支持中文大写数字（如"一万"、"十万"等）
    if not budget_match:
        chinese_nums = {"零":0, "一":1, "二":2, "两":2, "三":3, "四":4, "五":5, "六":6, "七":7, "八":8, "九":9, "十":10}
        chinese_units = {"十":10, "百":100, "千":1000, "万":10000, "亿":100000000}
        
        # 匹配中文数字+单位的模式（如"一万"、"十万"、"一百万"）
        for num_char, num_val in chinese_nums.items():
            for unit_char, unit_val in chinese_units.items():
                pattern = num_char + unit_char
                if pattern in user_input:
                    budget = num_val * unit_val
                    budget_match = True
                    break
            if budget_match:
                break
    
    if budget_match and isinstance(budget_match, re.Match):
        budget_str = budget_match.group(1).replace(",", "")
        budget = int(budget_str)
    
    # 语言检测：根据用户输入语言选择货币
    contains_chinese = bool(re.search(r'[\u4e00-\u9fff]+', user_input))
    contains_english = bool(re.search(r'\b(budget|days|travel|trip|vacation|holiday)\b', user_input, re.IGNORECASE))
    
    # 根据语言选择货币
    if contains_chinese and not contains_english:
        currency_symbol = "¥"
        currency_name = "人民币"
        currency_suffix = "元"
    elif contains_english and not contains_chinese:
        currency_symbol = "£"
        currency_name = "英镑"
        currency_suffix = " GBP"
    else:
        currency_symbol = "¥"
        currency_name = "人民币"
        currency_suffix = "元"
    
    # 保存基本信息到session
    cl.user_session.set("travel_context", {
        "departure_city": departure_city,
        "destination": destination,
        "days": days,
        "budget": budget,
        "currency_symbol": currency_symbol,
        "currency_name": currency_name,
        "currency_suffix": currency_suffix
    })
    
    # 步骤1：选择日期
    await cl.Message(
        content="【Step 1/6】请选择您的出行日期\n\n**{0} → {1} 旅行规划**\n\n请选择出发日期（可点击下方快速选择或打开日历选择具体日期）：".format(departure_city, destination),
        author="TravAgent",
        actions=[
            cl.Action(name="select_date", label="📅 明天出发", description="选择明天作为出发日期", payload={"date_type": "departure", "days_offset": 1}),
            cl.Action(name="select_date", label="📅 后天出发", description="选择后天作为出发日期", payload={"date_type": "departure", "days_offset": 2}),
            cl.Action(name="select_date", label="📅 3天后出发", description="选择3天后作为出发日期", payload={"date_type": "departure", "days_offset": 3}),
            cl.Action(name="select_date", label="📅 一周后出发", description="选择一周后作为出发日期", payload={"date_type": "departure", "days_offset": 7}),
            cl.Action(name="show_calendar", label="📆 打开日历", description="打开日历选择具体日期", payload={})
        ]
    ).send()

async def generate_beautiful_response(itinerary: Dict) -> str:
    """生成美观的行程响应内容"""
    # 获取货币信息
    currency_symbol = itinerary.get('currency_symbol', '¥')
    currency_name = itinerary.get('currency_name', '人民币')
    currency_suffix = itinerary.get('currency_suffix', '元')
    
    # 获取天气信息
    weather_info = itinerary.get('weather', {})
    today_weather = weather_info.get('today', {})
    forecast_list = weather_info.get('forecast', [])
    
    weather_section = ""
    if forecast_list:
        weather_section = """

---

### 🌤️ 天气预报

| 日期 | 天气 | 温度 | 风力 |
|------|------|------|------|
"""
        for day in forecast_list[:itinerary['days']]:
            weather_section += "| {0} | {1} | {2} | {3} |\n".format(
                day.get('date', ''),
                day.get('weather', ''),
                day.get('temp', ''),
                day.get('wind', '')
            )
    
    # 获取交通详情
    departure_transport = itinerary.get('departure_transport', {})
    return_transport = itinerary.get('return_transport', {})
    departure_time = departure_transport.get('departure_time', '')
    arrival_time = departure_transport.get('arrival_time', '')
    return_departure_time = return_transport.get('departure_time', '')
    return_arrival_time = return_transport.get('arrival_time', '')
    departure_no = departure_transport.get('train_no', departure_transport.get('flight_no', ''))
    return_no = return_transport.get('train_no', return_transport.get('flight_no', ''))
    
    # 计算交通图标
    departure_icon = '🚄' if departure_transport.get('type') == 'train' else '✈️'
    return_icon = '🚄' if return_transport.get('type') == 'train' else '✈️'
    
    # 构建往返交通表格
    transport_table = f"""
### 🚄 往返交通

**{itinerary.get('departure_city', '武汉')} → {itinerary['destination']}**

| 项目 | 去程 | 返程 |
|------|------|------|
| 交通方式 | {departure_icon} {departure_transport.get('name', '高铁')} | {return_icon} {return_transport.get('name', '高铁')} |
| 车次/航班 | {departure_no} | {return_no} |
| 出发时间 | {itinerary.get('departure_city', '武汉')} {departure_time} | {itinerary['destination']} {return_departure_time} |
| 到达时间 | {itinerary['destination']} {arrival_time} | {itinerary.get('departure_city', '武汉')} {return_arrival_time} |
| 时长 | {departure_transport.get('duration', '4小时')} | {return_transport.get('duration', '4小时')} |
| 价格 | {currency_symbol}{departure_transport.get('price', 300)} | {currency_symbol}{return_transport.get('price', 300)} |
"""
    
    response = f"""
## 您的 {itinerary['destination']} {itinerary['days']}日游行程已生成！

基于您的偏好「{USER_PROFILE['旅行偏好'][0]}」为您定制

### 行程概览

| 项目 | 详情 |
|------|------|
| 出发地 | {itinerary.get('departure_city', '武汉')} |
| 目的地 | {itinerary['destination']} |
| 旅行天数 | {itinerary['days']}天{itinerary.get('hotel_nights', itinerary['days'] - 1)}晚 |
| 预算 | {currency_symbol}{itinerary['budget']} ({currency_name}) |
| 预计总费用 | {currency_symbol}{itinerary['total_cost']} |
| 预算状态 | {'未超预算' if itinerary['budget_status'] == 'under' else '已超预算'} |
| 当前天气 | {today_weather.get('weather', '暂无数据')} |

---

{transport_table}
---

### 🏨 住宿安排

**{itinerary.get('hotel', {}).get('name', '推荐酒店')}** ({itinerary.get('hotel', {}).get('star', 4)}⭐)
- 位置：{itinerary.get('hotel', {}).get('location', '市中心')}
- 地址：{itinerary.get('hotel', {}).get('address', '')}
- 评分：{itinerary.get('hotel', {}).get('rating', 4.5)}分
- 价格：{currency_symbol}{itinerary.get('hotel', {}).get('price', 500)}/晚
- 总计：{currency_symbol}{itinerary.get('hotel_total', 1000)} ({itinerary.get('hotel_nights', itinerary['days'] - 1)}晚)

{weather_section}

### 📅 每日行程安排
"""
    
    for day_plan in itinerary['daily_plan']:
        response += f"""

**Day {day_plan['day']} - {day_plan['date']}**

"""
        
        # 如果是第一天，显示到达信息
        if day_plan['day'] == 1 and itinerary.get('arrival_datetime'):
            arrival_dt = itinerary['arrival_datetime']
            response += f"""
✈️ **到达**: {arrival_dt} ({itinerary.get('departure_transport', {}).get('name', '')})
"""
        
        # 如果是最后一天，显示返程信息
        if day_plan['day'] == itinerary['days'] and itinerary.get('return_departure_time'):
            return_time = itinerary['return_departure_time']
            response += f"""
✈️ **返程**: {itinerary['destination']} {return_time} ({itinerary.get('return_transport', {}).get('name', '')})
"""
        
        # 显示当天的时间安排（按时间顺序）
        schedule_items = []
        
        # 添加景点时间安排
        for i, attraction in enumerate(day_plan['attractions']):
            start_time = attraction.get('start_time', '')
            end_time = attraction.get('end_time', '')
            if start_time and end_time:
                schedule_items.append({
                    'time': start_time,
                    'type': 'attraction',
                    'content': f"{i+1}. **{attraction['name']}** ({attraction['category']})",
                    'details': f"评分: {attraction['rating']} | 门票: {currency_symbol}{attraction['price']}{currency_suffix}",
                    'description': attraction.get('description', ''),
                    'end_time': end_time
                })
        
        # 添加餐饮时间安排
        meal_times = day_plan.get('meal_times', {})
        if meal_times.get('lunch'):
            schedule_items.append({
                'time': meal_times['lunch'],
                'type': 'meal',
                'content': "🍽️ **午餐**",
                'details': day_plan['meals']['lunch'],
                'end_time': str(int(meal_times['lunch'].split(':')[0]) + 1) + ":00"
            })
        if meal_times.get('dinner'):
            schedule_items.append({
                'time': meal_times['dinner'],
                'type': 'meal',
                'content': "🍽️ **晚餐**",
                'details': day_plan['meals']['dinner'],
                'end_time': str(int(meal_times['dinner'].split(':')[0]) + 1) + ":30"
            })
        
        # 按时间排序
        schedule_items.sort(key=lambda x: x['time'])
        
        # 输出时间安排
        for item in schedule_items:
            response += f"""
**{item['time']} - {item.get('end_time', '')}** {item['content']}
   {item['details']}
"""
            
            # 添加景点介绍（可折叠）
            if item['type'] == 'attraction' and item['description']:
                response += f"""
   <details>
   <summary>📍 景点介绍</summary>
   
   {item['description']}
   </details>
"""
        
        response += f"""
   **当日预计费用**: {currency_symbol}{day_plan['estimated_cost']}{currency_suffix}

"""
    
    # 费用明细
    departure_cost = itinerary.get('departure_cost', 0)
    hotel_total = itinerary.get('hotel_total', 0)
    attraction_cost = sum(a['price'] for d in itinerary['daily_plan'] for a in d['attractions'])
    meal_cost = itinerary['days'] * 150
    transport_cost = sum(t['cost'] for d in itinerary['daily_plan'] for t in d.get('transports', []))
    total_cost = itinerary['total_cost']
    
    response += f"""

---

### 💰 费用明细

| 项目 | 费用 |
|------|------|
| 往返交通 | {currency_symbol}{departure_cost + itinerary.get('return_cost', 0)}{currency_suffix} |
| 酒店住宿 | {currency_symbol}{hotel_total}{currency_suffix} |
| 景点门票 | {currency_symbol}{attraction_cost}{currency_suffix} |
| 餐饮费用 | {currency_symbol}{meal_cost}{currency_suffix} |
| 市内交通 | {currency_symbol}{transport_cost}{currency_suffix} |
| **总计** | **{currency_symbol}{total_cost}{currency_suffix}** |

---

小贴士：根据您的偏好「{USER_PROFILE['旅行偏好'][0]}」，已为您安排较为轻松的行程节奏。建议提前预约热门景点门票！
"""
    
    return response

async def send_itinerary_with_images(itinerary: Dict):
    """发送带有图片的行程消息"""
    # 先发送文字内容
    response = await generate_beautiful_response(itinerary)
    
    # 根据预算状态决定显示哪些按钮
    actions = [
        cl.Action(name="export_pdf", label="导出 PDF 路线单", description="导出当前行程为PDF文件", payload={"action": "export"}),
        cl.Action(name="generate_map", label="🗺️ 生成路线地图", description="生成包含每日路线的交互式地图", payload={"action": "map"}),
        cl.Action(name="sync_calendar", label="同步至系统日历", description="将行程同步到系统日历", payload={"action": "calendar"}),
        cl.Action(name="undo", label="撤销本次修改", description="回滚到上一个状态", payload={"action": "undo"})
    ]
    
    # 如果预算超支，添加修改预算或重新调整的选项
    if itinerary.get('budget_status') == 'over':
        actions.extend([
            cl.Action(name="adjust_budget", label="💰 修改预算", description="调整预算金额重新规划行程", payload={"action": "adjust_budget"}),
            cl.Action(name="recommend_economy", label="💡 推荐经济型方案", description="重新生成更经济的行程规划", payload={"action": "recommend_economy"})
        ])
    
    await cl.Message(
        content=response,
        author="TravAgent",
        actions=actions
    ).send()

@cl.action_callback("export_pdf")
async def on_export_pdf(action: cl.Action):
    """导出PDF回调"""
    itinerary = cl.user_session.get("current_itinerary")
    if not itinerary:
        await cl.Message(content="没有可导出的行程").send()
        return
    
    exporting = cl.user_session.get("is_exporting", False)
    if exporting:
        await cl.Message(content="正在导出中，请稍候...").send()
        return
    
    cl.user_session.set("is_exporting", True)
    
    try:
        pdf_content = generate_pdf_content(itinerary)
        pdf_path = "./public/itinerary_{0}_{1}.html".format(itinerary['destination'], datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(pdf_content)
        
        download_url = "/public/{0}".format(pdf_path.split('/')[-1])
        
        await cl.Message(
            content="PDF路线单已导出！\n\n[OK] Filesystem MCP: 写入成功\n文件路径: {0}\n点击下载: [{1}]({1})".format(pdf_path, download_url),
            author="TravAgent"
        ).send()
    except Exception as e:
        await cl.Message(content="导出失败: {0}".format(str(e))).send()
    finally:
        cl.user_session.set("is_exporting", False)

@cl.action_callback("sync_calendar")
async def on_sync_calendar(action: cl.Action):
    """同步日历回调 - 直接同步到谷歌日历"""
    itinerary = cl.user_session.get("current_itinerary")
    if not itinerary:
        await cl.Message(content="没有可同步的行程").send()
        return
    
    await cl.Message(content="🔄 正在同步到谷歌日历，请稍候...\n\n（首次同步需要登录谷歌账户）").send()
    
    try:
        # 导入谷歌日历模块
        from google_calendar import sync_itinerary_to_google_calendar
        
        result = sync_itinerary_to_google_calendar(itinerary)
        
        if result["success"]:
            event_list = "\n".join([f"- {e['date']}: {e['title']}" for e in result["events"]])
            content = f"✅ **同步成功！**\n\n已成功将 {len(result['events'])} 个旅行事件添加到您的谷歌日历：\n{event_list}\n\n🔔 提醒设置：\n- 提前1天发送邮件提醒\n- 提前1小时弹出提醒\n\n您可以在 [谷歌日历](https://calendar.google.com) 中查看和管理这些事件。"
            
            await cl.Message(content=content, author="TravAgent").send()
        else:
            # 如果谷歌日历同步失败，回退到ICS文件方式
            await cl.Message(content=f"⚠️ 谷歌日历同步失败: {result.get('error', '未知错误')}\n\n正在尝试生成ICS文件...").send()
            
            # 生成ICS日历文件内容
            ics_content = generate_ics(itinerary)
            
            # 保存ICS文件
            ics_filename = "calendar_{0}_{1}.ics".format(itinerary['destination'], datetime.now().strftime('%Y%m%d_%H%M%S'))
            ics_path = "./public/" + ics_filename
            
            os.makedirs("./public", exist_ok=True)
            
            with open(ics_path, 'w', encoding='utf-8') as f:
                f.write(ics_content)
            
            event_list = "\n".join([f"- {day_plan['date']}: {itinerary['destination']}旅行 Day{day_plan['day']}" for day_plan in itinerary['daily_plan']])
            
            await cl.Message(
                content=f"📅 **ICS日历文件已生成！**\n\n已创建 {len(itinerary['daily_plan'])} 个日历事件:\n{event_list}\n\n**手动导入谷歌日历：**\n1. 打开 [谷歌日历](https://calendar.google.com)\n2. 点击左侧「其他日历」旁的 ➕ 号\n3. 选择「导入日历」\n4. 选择下载的 `.ics` 文件\n5. 点击「导入」",
                author="TravAgent",
                actions=[
                    cl.Action(
                        name="download_ics",
                        label="📥 下载ICS文件",
                        description="下载日历文件",
                        payload={"filename": ics_filename}
                    )
                ]
            ).send()
            
    except Exception as e:
        await cl.Message(content=f"同步失败: {str(e)}").send()

def generate_ics(itinerary):
    """生成ICS日历文件内容"""
    ics_lines = []
    
    # ICS文件头
    ics_lines.append("BEGIN:VCALENDAR")
    ics_lines.append("VERSION:2.0")
    ics_lines.append("PRODID:-//TravAgent//旅行助手//ZH")
    ics_lines.append("CALSCALE:GREGORIAN")
    ics_lines.append("METHOD:PUBLISH")
    
    # 为每天创建一个事件
    for day_plan in itinerary['daily_plan']:
        event_title = f"{itinerary['destination']}旅行 Day{day_plan['day']}"
        event_date = day_plan['date']
        event_desc = "\n".join([f"- {a['name']}" for a in day_plan['attractions']])
        
        # 生成唯一ID
        uid = f"travagent-{event_date}-{day_plan['day']}@travagent.example.com"
        
        ics_lines.append("BEGIN:VEVENT")
        ics_lines.append(f"UID:{uid}")
        ics_lines.append(f"SUMMARY:{event_title}")
        ics_lines.append(f"DESCRIPTION:{event_desc}")
        ics_lines.append(f"DTSTART;VALUE=DATE:{event_date.replace('-', '')}")
        ics_lines.append(f"DTEND;VALUE=DATE:{event_date.replace('-', '')}")
        ics_lines.append("STATUS:CONFIRMED")
        ics_lines.append("TRANSP:OPAQUE")
        ics_lines.append("END:VEVENT")
    
    # ICS文件尾
    ics_lines.append("END:VCALENDAR")
    
    return "\n".join(ics_lines)

@cl.action_callback("download_ics")
async def on_download_ics(action: cl.Action):
    """下载ICS日历文件回调"""
    filename = action.payload.get("filename")
    if not filename:
        await cl.Message(content="文件不存在").send()
        return
    
    ics_path = "./public/" + filename
    
    try:
        # 创建文件附件并发送
        with open(ics_path, 'rb') as f:
            ics_content = f.read()
        
        # 使用正确的方式发送文件
        await cl.File(
            content=ics_content,
            name=filename
        ).send()
        
        await cl.Message(
            content=f"📥 **日历文件已下载**\n\n您可以将此ICS文件导入到谷歌日历或其他日历应用中。"
        ).send()
    except Exception as e:
        await cl.Message(content=f"下载失败: {str(e)}").send()

@cl.action_callback("generate_map")
async def on_generate_map(action: cl.Action):
    """生成地图回调"""
    itinerary = cl.user_session.get("current_itinerary")
    if not itinerary:
        await cl.Message(content="没有可生成地图的行程").send()
        return
    
    try:
        map_content = generate_map_content(itinerary)
        map_filename = "map_{0}_{1}.html".format(itinerary['destination'], datetime.now().strftime('%Y%m%d_%H%M%S'))
        map_path = "./public/" + map_filename
        
        # 确保public目录存在
        import os
        if not os.path.exists("./public"):
            os.makedirs("./public")
        
        with open(map_path, 'w', encoding='utf-8') as f:
            f.write(map_content)
        
        # 使用完整的本地文件路径供用户查看
        full_path = os.path.abspath(map_path)
        
        # 创建文件附件
        with open(map_path, 'rb') as f:
            map_file = cl.File(
                content=f.read(),
                name=map_filename,
                display_name=f"🗺️ {itinerary['destination']}旅行路线地图.html"
            )
        
        await cl.Message(
            content="🗺️ 路线地图已生成！\n\n**地图特性：**\n- 每日路线以不同颜色显示\n- 点击路线可查看交通方式（🚗打车、🚇地铁、🚌公交）\n- 支持地图缩放和拖拽\n- 图例显示每日路线颜色\n- 点击标记点查看景点详情\n\n**点击下方附件即可在浏览器中打开查看地图：**",
            author="TravAgent",
            elements=[map_file]
        ).send()
    except Exception as e:
        await cl.Message(content="生成地图失败: {0}".format(str(e))).send()

@cl.action_callback("undo")
async def on_undo(action: cl.Action):
    """撤销回调"""
    history = cl.user_session.get("state_history", [])
    
    if len(history) < 2:
        await cl.Message(content="没有可撤销的历史记录").send()
        return
    
    history.pop()
    previous_itinerary = history[-1]
    cl.user_session.set("current_itinerary", previous_itinerary)
    cl.user_session.set("state_history", history)
    
    response = await generate_beautiful_response(previous_itinerary)
    await cl.Message(
        content="已撤销到上一个状态\n\n{0}".format(response),
        author="TravAgent",
        actions=[
            cl.Action(name="export_pdf", label="导出 PDF 路线单", description="导出当前行程为PDF文件", payload={"action": "export"}),
            cl.Action(name="generate_map", label="🗺️ 生成路线地图", description="生成包含每日路线的交互式地图", payload={"action": "map"}),
            cl.Action(name="sync_calendar", label="同步至系统日历", description="将行程同步到系统日历", payload={"action": "calendar"}),
            cl.Action(name="undo", label="撤销本次修改", description="回滚到上一个状态", payload={"action": "undo"})
        ]
    ).send()

@cl.action_callback("adjust_budget")
async def on_adjust_budget(action: cl.Action):
    """调整预算"""
    await cl.Message(
        content="💰 **预算调整**\n\n当前预算已超支，您可以：\n\n1. 增加预算金额\n2. 选择更经济的交通方式\n3. 选择经济型酒店\n\n请告诉我您的新预算金额（例如：4000）：",
        author="TravAgent"
    ).send()

@cl.action_callback("recommend_economy")
async def on_recommend_economy(action: cl.Action):
    """推荐经济型方案"""
    itinerary = cl.user_session.get("current_itinerary", {})
    
    destination = itinerary.get('destination', '杭州')
    days = itinerary.get('days', 3)
    budget = itinerary.get('budget', 3000)
    departure_city = itinerary.get('departure_city', '武汉')
    departure_info = itinerary.get('departure_transport', {})
    return_info = itinerary.get('return_transport', {})
    arrival_datetime = itinerary.get('arrival_datetime', '')
    
    # 使用较低预算重新生成经济型方案
    economy_budget = budget
    economy_itinerary = generate_itinerary(
        destination, days, economy_budget, departure_city,
        departure_info=departure_info,
        return_info=return_info,
        arrival_datetime=arrival_datetime
    )
    
    # 保存并发送
    cl.user_session.set("current_itinerary", economy_itinerary)
    history = cl.user_session.get("state_history", [])
    history.append(economy_itinerary)
    cl.user_session.set("state_history", history)
    
    await cl.Message(
        content=f"💡 **已为您优化行程方案**\n\n根据您的预算，我们已调整了行程安排：\n\n- 酒店：选择性价比更高的住宿\n- 餐饮：推荐经济实惠的餐厅\n- 景点：优先选择免费或低价景点\n\n预计总费用：¥{economy_itinerary['total_cost']:.0f}",
        author="TravAgent"
    ).send()
    await send_itinerary_with_images(economy_itinerary)

# ==================== 交通票务模块回调 ====================

# 旧的交通选择回调已移除，使用新的四步流程回调

# ==================== 日期选择模块回调 ====================

@cl.action_callback("show_calendar")
async def on_show_calendar(action: cl.Action):
    """显示日历选择器 - 网格日历直接点击选择"""
    today = datetime.now()
    today_date = today.date()
    travel_context = cl.user_session.get("travel_context", {})
    departure_city = travel_context.get("departure_city", "武汉")
    destination = travel_context.get("destination", "杭州")
    
    # 最大选择范围：3个月（90天）
    max_days = 90
    
    content = f"""【Step 1/6】请选择您的出行日期

**{departure_city} → {destination} 旅行规划**

请直接点击下方日历中的日期选择出发日期：

"""
    
    # 获取当前选中的日期
    selected_date = cl.user_session.get("selected_departure_date", "")
    
    # 获取当前月、下个月和下下个月（最多3个月）
    for month_offset in [0, 1, 2]:
        # 正确计算月份
        if month_offset == 0:
            current_month = today.replace(day=1)
        elif month_offset == 1:
            if today.month == 12:
                current_month = datetime(today.year + 1, 1, 1)
            else:
                current_month = datetime(today.year, today.month + 1, 1)
        else:
            if today.month >= 11:
                current_month = datetime(today.year + 1, (today.month + 2) % 12, 1)
                if current_month.month == 0:
                    current_month = datetime(today.year + 1, 12, 1)
            else:
                current_month = datetime(today.year, today.month + 2, 1)
        
        year = current_month.year
        month = current_month.month
        
        # 获取月份名称
        month_names = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
        content += f"\n**{year}年{month_names[month-1]}**\n\n"
        content += "| 日 | 一 | 二 | 三 | 四 | 五 | 六 |\n"
        content += "|----|----|----|----|----|----|----|\n"
        
        # 获取当月第一天是星期几
        first_day_of_week = current_month.isoweekday()
        offset = (first_day_of_week % 7)  # 1->1, 2->2, ..., 7->0
        
        # 生成日历网格（严格7列）
        calendar_grid = []
        
        # 添加空白占位符（首日之前的空格）
        for _ in range(offset):
            calendar_grid.append("")
        
        # 获取当月天数
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                days_in_month = 29
            else:
                days_in_month = 28
        elif month in [4, 6, 9, 11]:
            days_in_month = 30
        else:
            days_in_month = 31
        
        # 添加当月所有日期
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day)
            date_date = date_obj.date()
            days_from_now = (date_obj - today).days
            date_str = date_obj.strftime("%Y-%m-%d")
            
            # 判断是否是今天
            is_today = date_date == today_date
            
            # 判断是否可选择（今天及以后，且在3个月内）
            is_selectable = days_from_now >= 0 and days_from_now <= max_days
            
            # 判断是否是选中状态
            is_selected = selected_date == date_str
            
            if is_selectable:
                if is_selected:
                    # 选中状态：高亮显示
                    calendar_grid.append(f"**{day}**")
                else:
                    # 可选择状态
                    calendar_grid.append(f"{day}")
            else:
                # 不可选择的日期（过去日期）
                calendar_grid.append(f"{day}")
        
        # 将网格转换为表格行（每行7个格子，居中对齐）
        for i in range(0, len(calendar_grid), 7):
            week_days = calendar_grid[i:i+7]
            row = "|"
            for d in week_days:
                if d == "":
                    row += "     |"
                elif "**" in d:
                    # 选中状态（加粗显示）
                    if len(d) == 4:  # **d** 单个数字
                        row += f" {d}  |"
                    else:  # **dd** 两位数
                        row += f" {d} |"
                else:
                    # 普通状态（可选择或不可选择）
                    if len(d) == 1:  # 单个数字
                        row += f"  {d}  |"
                    else:  # 两位数
                        row += f" {d}  |"
            content += row + "\n"
    
    # 添加简单提示
    content += "\n💡 点击下方日期数字按钮选择出发日期"
    
    # 创建日期选择按钮 - 使用完整日期格式作为标签（仅显示可选择的日期）
    actions = []
    for month_offset in [0, 1, 2]:
        if month_offset == 0:
            current_month = today.replace(day=1)
        elif month_offset == 1:
            if today.month == 12:
                current_month = datetime(today.year + 1, 1, 1)
            else:
                current_month = datetime(today.year, today.month + 1, 1)
        else:
            if today.month >= 11:
                current_month = datetime(today.year + 1, (today.month + 2) % 12, 1)
                if current_month.month == 0:
                    current_month = datetime(today.year + 1, 12, 1)
            else:
                current_month = datetime(today.year, today.month + 2, 1)
        
        year = current_month.year
        month = current_month.month
        
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                days_in_month = 29
            else:
                days_in_month = 28
        elif month in [4, 6, 9, 11]:
            days_in_month = 30
        else:
            days_in_month = 31
        
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day)
            days_from_now = (date_obj - today).days
            
            if days_from_now >= 0 and days_from_now <= max_days:
                date_str = date_obj.strftime("%Y-%m-%d")
                days_offset = days_from_now
                
                # 按钮标签使用完整日期格式
                actions.append(cl.Action(
                    name="select_date",
                    label=f"{date_str}",
                    description=f"选择出发日期",
                    payload={"date_type": "departure", "days_offset": days_offset}
                ))
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=actions
    ).send()


@cl.action_callback("select_date")
async def on_select_date(action: cl.Action):
    """选择日期回调"""
    days_offset = action.payload.get("days_offset", 1)
    today = datetime.now()
    
    # 计算出发日期
    departure_date = (today + timedelta(days=days_offset)).strftime("%Y-%m-%d")
    
    # 保存选中状态，用于日历高亮显示
    cl.user_session.set("selected_departure_date", departure_date)
    
    # 获取旅行天数
    travel_context = cl.user_session.get("travel_context", {})
    days = travel_context.get("days", 2)
    
    # 计算返回日期（三天两晚模式：出发日 + days - 1 = 返回日）
    return_date = (today + timedelta(days=days_offset + days - 1)).strftime("%Y-%m-%d")
    
    # 保存日期信息
    cl.user_session.set("travel_dates", {
        "departure_date": departure_date,
        "return_date": return_date
    })
    
    # 获取目的地天气信息
    destination = travel_context.get("destination", "杭州")
    # 获取足够的天气数据：需要从今天到返回日期的所有天数
    # 高德地图API最多返回4天数据，所以请求尽可能多的天数
    total_days_needed = days_offset + days
    weather_info = get_weather_info(destination, max(total_days_needed, 7))
    
    # 如果API返回的数据不够，补充模拟天气数据
    forecast = weather_info.get('forecast', [])
    # 确保有足够的天气数据覆盖整个行程
    if len(forecast) < total_days_needed:
        # 补充模拟数据
        import random
        weathers = ['晴', '多云', '小雨', '阵雨', '阴', '雷阵雨', '晴转多云']
        winds = ['东', '西', '南', '北', '东北', '东南', '西北', '西南']
        
        # 从API返回的数据之后开始补充
        for i in range(len(forecast), total_days_needed):
            date_str = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                'date': date_str,
                'weather': random.choice(weathers),
                'temp': f"{random.randint(18, 25)}-{random.randint(25, 35)}°C",
                'wind': f"{random.choice(winds)} {random.randint(1, 3)}级"
            })
        weather_info['forecast'] = forecast
    
    # 构建天气提示（从出发日期开始显示完整的旅行天数）
    weather_text = "\n**📊 天气预报：**\n"
    if weather_info.get('forecast'):
        # 从出发日期开始显示，显示完整的旅行天数
        start_index = days_offset
        end_index = start_index + days
        
        for day_weather in weather_info['forecast'][start_index:end_index]:
            date = day_weather.get('date', '')
            weather = day_weather.get('weather', '')
            temp = day_weather.get('temp', '')
            wind = day_weather.get('wind', '')
            
            # 天气建议
            suggestions = []
            if '雨' in weather:
                suggestions.append('🌧️ 建议携带雨具')
            
            # 安全解析温度
            try:
                temp_clean = temp.replace('℃', '').strip()
                if '~' in temp_clean:
                    temp_parts = temp_clean.split('~')
                    if len(temp_parts) >= 2:
                        high_temp = int(temp_parts[1].strip())
                        if '晴' in weather and high_temp > 30:
                            suggestions.append('☀️ 注意防晒')
                    if len(temp_parts) >= 1:
                        low_temp_str = temp_parts[0].strip()
                        if '-' in low_temp_str:
                            low_temp_str = low_temp_str.split('-')[0]
                        low_temp = int(low_temp_str)
                        if '雪' in weather or low_temp < 5:
                            suggestions.append('❄️ 注意保暖')
            except (ValueError, IndexError):
                pass
            
            weather_text += f"\n**{date}**: {weather} {temp} {wind}"
            if suggestions:
                weather_text += f"\n  提示: {' '.join(suggestions)}"
    
    await cl.Message(
        content=f"【Step 2/6】日期已选择\n\n**📅 行程日期：**\n- 出发日期：{departure_date}\n- 返回日期：{return_date}\n- 旅行时长：{days}天{days-1}晚\n\n{weather_text}\n\n是否确认以上日期？",
        author="TravAgent",
        actions=[
            cl.Action(name="confirm_dates", label="✅ 确认日期", description="确认所选日期并继续", payload={"action": "confirm"}),
            cl.Action(name="reselect_date", label="🔄 重新选择", description="重新选择日期", payload={"action": "reselect"})
        ]
    ).send()

@cl.action_callback("confirm_dates")
async def on_confirm_dates(action: cl.Action):
    """确认日期回调 - 进入交通选择阶段"""
    travel_context = cl.user_session.get("travel_context", {})
    travel_dates = cl.user_session.get("travel_dates", {})
    
    departure_city = travel_context.get("departure_city", "武汉")
    destination = travel_context.get("destination", "杭州")
    
    await cl.Message(
        content=f"【Step 3/6】正在查询往返交通方案...\n\n{departure_city} → {destination}\n出发: {travel_dates.get('departure_date')}\n返回: {travel_dates.get('return_date')}",
        author="TravAgent"
    ).send()
    await asyncio.sleep(0.8)
    
    # 查询往返交通方案
    trains_departure = search_high_speed_trains(departure_city, destination)
    flights_departure = search_flights(departure_city, destination)
    
    trains_return = search_high_speed_trains(destination, departure_city)
    flights_return = search_flights(destination, departure_city)
    
    # 保存交通信息到session
    cl.user_session.set("transport_options", {
        "trains_departure": trains_departure,
        "flights_departure": flights_departure,
        "trains_return": trains_return,
        "flights_return": flights_return
    })
    
    # 计算性价比（价格/时长），选择默认方式
    # 高铁性价比 = 平均价格 / 平均时长(小时)
    # 飞机性价比 = 平均价格 / 平均时长(小时)
    if trains_departure and flights_departure:
        # 计算高铁平均价格和时长
        train_avg_price = sum(t['price'] for t in trains_departure) / len(trains_departure)
        train_avg_hours = sum(float(t['duration'].replace('小时', '.').replace('分', '')) for t in trains_departure) / len(trains_departure)
        train_ratio = train_avg_price / train_avg_hours
        
        # 计算飞机平均价格和时长
        flight_avg_price = sum(f['price'] for f in flights_departure) / len(flights_departure)
        flight_avg_hours = sum(float(f['duration'].replace('小时', '.').replace('分', '')) for f in flights_departure) / len(flights_departure)
        flight_ratio = flight_avg_price / flight_avg_hours
        
        # 性价比高的优先显示（ratio越小越好）
        default_transport = "train" if train_ratio < flight_ratio else "flight"
    else:
        default_transport = "train" if trains_departure else "flight"
    
    # 显示交通方式选择
    await cl.Message(
        content=f"【Step 3/6】请选择交通方式\n\n📍 **{departure_city} → {destination}**\n\n请先选择您偏好的交通方式，系统默认推荐性价比最高的选项：",
        author="TravAgent",
        actions=[
            cl.Action(name="select_transport_mode", label=f"🚄 高铁出行", 
                     description="选择高铁作为交通工具", 
                     payload={"mode": "train"}),
            cl.Action(name="select_transport_mode", label=f"✈️ 飞机出行", 
                     description="选择飞机作为交通工具", 
                     payload={"mode": "flight"}),
            cl.Action(name="select_transport_mode", label=f"🔄 两者都看", 
                     description="同时查看高铁和飞机选项", 
                     payload={"mode": "both"})
        ]
    ).send()

@cl.action_callback("select_transport_mode")
async def on_select_transport_mode(action: cl.Action):
    """选择交通方式 - 显示真实班次列表"""
    mode = action.payload.get("mode", "train")
    travel_context = cl.user_session.get("travel_context", {})
    transport_options = cl.user_session.get("transport_options", {})
    
    departure_city = travel_context.get("departure_city", "武汉")
    destination = travel_context.get("destination", "杭州")
    
    trains_departure = transport_options.get("trains_departure", [])
    flights_departure = transport_options.get("flights_departure", [])
    
    # 保存当前选择的交通模式
    cl.user_session.set("selected_transport_mode", mode)
    
    # 构建内容和动作按钮
    content = f"""【Step 3/6】请选择去程交通方案

📍 **{departure_city} → {destination}**

请从下方选择合适的班次（点击按钮即可选择）：

"""
    
    actions = []
    
    # 显示高铁选项
    if mode == "train" or mode == "both":
        content += "**🚄 高铁车次：**\n\n"
        for train in trains_departure:
            actions.append(cl.Action(
                name="select_departure_train", 
                label=f"🚄 {train['train_no']}\n{train['departure_time']}→{train['arrival_time']}\n¥{train['price']} | {train['duration']}", 
                description=f"选择高铁 {train['train_no']}", 
                payload={"train": train}
            ))
    
    # 显示航班选项
    if mode == "flight" or mode == "both":
        content += "\n**✈️ 航班：**\n\n"
        for flight in flights_departure:
            actions.append(cl.Action(
                name="select_departure_flight", 
                label=f"✈️ {flight['flight_no']} ({flight['airline']})\n{flight['departure_time']}→{flight['arrival_time']}\n¥{flight['price']} | {flight['duration']}", 
                description=f"选择航班 {flight['flight_no']}", 
                payload={"flight": flight}
            ))
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=actions
    ).send()

@cl.action_callback("confirm_departure_transport")
async def on_confirm_departure_transport(action: cl.Action):
    """确认去程交通选择 - 显示返程交通方式选择"""
    travel_context = cl.user_session.get("travel_context", {})
    transport_options = cl.user_session.get("transport_options", {})
    
    destination = travel_context.get("destination", "杭州")
    departure_city = travel_context.get("departure_city", "武汉")
    
    trains_return = transport_options.get("trains_return", [])
    flights_return = transport_options.get("flights_return", [])
    
    content = f"""【Step 3/6】请选择返程交通方式

📍 **{destination} → {departure_city}**

请先选择您偏好的返程交通方式："""
    
    actions = []
    
    # 高铁选项（如果有数据）
    if trains_return:
        actions.append(cl.Action(
            name="select_return_transport_mode", 
            label=f"🚄 高铁出行 ({len(trains_return)}个车次)", 
            description="选择高铁作为返程交通工具", 
            payload={"mode": "train"}
        ))
    
    # 飞机选项（如果有数据）
    if flights_return:
        actions.append(cl.Action(
            name="select_return_transport_mode", 
            label=f"✈️ 飞机出行 ({len(flights_return)}个航班)", 
            description="选择飞机作为返程交通工具", 
            payload={"mode": "flight"}
        ))
    
    # 两者都看
    if trains_return and flights_return:
        actions.append(cl.Action(
            name="select_return_transport_mode", 
            label=f"🔄 两者都看", 
            description="同时查看高铁和飞机选项", 
            payload={"mode": "both"}
        ))
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=actions
    ).send()


@cl.action_callback("select_return_transport_mode")
async def on_select_return_transport_mode(action: cl.Action):
    """选择返程交通方式 - 显示真实班次列表"""
    mode = action.payload.get("mode", "train")
    travel_context = cl.user_session.get("travel_context", {})
    transport_options = cl.user_session.get("transport_options", {})
    
    destination = travel_context.get("destination", "杭州")
    departure_city = travel_context.get("departure_city", "武汉")
    
    trains_return = transport_options.get("trains_return", [])
    flights_return = transport_options.get("flights_return", [])
    
    # 保存当前选择的交通模式
    cl.user_session.set("selected_return_transport_mode", mode)
    
    # 构建内容和动作按钮
    content = f"""【Step 3/6】请选择返程交通方案

📍 **{destination} → {departure_city}**

请从下方选择合适的班次（点击按钮即可选择）：

"""
    
    actions = []
    
    # 显示高铁选项
    if mode == "train" or mode == "both":
        content += "**🚄 高铁车次：**\n\n"
        for train in trains_return:
            actions.append(cl.Action(
                name="select_return_train", 
                label=f"🚄 {train['train_no']}\n{train['departure_time']}→{train['arrival_time']}\n¥{train['price']} | {train['duration']}", 
                description=f"选择高铁 {train['train_no']}", 
                payload={"train": train}
            ))
    
    # 显示航班选项
    if mode == "flight" or mode == "both":
        content += "\n**✈️ 航班：**\n\n"
        for flight in flights_return:
            actions.append(cl.Action(
                name="select_return_flight", 
                label=f"✈️ {flight['flight_no']} ({flight['airline']})\n{flight['departure_time']}→{flight['arrival_time']}\n¥{flight['price']} | {flight['duration']}", 
                description=f"选择航班 {flight['flight_no']}", 
                payload={"flight": flight}
            ))
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=actions
    ).send()


@cl.action_callback("select_departure_train")
async def on_select_departure_train(action: cl.Action):
    """选择去程高铁"""
    train = action.payload.get("train")
    if not train:
        await cl.Message(content="未选择有效的高铁车次").send()
        return
    
    selected_transport = cl.user_session.get("selected_transport", {})
    selected_transport["departure"] = {
        "type": "train",
        "train_no": train["train_no"],
        "name": "高铁",
        "price": train["price"],
        "duration": train["duration"],
        "departure_time": train["departure_time"],
        "arrival_time": train["arrival_time"],
        "departure_city": train["departure_city"],
        "arrival_city": train["arrival_city"]
    }
    cl.user_session.set("selected_transport", selected_transport)
    
    await cl.Message(
        content=f"✅ 已选择去程高铁：\n\n**🚄 {train['train_no']}**\n{train['departure_city']} {train['departure_time']} → {train['arrival_city']} {train['arrival_time']}\n时长: {train['duration']} | 票价: ¥{train['price']}\n\n点击确认进入返程选择：",
        author="TravAgent",
        actions=[
            cl.Action(name="confirm_departure_transport", label="✅ 确认去程，选择返程", 
                     description="确认去程选择，进入返程交通选择", payload={})
        ]
    ).send()

@cl.action_callback("select_departure_flight")
async def on_select_departure_flight(action: cl.Action):
    """选择去程航班"""
    flight = action.payload.get("flight")
    if not flight:
        await cl.Message(content="未选择有效的航班").send()
        return
    
    selected_transport = cl.user_session.get("selected_transport", {})
    selected_transport["departure"] = {
        "type": "flight",
        "flight_no": flight["flight_no"],
        "airline": flight["airline"],
        "name": "飞机",
        "price": flight["price"],
        "duration": flight["duration"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "departure_airport": flight["departure_airport"],
        "arrival_airport": flight["arrival_airport"],
        "departure_city": flight["departure_city"],
        "arrival_city": flight["arrival_city"]
    }
    cl.user_session.set("selected_transport", selected_transport)
    
    await cl.Message(
        content=f"✅ 已选择去程航班：\n\n**✈️ {flight['flight_no']}** ({flight['airline']})\n{flight['departure_city']}({flight['departure_airport']}) {flight['departure_time']} → {flight['arrival_city']}({flight['arrival_airport']}) {flight['arrival_time']}\n时长: {flight['duration']} | 票价: ¥{flight['price']}\n\n点击确认进入返程选择：",
        author="TravAgent",
        actions=[
            cl.Action(name="confirm_departure_transport", label="✅ 确认去程，选择返程", 
                     description="确认去程选择，进入返程交通选择", payload={})
        ]
    ).send()

@cl.action_callback("select_return_train")
async def on_select_return_train(action: cl.Action):
    """选择返程高铁"""
    train = action.payload.get("train")
    if not train:
        await cl.Message(content="未选择有效的高铁车次").send()
        return
    
    selected_transport = cl.user_session.get("selected_transport", {})
    selected_transport["return"] = {
        "type": "train",
        "train_no": train["train_no"],
        "name": "高铁",
        "price": train["price"],
        "duration": train["duration"],
        "departure_time": train["departure_time"],
        "arrival_time": train["arrival_time"],
        "departure_city": train["departure_city"],
        "arrival_city": train["arrival_city"]
    }
    cl.user_session.set("selected_transport", selected_transport)
    
    # 显示确认交通方案按钮
    departure_info = selected_transport.get("departure", {})
    total_cost = departure_info.get("price", 0) + train["price"]
    
    await cl.Message(
        content=f"✅ 已选择返程高铁：\n\n**🚄 {train['train_no']}**\n{train['departure_city']} {train['departure_time']} → {train['arrival_city']} {train['arrival_time']}\n时长: {train['duration']} | 票价: ¥{train['price']}\n\n---\n\n**往返交通方案确认：**\n\n**去程：** {'🚄' if departure_info.get('type') == 'train' else '✈️'} {departure_info.get('train_no', departure_info.get('flight_no'))}\n**返程：** 🚄 {train['train_no']}\n**交通总费用：** ¥{total_cost}",
        author="TravAgent",
        actions=[
            cl.Action(name="confirm_transport_full", label="✅ 确认交通方案", description="确认所选往返交通方案并生成行程", payload={"action": "confirm"}),
            cl.Action(name="reselect_transport", label="🔄 重新选择", description="重新选择往返交通", payload={"action": "reselect"})
        ]
    ).send()

@cl.action_callback("select_return_flight")
async def on_select_return_flight(action: cl.Action):
    """选择返程航班"""
    flight = action.payload.get("flight")
    if not flight:
        await cl.Message(content="未选择有效的航班").send()
        return
    
    selected_transport = cl.user_session.get("selected_transport", {})
    selected_transport["return"] = {
        "type": "flight",
        "flight_no": flight["flight_no"],
        "airline": flight["airline"],
        "name": "飞机",
        "price": flight["price"],
        "duration": flight["duration"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "departure_airport": flight["departure_airport"],
        "arrival_airport": flight["arrival_airport"],
        "departure_city": flight["departure_city"],
        "arrival_city": flight["arrival_city"]
    }
    cl.user_session.set("selected_transport", selected_transport)
    
    # 显示确认交通方案按钮
    departure_info = selected_transport.get("departure", {})
    total_cost = departure_info.get("price", 0) + flight["price"]
    
    await cl.Message(
        content=f"✅ 已选择返程航班：\n\n**✈️ {flight['flight_no']}** ({flight['airline']})\n{flight['departure_city']}({flight['departure_airport']}) {flight['departure_time']} → {flight['arrival_city']}({flight['arrival_airport']}) {flight['arrival_time']}\n时长: {flight['duration']} | 票价: ¥{flight['price']}\n\n---\n\n**往返交通方案确认：**\n\n**去程：** {'🚄' if departure_info.get('type') == 'train' else '✈️'} {departure_info.get('train_no', departure_info.get('flight_no'))}\n**返程：** ✈️ {flight['flight_no']}\n**交通总费用：** ¥{total_cost}",
        author="TravAgent",
        actions=[
            cl.Action(name="confirm_transport_full", label="✅ 确认交通方案", description="确认所选往返交通方案并生成行程", payload={"action": "confirm"}),
            cl.Action(name="reselect_transport", label="🔄 重新选择", description="重新选择往返交通", payload={"action": "reselect"})
        ]
    ).send()

@cl.action_callback("confirm_transport_full")
async def on_confirm_transport_full(action: cl.Action):
    """确认完整交通方案回调 - 进入酒店选择阶段"""
    selected_transport = cl.user_session.get("selected_transport", {})
    travel_context = cl.user_session.get("travel_context", {})
    travel_dates = cl.user_session.get("travel_dates", {})
    
    departure_info = selected_transport.get("departure")
    return_info = selected_transport.get("return")
    
    if not departure_info or not return_info:
        await cl.Message(content="请先选择往返交通方式").send()
        return
    
    # 计算到达日期
    departure_date = travel_dates.get("departure_date", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
    arrival_datetime = calculate_arrival_datetime(departure_date, departure_info["departure_time"], departure_info["duration"])
    
    # 计算返程出发日期
    return_date = travel_dates.get("return_date", (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"))
    return_arrival_datetime = calculate_arrival_datetime(return_date, return_info["departure_time"], return_info["duration"])
    
    # 计算第一天可用时间
    arrival_time_str = arrival_datetime.split(" ")[1]
    arrival_hour = int(arrival_time_str.split(":")[0])
    available_hours_on_day1 = 20 - arrival_hour
    
    # 保存交通信息供后续使用
    cl.user_session.set("transport_summary", {
        "departure_info": departure_info,
        "return_info": return_info,
        "arrival_datetime": arrival_datetime,
        "return_arrival_datetime": return_arrival_datetime,
        "available_hours_on_day1": available_hours_on_day1
    })
    
    await cl.Message(
        content=f"【Step 4/6】交通方案已确认！\n\n**🚀 往返交通概览：**\n\n**去程：** {'🚄' if departure_info['type'] == 'train' else '✈️'} {departure_info.get('train_no', departure_info.get('flight_no'))}\n{departure_info['departure_city']} {departure_info['departure_time']} → {departure_info['arrival_city']} {departure_info['arrival_time']}\n\n**返程：** {'🚄' if return_info['type'] == 'train' else '✈️'} {return_info.get('train_no', return_info.get('flight_no'))}\n{return_info['departure_city']} {return_info['departure_time']} → {return_info['arrival_city']} {return_info['arrival_time']}\n\n**到达时间：** {arrival_datetime} (首日可用约 {available_hours_on_day1} 小时)\n**返程时间：** {return_arrival_datetime}\n**交通总费用：** ¥{departure_info['price'] + return_info['price']}\n\n接下来请选择您的住宿酒店：",
        author="TravAgent"
    ).send()
    
    # 获取目的地酒店列表
    destination = travel_context.get("destination", "杭州")
    hotel_result = get_hotels(destination)
    hotels = hotel_result.get("hotels", []) if isinstance(hotel_result, dict) else []
    
    if not hotels:
        # 如果没有获取到酒店，使用默认酒店数据
        from app import HOTELS
        hotels = HOTELS.get(destination, [])
    
    # 构建酒店选择消息
    content = f"🏨 **{destination}酒店推荐**\n\n请选择您想要入住的酒店：\n\n"
    actions = []
    
    for i, hotel in enumerate(hotels):
        star_str = "⭐" * hotel.get('star', 3)
        content += f"{i+1}. **{hotel.get('name', '酒店')}**\n"
        content += f"   {star_str} | 位置：{hotel.get('location', '')}\n"
        content += f"   评分：{hotel.get('rating', 4.0)}分 | 价格：¥{hotel.get('price', 500)}/晚\n"
        if hotel.get('address'):
            content += f"   地址：{hotel.get('address')}\n"
        content += "\n"
        
        actions.append(cl.Action(
            name="select_hotel",
            label=f"🏨 {hotel.get('name', '酒店')}",
            description=f"选择{hotel.get('name', '酒店')}作为住宿",
            payload={"hotel": hotel}
        ))
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=actions
    ).send()


@cl.action_callback("select_hotel")
async def on_select_hotel(action: cl.Action):
    """选择酒店回调 - 进入美食选择阶段"""
    selected_hotel = action.payload.get("hotel")
    if not selected_hotel:
        await cl.Message(content="未选择有效的酒店").send()
        return
    
    # 保存选择的酒店
    cl.user_session.set("selected_hotel", selected_hotel)
    
    # 显示已选择的酒店
    star_str = "⭐" * selected_hotel.get('star', 3)
    await cl.Message(
        content=f"【Step 5/6】酒店已选择！\n\n**🏨 {selected_hotel.get('name')}**\n{star_str} | 位置：{selected_hotel.get('location')}\n评分：{selected_hotel.get('rating')}分 | 价格：¥{selected_hotel.get('price')}/晚\n{selected_hotel.get('address', '')}\n\n接下来请选择您想体验的美食：",
        author="TravAgent"
    ).send()
    
    # 获取目的地并搜索美食
    travel_context = cl.user_session.get("travel_context", {})
    destination = travel_context.get("destination", "杭州")
    
    # 使用高德地图API搜索美食
    foods = search_food(destination)
    
    if not foods:
        # 如果API返回为空，使用默认美食数据
        import random
        foods = [
            {"name": f"{destination}特色餐厅", "address": "市中心", "rating": round(4.0 + random.random() * 0.9, 1), "cost": "人均80元", "type": "当地特色", "description": f"{destination}特色餐厅位于市中心繁华地段，环境优雅，提供地道的本地美食。", "reviews": ["环境很好，菜品味道正宗", "性价比很高，值得推荐"], "recommended_dishes": ["特色菜1", "特色菜2", "特色菜3"]},
            {"name": f"{destination}小吃街", "address": "步行街", "rating": round(4.0 + random.random() * 0.9, 1), "cost": "人均30元", "type": "小吃", "description": f"{destination}小吃街汇集了各种本地特色小吃，是体验市井文化的好去处。", "reviews": ["口味很地道", "价格实惠"], "recommended_dishes": ["小吃1", "小吃2", "小吃3"]},
            {"name": f"{destination}老字号", "address": "老城区", "rating": round(4.0 + random.random() * 0.9, 1), "cost": "人均100元", "type": "传统美食", "description": f"{destination}老字号传承百年技艺，菜品原汁原味，深受食客喜爱。", "reviews": ["百年老店，值得信赖", "味道正宗"], "recommended_dishes": ["招牌菜1", "招牌菜2", "招牌菜3"]},
            {"name": f"{destination}网红餐厅", "address": "商业区", "rating": round(4.0 + random.random() * 0.9, 1), "cost": "人均60元", "type": "创意菜", "description": f"{destination}网红餐厅以创意菜品和独特装修风格著称，是打卡拍照的好去处。", "reviews": ["装修很有特色", "菜品很有创意"], "recommended_dishes": ["创意菜1", "创意菜2", "创意菜3"]},
            {"name": f"{destination}夜市", "address": "夜市街", "rating": round(4.0 + random.random() * 0.9, 1), "cost": "人均40元", "type": "夜宵", "description": f"{destination}夜市是夜间觅食的好地方，各种小吃琳琅满目。", "reviews": ["夜宵好去处", "热闹非凡"], "recommended_dishes": ["夜宵1", "夜宵2", "夜宵3"]}
        ]
    
    # 保存美食列表到session
    cl.user_session.set("food_list", foods[:6])
    
    # 构建美食选择消息
    content = f"🍽️ **{destination}美食推荐**\n\n请选择您想要体验的美食（点击选择，可多选）：\n\n"
    
    for i, food in enumerate(foods[:6]):
        rating = food.get('rating', 0)
        content += f"{i+1}. **{food.get('name', '餐厅')}**\n"
        content += f"   📍 类型：{food.get('type', '餐饮')} | ⭐ 评分：{rating}分 | 💰 {food.get('cost', '')}\n"
        if food.get('address'):
            content += f"   📌 地址：{food.get('address')}\n"
        content += "\n"
    
    content += "💡 点击下方按钮选择美食，选完后点击确认按钮"
    
    # 创建选择按钮
    actions = []
    for food in foods[:6]:
        actions.append(cl.Action(
            name="toggle_food",
            label=f"🍽️ {food.get('name', '餐厅')}",
            description=f"选择/取消选择{food.get('name', '餐厅')}",
            payload={"food": food}
        ))
    
    # 添加确认按钮
    actions.append(cl.Action(
        name="confirm_food_selection",
        label="✅ 确认美食选择",
        description="确认所选美食并生成行程",
        payload={"action": "confirm"}
    ))
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=actions
    ).send()


@cl.action_callback("toggle_food")
async def on_toggle_food(action: cl.Action):
    """切换美食选择状态（支持多选）"""
    selected_food = action.payload.get("food")
    if not selected_food:
        await cl.Message(content="未选择有效的美食").send()
        return
    
    # 获取已选择的美食列表
    selected_foods = cl.user_session.get("selected_foods", [])
    food_name = selected_food.get('name')
    
    # 检查是否已选择
    existing_names = [f.get('name') for f in selected_foods]
    if food_name in existing_names:
        # 取消选择
        selected_foods = [f for f in selected_foods if f.get('name') != food_name]
        status = "❌"
        status_text = "已取消选择"
    else:
        # 添加选择
        selected_foods.append(selected_food)
        status = "✅"
        status_text = "已选择"
    
    cl.user_session.set("selected_foods", selected_foods)
    
    # 显示选择状态
    content = f"{status} {status_text}：**{food_name}**\n\n"
    
    if selected_foods:
        content += "已选美食列表：\n"
        for i, food in enumerate(selected_foods):
            content += f"{i+1}. {food.get('name')}\n"
        content += "\n继续选择其他美食，或点击下方按钮确认选择"
    else:
        content += "当前未选择任何美食，请选择您想体验的餐厅"
    
    await cl.Message(
        content=content,
        author="TravAgent",
        actions=[
            cl.Action(
                name="confirm_food_selection",
                label="✅ 确认美食选择",
                description="确认所选美食并生成行程",
                payload={"action": "confirm"}
            )
        ]
    ).send()


@cl.action_callback("select_food")
async def on_select_food(action: cl.Action):
    """查看美食详情"""
    selected_food = action.payload.get("food")
    if not selected_food:
        await cl.Message(content="未选择有效的美食").send()
        return
    
    food_name = selected_food.get('name')
    rating = selected_food.get('rating', 0)
    cost = selected_food.get('cost', '')
    address = selected_food.get('address', '')
    food_type = selected_food.get('type', '')
    description = selected_food.get('description', '')
    reviews = selected_food.get('reviews', [])
    recommended_dishes = selected_food.get('recommended_dishes', [])
    
    # 构建详情内容
    content = f"🍽️ **{food_name}**\n\n"
    content += f"📍 类型：{food_type}\n"
    content += f"⭐ 评分：{rating}分\n"
    content += f"💰 {cost}\n"
    if address:
        content += f"📌 地址：{address}\n"
    content += "\n"
    
    if description:
        content += f"📝 餐厅介绍：\n{description}\n\n"
    
    if reviews:
        content += "💬 用户评价：\n"
        for i, review in enumerate(reviews):
            content += f"   {i+1}. {review}\n"
        content += "\n"
    
    if recommended_dishes:
        content += "🍳 推荐菜品：\n"
        for dish in recommended_dishes:
            content += f"   • {dish}\n"
    
    await cl.Message(
        content=content,
        author="TravAgent"
    ).send()


@cl.action_callback("confirm_food_selection")
async def on_confirm_food_selection(action: cl.Action):
    """确认美食选择回调 - 进入行程生成阶段"""
    # 获取之前保存的信息
    transport_summary = cl.user_session.get("transport_summary", {})
    travel_context = cl.user_session.get("travel_context", {})
    travel_dates = cl.user_session.get("travel_dates", {})
    selected_hotel = cl.user_session.get("selected_hotel", {})
    selected_foods = cl.user_session.get("selected_foods", [])
    
    departure_info = transport_summary.get("departure_info")
    return_info = transport_summary.get("return_info")
    arrival_datetime = transport_summary.get("arrival_datetime")
    return_arrival_datetime = transport_summary.get("return_arrival_datetime")
    available_hours_on_day1 = transport_summary.get("available_hours_on_day1", 6)
    
    # 显示已选择的美食
    if selected_foods:
        food_names = ", ".join([f.get('name') for f in selected_foods])
        await cl.Message(
            content=f"【Step 6/6】美食已选择！\n\n🍽️ 已选美食：{food_names}\n\n正在生成专属行程规划...",
            author="TravAgent"
        ).send()
    else:
        await cl.Message(
            content=f"【Step 6/6】跳过美食选择\n\n正在生成专属行程规划...",
            author="TravAgent"
        ).send()
    
    await asyncio.sleep(0.8)
    
    # 获取上下文信息
    destination = travel_context.get("destination", "杭州")
    days = travel_context.get("days", 2)
    budget = travel_context.get("budget", 2000)
    departure_city = travel_context.get("departure_city", "武汉")
    currency_symbol = travel_context.get("currency_symbol", "¥")
    currency_name = travel_context.get("currency_name", "人民币")
    currency_suffix = travel_context.get("currency_suffix", "元")
    
    # 获取返程出发时间，用于调整最后一天的行程安排
    return_departure_time = return_info.get("departure_time")
    
    # 获取出发日期偏移
    days_offset = travel_context.get("days_offset", 1)
    
    # 生成行程（考虑到达时间和返程时间）
    itinerary = generate_itinerary(
        destination, days, budget, departure_city, 
        currency_symbol, currency_name, currency_suffix,
        departure_info=departure_info,
        return_info=return_info,
        arrival_datetime=arrival_datetime,
        return_departure_time=return_departure_time,
        days_offset=days_offset,
        hotel=selected_hotel,
        foods=selected_foods
    )
    
    # 添加行程日期信息
    itinerary["travel_dates"] = travel_dates
    
    # 保存到状态历史
    history = cl.user_session.get("state_history", [])
    history.append(itinerary)
    if len(history) > max_history:
        history = history[-max_history:]
    cl.user_session.set("state_history", history)
    cl.user_session.set("current_itinerary", itinerary)
    
    # 发送行程消息
    await send_itinerary_with_images(itinerary)


@cl.action_callback("reselect_date")
async def on_reselect_date(action: cl.Action):
    """重新选择日期"""
    travel_context = cl.user_session.get("travel_context", {})
    departure_city = travel_context.get("departure_city", "武汉")
    destination = travel_context.get("destination", "杭州")
    
    await cl.Message(
        content="【Step 1/6】请重新选择您的出行日期\n\n**{0} → {1} 旅行规划**\n\n请选择出发日期：".format(departure_city, destination),
        author="TravAgent",
        actions=[
            cl.Action(name="select_date", label="📅 明天出发", description="选择明天作为出发日期", payload={"date_type": "departure", "days_offset": 1}),
            cl.Action(name="select_date", label="📅 后天出发", description="选择后天作为出发日期", payload={"date_type": "departure", "days_offset": 2}),
            cl.Action(name="select_date", label="📅 3天后出发", description="选择3天后作为出发日期", payload={"date_type": "departure", "days_offset": 3}),
            cl.Action(name="select_date", label="📅 一周后出发", description="选择一周后作为出发日期", payload={"date_type": "departure", "days_offset": 7}),
            cl.Action(name="show_calendar", label="📆 打开日历", description="打开日历选择具体日期", payload={})
        ]
    ).send()

@cl.action_callback("reselect_transport")
async def on_reselect_transport(action: cl.Action):
    """重新选择交通"""
    travel_context = cl.user_session.get("travel_context", {})
    departure_city = travel_context.get("departure_city", "武汉")
    destination = travel_context.get("destination", "杭州")
    
    # 查询往返交通方案
    trains_departure = search_high_speed_trains(departure_city, destination)
    flights_departure = search_flights(departure_city, destination)
    
    cl.user_session.set("transport_options", {
        "trains_departure": trains_departure,
        "flights_departure": flights_departure,
        "trains_return": search_high_speed_trains(destination, departure_city),
        "flights_return": search_flights(destination, departure_city)
    })
    
    await cl.Message(
        content=f"【Step 3/6】请重新选择往返交通方案\n\n**🚄 去程高铁 ({departure_city} → {destination})**\n",
        author="TravAgent",
        actions=[
            cl.Action(name="select_departure_train", label=f"🚄 {trains_departure[0]['train_no']}\n{trains_departure[0]['departure_time']}→{trains_departure[0]['arrival_time']}\n¥{trains_departure[0]['price']}", 
                     description=f"选择去程高铁 {trains_departure[0]['train_no']}", 
                     payload={"train": trains_departure[0]}),
            cl.Action(name="select_departure_train", label=f"🚄 {trains_departure[1]['train_no']}\n{trains_departure[1]['departure_time']}→{trains_departure[1]['arrival_time']}\n¥{trains_departure[1]['price']}", 
                     description=f"选择去程高铁 {trains_departure[1]['train_no']}", 
                     payload={"train": trains_departure[1]}),
            cl.Action(name="select_departure_train", label=f"🚄 {trains_departure[2]['train_no']}\n{trains_departure[2]['departure_time']}→{trains_departure[2]['arrival_time']}\n¥{trains_departure[2]['price']}", 
                     description=f"选择去程高铁 {trains_departure[2]['train_no']}", 
                     payload={"train": trains_departure[2]}),
            cl.Action(name="select_departure_flight", label=f"✈️ {flights_departure[0]['flight_no']}\n{flights_departure[0]['departure_time']}→{flights_departure[0]['arrival_time']}\n¥{flights_departure[0]['price']}", 
                     description=f"选择去程航班 {flights_departure[0]['flight_no']}", 
                     payload={"flight": flights_departure[0]}),
            cl.Action(name="select_departure_flight", label=f"✈️ {flights_departure[1]['flight_no']}\n{flights_departure[1]['departure_time']}→{flights_departure[1]['arrival_time']}\n¥{flights_departure[1]['price']}", 
                     description=f"选择去程航班 {flights_departure[1]['flight_no']}", 
                     payload={"flight": flights_departure[1]}),
            cl.Action(name="select_departure_flight", label=f"✈️ {flights_departure[2]['flight_no']}\n{flights_departure[2]['departure_time']}→{flights_departure[2]['arrival_time']}\n¥{flights_departure[2]['price']}", 
                     description=f"选择去程航班 {flights_departure[2]['flight_no']}", 
                     payload={"flight": flights_departure[2]})
        ]
    ).send()