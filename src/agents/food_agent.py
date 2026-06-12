from typing import Dict, Any, List
from src.tools.restaurant_tools import search_restaurants


class FoodAgent:
    """美食助手 - 分享当地好吃的特色食物"""
    
    def __init__(self):
        self.local_specialties = {
            "杭州": [
                {"name": "西湖醋鱼", "description": "以鲜活草鱼为原料，色泽红亮，酸甜适口", "recommend_restaurant": "楼外楼"},
                {"name": "龙井虾仁", "description": "选用清明前后的龙井茶叶和新鲜河虾仁", "recommend_restaurant": "楼外楼"},
                {"name": "叫化鸡", "description": "用荷叶包裹泥土烤制，香气四溢", "recommend_restaurant": "楼外楼"},
                {"name": "猫耳朵", "description": "形似猫耳的面食，口感爽滑", "recommend_restaurant": "知味观"},
                {"name": "片儿川", "description": "杭州特色汤面，雪菜、笋片、瘦肉为浇头", "recommend_restaurant": "奎元馆"}
            ],
            "北京": [
                {"name": "北京烤鸭", "description": "外酥里嫩，搭配荷叶饼和甜面酱", "recommend_restaurant": "全聚德"},
                {"name": "涮羊肉", "description": "铜锅涮肉，肉质鲜嫩", "recommend_restaurant": "东来顺"},
                {"name": "炸酱面", "description": "手擀面配秘制炸酱", "recommend_restaurant": "海碗居"},
                {"name": "豆汁", "description": "绿豆发酵饮品，老北京特色", "recommend_restaurant": "护国寺小吃"},
                {"name": "卤煮火烧", "description": "猪肠、肺头、炸豆腐炖制", "recommend_restaurant": "北新桥卤煮"}
            ],
            "上海": [
                {"name": "小笼包", "description": "皮薄馅大，汤汁鲜美", "recommend_restaurant": "南翔馒头店"},
                {"name": "生煎包", "description": "底脆汁多，肉馅鲜嫩", "recommend_restaurant": "小杨生煎"},
                {"name": "响油鳝糊", "description": "鳝丝滑嫩，咸中带甜", "recommend_restaurant": "老上海菜馆"},
                {"name": "油爆虾", "description": "色泽红亮，外脆里嫩", "recommend_restaurant": "老上海菜馆"},
                {"name": "桂花拉糕", "description": "软糯香甜，桂花香浓", "recommend_restaurant": "绿波廊"}
            ]
        }
    
    def get_local_specialties(self, city: str) -> Dict[str, Any]:
        """获取当地特色美食"""
        specialties = self.local_specialties.get(city, [])
        
        return {
            "success": True,
            "data": {
                "city": city,
                "specialties": specialties
            },
            "error": None
        }
    
    def recommend_restaurants(self, city: str, preferences: List[str] = None) -> Dict[str, Any]:
        """推荐餐厅"""
        params = {
            "city": city,
            "keywords": "",
            "cuisine": "local",
            "price_range": "all",
            "page_size": 5
        }
        
        if preferences:
            for pref in preferences:
                if pref in ["便宜", "实惠", "经济"]:
                    params["price_range"] = "budget"
                elif pref in ["高档", "豪华", "精致"]:
                    params["price_range"] = "luxury"
        
        return search_restaurants(**params)
    
    def suggest_dining_plan(self, city: str, days: int) -> Dict[str, Any]:
        """建议用餐计划"""
        specialties = self.local_specialties.get(city, [])
        plan = []
        
        for day in range(1, days + 1):
            day_plan = {
                "day": day,
                "breakfast": self._get_breakfast_suggestion(city),
                "lunch": self._get_lunch_suggestion(city, day),
                "dinner": self._get_dinner_suggestion(city, day),
                "snacks": self._get_snacks_suggestion(city)
            }
            plan.append(day_plan)
        
        return {
            "success": True,
            "data": {
                "city": city,
                "plan": plan
            },
            "error": None
        }
    
    def _get_breakfast_suggestion(self, city: str) -> str:
        suggestions = {
            "杭州": "知味观 - 小笼包、豆浆油条",
            "北京": "护国寺小吃 - 豆汁焦圈、包子",
            "上海": "小杨生煎 - 生煎包、豆腐脑"
        }
        return suggestions.get(city, "当地特色早餐")
    
    def _get_lunch_suggestion(self, city: str, day: int) -> str:
        specialties = self.local_specialties.get(city, [])
        if day - 1 < len(specialties):
            return f"{specialties[day - 1]['recommend_restaurant']} - {specialties[day - 1]['name']}"
        return "当地特色餐厅"
    
    def _get_dinner_suggestion(self, city: str, day: int) -> str:
        suggestions = {
            "杭州": "绿茶餐厅 - 江浙融合菜",
            "北京": "四季民福 - 烤鸭",
            "上海": "上海本帮菜 - 红烧肉"
        }
        return suggestions.get(city, "当地特色晚餐")
    
    def _get_snacks_suggestion(self, city: str) -> str:
        suggestions = {
            "杭州": "桂花糕、西湖藕粉",
            "北京": "糖葫芦、驴打滚",
            "上海": "蟹壳黄、麻球"
        }
        return suggestions.get(city, "当地特色小吃")