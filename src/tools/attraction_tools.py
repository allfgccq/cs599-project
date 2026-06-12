import requests
import os
from typing import List, Dict


def search_attractions(city: str, keywords: str = "", category: str = "all", page_size: int = 10) -> dict:
    """
    搜索目的地景点
    
    Args:
        city: 城市名称
        keywords: 搜索关键词
        category: 景点类型: all | natural | cultural | entertainment
        page_size: 返回数量
    
    Returns:
        景点列表
    """
    MOCK_ATTRACTIONS = {
        "杭州": [
            {"id": "1", "name": "西湖", "address": "杭州市西湖区", "category": "natural", "rating": 4.9, 
             "price": 0, "opening_hours": "全天开放", "description": "杭州最著名的自然景观", "image_url": "https://example.com/westlake.jpg"},
            {"id": "2", "name": "灵隐寺", "address": "杭州市西湖区灵隐路", "category": "cultural", "rating": 4.8, 
             "price": 75, "opening_hours": "7:30-17:30", "description": "江南著名古刹", "image_url": "https://example.com/lingyin.jpg"},
            {"id": "3", "name": "雷峰塔", "address": "杭州市西湖区南山路", "category": "cultural", "rating": 4.6, 
             "price": 40, "opening_hours": "8:00-17:30", "description": "白娘子传说发源地", "image_url": "https://example.com/leifeng.jpg"},
            {"id": "4", "name": "西溪湿地", "address": "杭州市西湖区天目山路", "category": "natural", "rating": 4.7, 
             "price": 80, "opening_hours": "7:30-18:30", "description": "国家湿地公园", "image_url": "https://example.com/xixi.jpg"},
            {"id": "5", "name": "宋城", "address": "杭州市西湖区之江路", "category": "entertainment", "rating": 4.5, 
             "price": 300, "opening_hours": "9:30-21:00", "description": "宋代主题文化乐园", "image_url": "https://example.com/songcheng.jpg"}
        ],
        "北京": [
            {"id": "1", "name": "故宫", "address": "北京市东城区景山前街", "category": "cultural", "rating": 4.9, 
             "price": 60, "opening_hours": "8:30-17:00", "description": "明清皇家宫殿", "image_url": "https://example.com/gugong.jpg"},
            {"id": "2", "name": "八达岭长城", "address": "北京市延庆区", "category": "cultural", "rating": 4.8, 
             "price": 45, "opening_hours": "7:30-18:00", "description": "万里长城精华段", "image_url": "https://example.com/greatwall.jpg"},
            {"id": "3", "name": "颐和园", "address": "北京市海淀区", "category": "cultural", "rating": 4.8, 
             "price": 30, "opening_hours": "6:30-18:00", "description": "皇家园林典范", "image_url": "https://example.com/summerpalace.jpg"},
            {"id": "4", "name": "天坛", "address": "北京市东城区天坛路", "category": "cultural", "rating": 4.7, 
             "price": 15, "opening_hours": "6:00-22:00", "description": "古代祭天场所", "image_url": "https://example.com/templeofheaven.jpg"},
            {"id": "5", "name": "鸟巢", "address": "北京市朝阳区", "category": "entertainment", "rating": 4.6, 
             "price": 50, "opening_hours": "9:00-18:00", "description": "北京奥运会主体育场", "image_url": "https://example.com/nest.jpg"}
        ],
        "上海": [
            {"id": "1", "name": "外滩", "address": "上海市黄浦区中山东一路", "category": "natural", "rating": 4.8, 
             "price": 0, "opening_hours": "全天开放", "description": "上海标志性景观", "image_url": "https://example.com/bund.jpg"},
            {"id": "2", "name": "东方明珠", "address": "上海市浦东新区世纪大道", "category": "entertainment", "rating": 4.6, 
             "price": 199, "opening_hours": "8:00-21:30", "description": "上海地标建筑", "image_url": "https://example.com/pearl.jpg"},
            {"id": "3", "name": "豫园", "address": "上海市黄浦区福佑路", "category": "cultural", "rating": 4.7, 
             "price": 40, "opening_hours": "8:30-17:30", "description": "江南古典园林", "image_url": "https://example.com/yuyuan.jpg"},
            {"id": "4", "name": "上海迪士尼", "address": "上海市浦东新区川沙镇", "category": "entertainment", "rating": 4.7, 
             "price": 599, "opening_hours": "9:00-21:00", "description": "迪士尼主题乐园", "image_url": "https://example.com/disney.jpg"},
            {"id": "5", "name": "南京路", "address": "上海市黄浦区", "category": "entertainment", "rating": 4.5, 
             "price": 0, "opening_hours": "全天开放", "description": "中华商业第一街", "image_url": "https://example.com/nanjingroad.jpg"}
        ]
    }
    
    try:
        attractions = MOCK_ATTRACTIONS.get(city, [])
        
        if keywords:
            attractions = [a for a in attractions if keywords in a["name"] or keywords in a["description"]]
        
        if category != "all":
            attractions = [a for a in attractions if a["category"] == category]
        
        attractions = attractions[:page_size]
        
        return {
            "success": True,
            "data": {
                "city": city,
                "attractions": attractions
            },
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "API_ERROR", "message": str(e), "details": ""}
        }