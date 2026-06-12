import requests
import os
from typing import List, Dict


def search_restaurants(city: str, keywords: str = "", cuisine: str = "all", price_range: str = "all", page_size: int = 10) -> dict:
    """
    搜索当地美食餐厅
    
    Args:
        city: 城市名称
        keywords: 搜索关键词
        cuisine: 菜系: all | local | chinese | western
        price_range: 价格区间: all | budget | mid | luxury
        page_size: 返回数量
    
    Returns:
        餐厅列表
    """
    MOCK_RESTAURANTS = {
        "杭州": [
            {"id": "1", "name": "楼外楼", "address": "杭州市西湖区孤山路", "cuisine": "local", "rating": 4.7, 
             "price_per_person": 200, "opening_hours": "11:00-14:30, 17:00-21:00", 
             "recommendations": "西湖醋鱼、龙井虾仁、叫化鸡", "image_url": "https://example.com/louwaitai.jpg"},
            {"id": "2", "name": "知味观", "address": "杭州市上城区仁和路", "cuisine": "local", "rating": 4.5, 
             "price_per_person": 60, "opening_hours": "7:00-21:00", 
             "recommendations": "小笼包、猫耳朵、桂花糖藕", "image_url": "https://example.com/zhiweiguan.jpg"},
            {"id": "3", "name": "奎元馆", "address": "杭州市上城区解放路", "cuisine": "local", "rating": 4.4, 
             "price_per_person": 40, "opening_hours": "8:00-21:00", 
             "recommendations": "虾爆鳝面、片儿川", "image_url": "https://example.com/kuiyuanguan.jpg"},
            {"id": "4", "name": "绿茶餐厅", "address": "杭州市西湖区龙井路", "cuisine": "chinese", "rating": 4.6, 
             "price_per_person": 80, "opening_hours": "10:00-22:00", 
             "recommendations": "面包诱惑、绿茶烤肉", "image_url": "https://example.com/greentea.jpg"},
            {"id": "5", "name": "外婆家", "address": "杭州市西湖区文三路", "cuisine": "chinese", "rating": 4.5, 
             "price_per_person": 70, "opening_hours": "11:00-14:30, 17:00-21:00", 
             "recommendations": "茶香鸡、青豆泥", "image_url": "https://example.com/waipojia.jpg"}
        ],
        "北京": [
            {"id": "1", "name": "四季民福", "address": "北京市东城区王府井", "cuisine": "local", "rating": 4.8, 
             "price_per_person": 150, "opening_hours": "11:00-22:00", 
             "recommendations": "烤鸭、贝勒烤肉", "image_url": "https://example.com/sijiminfu.jpg"},
            {"id": "2", "name": "全聚德", "address": "北京市西城区前门", "cuisine": "local", "rating": 4.6, 
             "price_per_person": 200, "opening_hours": "11:00-21:00", 
             "recommendations": "北京烤鸭", "image_url": "https://example.com/quanjude.jpg"},
            {"id": "3", "name": "东来顺", "address": "北京市东城区王府井", "cuisine": "local", "rating": 4.6, 
             "price_per_person": 120, "opening_hours": "11:00-22:00", 
             "recommendations": "涮羊肉", "image_url": "https://example.com/donglaishun.jpg"},
            {"id": "4", "name": "大董", "address": "北京市朝阳区团结湖", "cuisine": "chinese", "rating": 4.7, 
             "price_per_person": 250, "opening_hours": "11:00-22:00", 
             "recommendations": "酥不腻烤鸭", "image_url": "https://example.com/dadong.jpg"},
            {"id": "5", "name": "护国寺小吃", "address": "北京市西城区护国寺街", "cuisine": "local", "rating": 4.4, 
             "price_per_person": 30, "opening_hours": "6:00-21:00", 
             "recommendations": "豆汁、焦圈、艾窝窝", "image_url": "https://example.com/huguosi.jpg"}
        ],
        "上海": [
            {"id": "1", "name": "南翔馒头店", "address": "上海市黄浦区豫园", "cuisine": "local", "rating": 4.5, 
             "price_per_person": 50, "opening_hours": "7:00-21:00", 
             "recommendations": "小笼包", "image_url": "https://example.com/nanxiang.jpg"},
            {"id": "2", "name": "老上海菜馆", "address": "上海市黄浦区南京东路", "cuisine": "local", "rating": 4.6, 
             "price_per_person": 100, "opening_hours": "11:00-22:00", 
             "recommendations": "响油鳝糊、油爆虾", "image_url": "https://example.com/laoshanghai.jpg"},
            {"id": "3", "name": "小杨生煎", "address": "上海市静安区南京西路", "cuisine": "local", "rating": 4.4, 
             "price_per_person": 30, "opening_hours": "6:00-22:00", 
             "recommendations": "生煎包", "image_url": "https://example.com/xiaoyang.jpg"},
            {"id": "4", "name": "上海本帮菜", "address": "上海市徐汇区衡山路", "cuisine": "local", "rating": 4.5, 
             "price_per_person": 120, "opening_hours": "11:00-22:00", 
             "recommendations": "红烧肉、糟溜鱼片", "image_url": "https://example.com/benbangcai.jpg"},
            {"id": "5", "name": "绿波廊", "address": "上海市黄浦区豫园路", "cuisine": "local", "rating": 4.6, 
             "price_per_person": 150, "opening_hours": "11:00-21:00", 
             "recommendations": "蟹粉小笼、桂花拉糕", "image_url": "https://example.com/lvbolang.jpg"}
        ]
    }
    
    try:
        restaurants = MOCK_RESTAURANTS.get(city, [])
        
        if keywords:
            restaurants = [r for r in restaurants if keywords in r["name"] or keywords in r["recommendations"]]
        
        if cuisine != "all":
            restaurants = [r for r in restaurants if r["cuisine"] == cuisine]
        
        if price_range != "all":
            price_mapping = {
                "budget": (0, 50),
                "mid": (50, 150),
                "luxury": (150, float('inf'))
            }
            min_price, max_price = price_mapping.get(price_range, (0, float('inf')))
            restaurants = [r for r in restaurants if min_price <= r["price_per_person"] < max_price]
        
        restaurants = restaurants[:page_size]
        
        return {
            "success": True,
            "data": {
                "city": city,
                "restaurants": restaurants
            },
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "API_ERROR", "message": str(e), "details": ""}
        }