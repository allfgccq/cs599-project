from typing import Dict, Any


class BudgetAgent:
    """精算师 Agent - 专门算账，预算超支警告"""
    
    def __init__(self):
        self.daily_cost_estimates = {
            "budget": {
                "food": 50,
                "accommodation": 150,
                "transport": 30
            },
            "mid": {
                "food": 100,
                "accommodation": 300,
                "transport": 50
            },
            "luxury": {
                "food": 200,
                "accommodation": 600,
                "transport": 100
            }
        }
    
    def estimate_cost(self, itinerary: Dict, budget: float) -> Dict[str, Any]:
        """估算行程费用"""
        total_cost = 0.0
        breakdown = {
            "transport": 0,
            "accommodation": 0,
            "attractions": 0,
            "food": 0,
            "shopping": 0,
            "other": 0
        }
        
        if "days" in itinerary and isinstance(itinerary["days"], list):
            days = len(itinerary["days"])
            budget_level = self._determine_budget_level(budget, days)
            
            breakdown["food"] = self.daily_cost_estimates[budget_level]["food"] * days
            breakdown["accommodation"] = self.daily_cost_estimates[budget_level]["accommodation"] * days
            breakdown["transport"] = self.daily_cost_estimates[budget_level]["transport"] * days
        
        if "attractions" in itinerary:
            for day in itinerary["days"]:
                if "attractions" in day:
                    for attraction in day["attractions"]:
                        breakdown["attractions"] += attraction.get("price", 0)
        
        total_cost = sum(breakdown.values())
        
        return self._analyze_budget(total_cost, budget, breakdown)
    
    def _determine_budget_level(self, budget: float, days: int) -> str:
        """根据预算和天数确定预算级别"""
        daily_budget = budget / days
        
        if daily_budget < 300:
            return "budget"
        elif daily_budget < 600:
            return "mid"
        else:
            return "luxury"
    
    def _analyze_budget(self, total_cost: float, budget: float, breakdown: Dict) -> Dict[str, Any]:
        """分析预算状态"""
        if budget <= 0:
            return {
                "success": True,
                "data": {
                    "breakdown": breakdown,
                    "total_cost": total_cost,
                    "currency": "CNY",
                    "budget_status": "unknown",
                    "budget_ratio": 0,
                    "warning": ""
                },
                "error": None
            }
        
        ratio = total_cost / budget
        
        if ratio <= 1.0:
            status = "under"
            warning = ""
        elif ratio <= 1.15:
            status = "normal"
            warning = f"当前费用接近预算上限（超出 {(ratio - 1) * 100:.1f}%）"
        else:
            status = "over"
            warning = f"[警告] 当前方案已超出预算 {(ratio - 1) * 100:.1f}%，建议调整行程"
        
        return {
            "success": True,
            "data": {
                "breakdown": breakdown,
                "total_cost": total_cost,
                "currency": "CNY",
                "budget_status": status,
                "budget_ratio": ratio,
                "warning": warning
            },
            "error": None
        }
    
    def suggest_adjustment(self, itinerary: Dict, budget: float, savings_needed: float) -> Dict[str, Any]:
        """建议调整方案以节省费用"""
        suggestions = []
        
        if savings_needed > 0:
            suggestions.append(f"需要节省约 {savings_needed:.2f} 元")
            
            if "days" in itinerary:
                for day in itinerary["days"]:
                    if "attractions" in day:
                        expensive_attractions = [
                            a for a in day["attractions"] 
                            if a.get("price", 0) > 100
                        ]
                        if expensive_attractions:
                            suggestions.append(
                                f"考虑替换高价景点：{', '.join([a['name'] for a in expensive_attractions])}"
                            )
        
        return {
            "success": True,
            "data": {
                "suggestions": suggestions,
                "savings_needed": savings_needed
            },
            "error": None
        }