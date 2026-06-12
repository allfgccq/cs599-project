#!/usr/bin/env python3
"""测试高德地图API密钥，查询"西湖断桥"的经纬度"""
import requests

# 高德地图API密钥
AMAP_KEY = "5873bb5e0bb65ad8f9fd76a3e715c256"

def get_geocode(address, city="杭州"):
    """
    使用高德地图地理编码API查询地址的经纬度
    :param address: 地址名称
    :param city: 城市名
    :return: 经纬度坐标 (latitude, longitude)
    """
    url = "https://restapi.amap.com/v3/geocode/geo"
    
    params = {
        "key": AMAP_KEY,
        "address": address,
        "city": city,
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 检查HTTP错误
        
        result = response.json()
        
        if result.get("status") == "1":
            geocodes = result.get("geocodes", [])
            if geocodes:
                location = geocodes[0].get("location", "")
                if location:
                    lng, lat = location.split(",")
                    return float(lat), float(lng), geocodes[0]
        
        return None, None, None
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None, None, None

def search_poi(keyword, city="杭州"):
    """
    使用高德地图POI搜索API查询地点
    :param keyword: 搜索关键词
    :param city: 城市名
    :return: POI列表
    """
    url = "https://restapi.amap.com/v3/place/text"
    
    params = {
        "key": AMAP_KEY,
        "keywords": keyword,
        "city": city,
        "output": "json",
        "offset": 10,
        "page": 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "1":
            return result.get("pois", [])
        
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []

if __name__ == "__main__":
    print("=== 测试高德地图API密钥 ===")
    print(f"API Key: {AMAP_KEY}")
    print()
    
    # 测试1：地理编码查询西湖断桥
    print("--- 测试1: 地理编码查询 ---")
    address = "西湖断桥"
    lat, lng, detail = get_geocode(address)
    
    if lat and lng:
        print(f"地址: {address}")
        print(f"纬度: {lat}")
        print(f"经度: {lng}")
        if detail:
            print(f"详细信息: {detail.get('formatted_address')}")
            print(f"行政区: {detail.get('province')} {detail.get('city')} {detail.get('district')}")
    else:
        print(f"查询失败，无法获取'{address}'的经纬度")
    
    print()
    
    # 测试2：POI搜索西湖断桥
    print("--- 测试2: POI搜索 ---")
    keyword = "西湖断桥"
    pois = search_poi(keyword)
    
    if pois:
        print(f"找到 {len(pois)} 个相关地点:")
        for i, poi in enumerate(pois[:5], 1):
            print(f"\n{i}. {poi.get('name')}")
            print(f"   地址: {poi.get('address')}")
            print(f"   坐标: {poi.get('location')}")
            print(f"   类型: {poi.get('type')}")
    else:
        print(f"未找到'{keyword}'相关地点")
    
    print()
    print("=== 测试完成 ===")
