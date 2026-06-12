from typing import Dict


def calculate_cost(
    transport_cost: float = 0,
    accommodation_cost: float = 0,
    attraction_cost: float = 0,
    food_cost: float = 0,
    shopping_cost: float = 0,
    other_cost: float = 0,
    budget: float = 0
) -> dict:
    """
    计算行程费用
    
    Args:
        transport_cost: 交通费用
        accommodation_cost: 住宿费用
        attraction_cost: 景点门票费用
        food_cost: 餐饮费用
        shopping_cost: 购物费用
        other_cost: 其他费用
        budget: 用户预算
    
    Returns:
        费用计算结果
    """
    try:
        total_cost = sum([
            transport_cost,
            accommodation_cost,
            attraction_cost,
            food_cost,
            shopping_cost,
            other_cost
        ])
        
        budget_ratio = total_cost / budget if budget > 0 else 0
        
        if budget > 0:
            if total_cost <= budget:
                budget_status = "under"
                warning = ""
            elif total_cost <= budget * 1.15:
                budget_status = "normal"
                warning = f"当前费用接近预算上限（超出 {((total_cost - budget) / budget * 100):.1f}%）"
            else:
                budget_status = "over"
                warning = f"⚠️ 当前方案已超出预算 {((total_cost - budget) / budget * 100):.1f}%，建议调整行程"
        else:
            budget_status = "unknown"
            warning = ""
        
        return {
            "success": True,
            "data": {
                "breakdown": {
                    "transport": transport_cost,
                    "accommodation": accommodation_cost,
                    "attractions": attraction_cost,
                    "food": food_cost,
                    "shopping": shopping_cost,
                    "other": other_cost
                },
                "total_cost": total_cost,
                "currency": "CNY",
                "budget_status": budget_status,
                "budget_ratio": budget_ratio,
                "warning": warning
            },
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "CALC_ERROR", "message": str(e), "details": ""}
        }