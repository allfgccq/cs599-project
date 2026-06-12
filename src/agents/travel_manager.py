from typing import Dict, Any
import re
from datetime import datetime, timedelta


class TravelManager:
    """旅行总管 - 负责和用户对话，理解意图，拆解任务"""
    
    def __init__(self):
        self.extraction_patterns = {
            "destination": [
                r"去(.+?)玩",
                r"到(.+?)旅游",
                r"前往(.+?)",
                r"目的地(.+?)"
            ],
            "origin": [
                r"从(.+?)出发",
                r"从(.+?)去"
            ],
            "budget": [
                r"预算(\d+(?:\.\d+)?)元",
                r"预算(\d+(?:\.\d+)?)",
                r"(\d+(?:\.\d+)?)元预算"
            ],
            "days": [
                r"(\d+)天",
                r"(\d+)日"
            ],
            "date": [
                r"(\d{4}-\d{2}-\d{2})",
                r"下周末",
                r"本周",
                r"明天",
                r"后天"
            ],
            "interests": [
                r"喜欢(.+?)(?:，|。|$)",
                r"偏好(.+?)(?:，|。|$)"
            ]
        }
    
    def parse_requirement(self, user_input: str) -> Dict[str, Any]:
        """解析用户需求，提取关键参数"""
        result = {
            "origin": "",
            "destination": "",
            "start_date": "",
            "end_date": "",
            "budget": 0.0,
            "travel_days": 3,
            "interests": [],
            "preferences": {}
        }
        
        for key, patterns in self.extraction_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input)
                if match:
                    if match.groups():
                        value = match.group(1).strip()
                    else:
                        value = match.group(0).strip()
                    
                    if key == "budget":
                        result["budget"] = float(value)
                    elif key == "days":
                        result["travel_days"] = int(value)
                    elif key == "date":
                        result["start_date"] = self._parse_date(value)
                        if result["start_date"] and result["travel_days"]:
                            start = datetime.strptime(result["start_date"], "%Y-%m-%d")
                            end = start + timedelta(days=result["travel_days"])
                            result["end_date"] = end.strftime("%Y-%m-%d")
                    elif key == "interests":
                        result["interests"] = [item.strip() for item in value.split("、")]
                    else:
                        result[key] = value
                    break
        
        if not result["start_date"]:
            result["start_date"] = datetime.now().strftime("%Y-%m-%d")
        
        return result
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        today = datetime.now()
        
        if date_str == "明天":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str == "后天":
            return (today + timedelta(days=2)).strftime("%Y-%m-%d")
        elif date_str == "本周":
            return today.strftime("%Y-%m-%d")
        elif date_str == "下周末":
            days_ahead = 5 - today.weekday() if today.weekday() <= 4 else 12 - today.weekday()
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif re.match(r"\d{4}-\d{2}-\d{2}", date_str):
            return date_str
        
        return ""
    
    def chat(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """处理用户对话"""
        parsed = self.parse_requirement(user_input)
        
        return {
            "status": "success",
            "parsed_requirement": parsed,
            "message": "需求解析完成，正在为您规划行程..."
        }