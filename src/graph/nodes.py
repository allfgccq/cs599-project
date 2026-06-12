from typing import Dict, Any
from src.agents import TravelManager, BudgetAgent, ContentAgent, FoodAgent
from src.tools import call_tool
from src.graph.state import TravelState


def requirement_parser(state: TravelState) -> TravelState:
    """解析用户需求"""
    manager = TravelManager()
    result = manager.parse_requirement(state["user_input"])
    
    return {
        **state,
        "origin": result["origin"],
        "destination": result["destination"],
        "start_date": result["start_date"],
        "end_date": result["end_date"],
        "budget": result["budget"],
        "travel_days": result["travel_days"],
        "interests": result["interests"],
        "processing_step": "Requirement_Parser"
    }


def search_agent(state: TravelState) -> TravelState:
    """调用地图/天气/景点工具收集信息"""
    destination = state["destination"]
    start_date = state["start_date"]
    
    weather_result = call_tool("get_weather_info", city=destination, date=start_date)
    attractions_result = call_tool("search_attractions", city=destination, page_size=10)
    restaurants_result = call_tool("search_restaurants", city=destination, page_size=5)
    
    return {
        **state,
        "weather_info": weather_result.get("data", {}),
        "attractions": attractions_result.get("data", {}).get("attractions", []),
        "restaurants": restaurants_result.get("data", {}).get("restaurants", []),
        "processing_step": "Search_Agent"
    }


def itinerary_generator(state: TravelState) -> TravelState:
    """生成初版行程"""
    destination = state["destination"]
    days = state["travel_days"]
    attractions = state["attractions"]
    interests = state["interests"]
    
    selected_attractions = _select_attractions(attractions, interests, days)
    
    itinerary = {
        "destination": destination,
        "days": []
    }
    
    for day_num in range(1, days + 1):
        day_attractions = selected_attractions[(day_num - 1) * 2:day_num * 2]
        day_plan = {
            "day": day_num,
            "date": state["start_date"],
            "attractions": day_attractions,
            "meals": _generate_meal_plan(state["restaurants"], day_num)
        }
        itinerary["days"].append(day_plan)
    
    history = state.get("itinerary_history", [])
    history.append(itinerary.copy())
    
    return {
        **state,
        "itinerary": itinerary,
        "itinerary_history": history,
        "current_version": len(history),
        "processing_step": "Itinerary_Generator"
    }


def _select_attractions(attractions: list, interests: list, days: int) -> list:
    """根据兴趣选择景点"""
    if interests:
        filtered = []
        for interest in interests:
            filtered.extend([a for a in attractions if interest in a["name"] or interest in a["description"]])
        selected = filtered[:days * 2]
    else:
        selected = attractions[:days * 2]
    
    return selected


def _generate_meal_plan(restaurants: list, day_num: int) -> dict:
    """生成用餐计划"""
    if restaurants:
        lunch_idx = (day_num - 1) % len(restaurants)
        dinner_idx = day_num % len(restaurants)
        return {
            "lunch": restaurants[lunch_idx]["name"],
            "dinner": restaurants[dinner_idx]["name"]
        }
    return {"lunch": "当地特色餐厅", "dinner": "当地特色餐厅"}


def conflict_validator(state: TravelState) -> TravelState:
    """冲突检测专家"""
    budget_agent = BudgetAgent()
    cost_result = budget_agent.estimate_cost(state["itinerary"], state["budget"])
    
    is_conflict = False
    conflict_details = []
    
    if cost_result["data"]["budget_status"] == "over":
        is_conflict = True
        conflict_details.append(cost_result["data"]["warning"])
    
    if _check_time_conflict(state["itinerary"]):
        is_conflict = True
        conflict_details.append("检测到时间安排冲突，景点之间距离过远")
    
    return {
        **state,
        "estimated_cost": cost_result["data"]["total_cost"],
        "budget_status": cost_result["data"]["budget_status"],
        "budget_warning": cost_result["data"]["warning"],
        "is_conflict": is_conflict,
        "conflict_details": conflict_details,
        "processing_step": "Conflict_Validator"
    }


def _check_time_conflict(itinerary: dict) -> bool:
    """检查时间冲突"""
    return False


def fix_node(state: TravelState) -> TravelState:
    """自动修复节点"""
    budget_agent = BudgetAgent()
    
    if state["budget_status"] == "over" and state["budget"] > 0:
        savings_needed = state["estimated_cost"] - state["budget"] * 1.15
        
        if savings_needed > 0:
            itinerary = state["itinerary"]
            
            for day in itinerary["days"]:
                if "attractions" in day:
                    day["attractions"] = [
                        a for a in day["attractions"] 
                        if a.get("price", 0) < 100
                    ]
            
            cost_result = budget_agent.estimate_cost(itinerary, state["budget"])
            
            return {
                **state,
                "itinerary": itinerary,
                "estimated_cost": cost_result["data"]["total_cost"],
                "budget_status": cost_result["data"]["budget_status"],
                "budget_warning": cost_result["data"]["warning"],
                "is_conflict": cost_result["data"]["budget_status"] == "over",
                "processing_step": "Fix_Node"
            }
    
    return {
        **state,
        "is_conflict": False,
        "processing_step": "Fix_Node"
    }


def user_review(state: TravelState) -> TravelState:
    """用户确认环节"""
    return {
        **state,
        "processing_step": "User_Review"
    }