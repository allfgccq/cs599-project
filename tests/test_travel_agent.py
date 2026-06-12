import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.agents import TravelManager, BudgetAgent, ContentAgent, FoodAgent
from src.tools import call_tool


class TestTravelManager:
    """测试旅行总管"""
    
    def test_parse_requirement(self):
        manager = TravelManager()
        result = manager.parse_requirement("我想下周末去杭州玩两天，预算2000元")
        
        assert result["destination"] == "杭州"
        assert result["travel_days"] == 2
        assert result["budget"] == 2000.0
    
    def test_parse_requirement_with_origin(self):
        manager = TravelManager()
        result = manager.parse_requirement("从上海出发去北京玩三天，预算3000元")
        
        assert result["origin"] == "上海"
        assert result["destination"] == "北京"
        assert result["travel_days"] == 3
        assert result["budget"] == 3000.0


class TestBudgetAgent:
    """测试精算师Agent"""
    
    def test_estimate_cost(self):
        budget_agent = BudgetAgent()
        itinerary = {"days": 2}
        
        result = budget_agent.estimate_cost(itinerary, 2000)
        
        assert result["success"] is True
        assert "total_cost" in result["data"]
    
    def test_budget_warning(self):
        budget_agent = BudgetAgent()
        itinerary = {"days": 10}
        
        result = budget_agent.estimate_cost(itinerary, 500)
        
        assert result["data"]["budget_status"] == "over"
        assert "超出预算" in result["data"]["warning"]


class TestContentAgent:
    """测试特约导游Agent"""
    
    def test_generate_guide(self):
        content_agent = ContentAgent()
        result = content_agent.generate_guide("西湖")
        
        assert result["success"] is True
        assert "guide" in result["data"]
        assert "tips" in result["data"]


class TestFoodAgent:
    """测试美食助手"""
    
    def test_get_local_specialties(self):
        food_agent = FoodAgent()
        result = food_agent.get_local_specialties("杭州")
        
        assert result["success"] is True
        assert len(result["data"]["specialties"]) > 0


class TestTools:
    """测试工具函数"""
    
    def test_search_attractions(self):
        result = call_tool("search_attractions", city="杭州", page_size=5)
        
        assert result["success"] is True
        assert len(result["data"]["attractions"]) <= 5
    
    def test_search_restaurants(self):
        result = call_tool("search_restaurants", city="北京", page_size=3)
        
        assert result["success"] is True
        assert len(result["data"]["restaurants"]) <= 3
    
    def test_calculate_cost(self):
        result = call_tool(
            "calculate_cost",
            transport_cost=200,
            accommodation_cost=400,
            attraction_cost=100,
            food_cost=150,
            budget=1000
        )
        
        assert result["success"] is True
        assert result["data"]["total_cost"] == 850


if __name__ == "__main__":
    pytest.main([__file__, "-v"])