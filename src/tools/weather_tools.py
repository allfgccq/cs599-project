import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

HEWEATHER_API_KEY = os.getenv("HEWEATHER_API_KEY", "demo")


def get_weather_info(city: str, days: int = 3) -> dict:
    """
    获取目的地多日天气信息
    
    Args:
        city: 城市名称
        days: 获取未来几天的天气（默认3天）
    
    Returns:
        天气信息字典，包含today和forecast列表
    """
    base_url = "https://devapi.qweather.com/v7/weather/3d"
    
    params = {
        "key": HEWEATHER_API_KEY,
        "location": city,
        "lang": "zh"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == "200":
            daily_forecast = data.get("daily", [])
            
            if daily_forecast:
                today = daily_forecast[0]
                forecast_list = []
                
                for i, day in enumerate(daily_forecast[:days]):
                    forecast_list.append({
                        "date": day.get("fxDate", ""),
                        "day_of_trip": i + 1,
                        "weather": day.get("textDay", ""),
                        "temp": f"{day.get('tempMin', '')}-{day.get('tempMax', '')}°C",
                        "wind": f"{day.get('windDirDay', '')} {day.get('windScaleDay', '')}级",
                        "humidity": int(day.get("humidity", 0)),
                        "tips": _get_weather_tips(day.get("textDay", ""), int(day.get("tempMax", 0)))
                    })
                
                return {
                    "success": True,
                    "today": {
                        "date": today.get("fxDate", ""),
                        "weather": today.get("textDay", ""),
                        "temp": f"{today.get('tempMin', '')}-{today.get('tempMax', '')}°C",
                        "wind": f"{today.get('windDirDay', '')} {today.get('windScaleDay', '')}级"
                    },
                    "forecast": forecast_list,
                    "error": None
                }
            
            return {
                "success": False,
                "today": {},
                "forecast": [],
                "error": {"code": "NOT_FOUND", "message": "未找到天气数据", "details": ""}
            }
        
        return {
            "success": False,
            "today": {},
            "forecast": [],
            "error": {"code": "API_ERROR", "message": data.get("msg", "获取天气信息失败"), "details": ""}
        }
    
    except Exception as e:
        return {
            "success": False,
            "today": {},
            "forecast": [],
            "error": {"code": "NETWORK_ERROR", "message": str(e), "details": ""}
        }


def _get_weather_tips(weather: str, temp: int) -> str:
    """根据天气情况生成出行建议"""
    tips = []
    
    if "雨" in weather:
        tips.append("记得带雨伞")
    if "雪" in weather:
        tips.append("注意保暖，小心路滑")
    if temp > 30:
        tips.append("天气炎热，做好防晒")
    if temp < 10:
        tips.append("天气寒冷，注意保暖")
    if "晴" in weather and temp >= 25:
        tips.append("阳光充足，建议戴墨镜")
    
    return "；".join(tips) if tips else "天气适宜出行"