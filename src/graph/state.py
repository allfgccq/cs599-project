from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END


class TravelState(TypedDict):
    """旅行助手状态定义"""
    
    # 基础信息
    user_input: str
    session_id: str
    timestamp: float
    
    # 行程基础参数
    origin: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    travel_days: int
    
    # 偏好设置
    preferences: Dict[str, str]
    interests: List[str]
    avoid_places: List[str]
    dietary_restrictions: List[str]
    
    # 行程数据
    itinerary: Dict
    itinerary_history: List[Dict]
    current_version: int
    
    # 外部数据
    weather_info: Dict
    route_info: Dict
    attractions: List[Dict]
    restaurants: List[Dict]
    
    # 预算相关
    estimated_cost: float
    budget_status: str
    budget_warning: str
    
    # 状态标志
    is_conflict: bool
    conflict_details: List[str]
    processing_step: str
    agent_info: Dict[str, str]
    
    # 记忆相关
    short_term_memory: Dict
    long_term_memory: Dict


def create_travel_graph():
    """创建旅行助手状态机"""
    graph = StateGraph(TravelState)
    
    from src.graph.nodes import (
        requirement_parser,
        search_agent,
        itinerary_generator,
        conflict_validator,
        fix_node,
        user_review
    )
    
    graph.add_node("Requirement_Parser", requirement_parser)
    graph.add_node("Search_Agent", search_agent)
    graph.add_node("Itinerary_Generator", itinerary_generator)
    graph.add_node("Conflict_Validator", conflict_validator)
    graph.add_node("Fix_Node", fix_node)
    graph.add_node("User_Review", user_review)
    
    graph.set_entry_point("Requirement_Parser")
    
    graph.add_edge("Requirement_Parser", "Search_Agent")
    graph.add_edge("Search_Agent", "Itinerary_Generator")
    graph.add_edge("Itinerary_Generator", "Conflict_Validator")
    
    def route_decision(state: TravelState) -> str:
        if state.get("is_conflict", False):
            return "Fix_Node"
        return "User_Review"
    
    graph.add_conditional_edges(
        "Conflict_Validator",
        route_decision,
        {"Fix_Node": "Fix_Node", "User_Review": "User_Review"}
    )
    
    graph.add_edge("Fix_Node", "Conflict_Validator")
    graph.add_edge("User_Review", END)
    
    return graph