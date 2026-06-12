"""TravAgent 旅行助手 - 简化演示版"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents import TravelManager, BudgetAgent, ContentAgent, FoodAgent
from src.tools import call_tool


def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("          TravAgent - 智能旅行助手")
    print("=" * 60)
    print("欢迎使用 TravAgent！我可以帮您规划旅行行程。")
    print("请告诉我您的旅行需求，例如：")
    print('  "我想下周末去杭州玩两天，预算2000元"')
    print('  "从上海出发去北京玩三天，喜欢历史文化"')
    print("=" * 60)


def format_itinerary(itinerary: dict) -> str:
    """格式化行程输出"""
    output = f"\n[目的地]：{itinerary['destination']}\n"
    output += "-" * 50 + "\n"
    
    for day in itinerary["days"]:
        output += f"\n[第 {day['day']} 天]\n"
        output += "|- 景点安排：\n"
        
        for idx, attraction in enumerate(day["attractions"], 1):
            output += f"|  {idx}. {attraction['name']} - ￥{attraction['price']}\n"
            output += f"|    地址：{attraction['address']}\n"
            output += f"|    评分：{attraction['rating']}分\n"
        
        if "meals" in day:
            output += "|- 用餐建议：\n"
            output += f"|  午餐：{day['meals']['lunch']}\n"
            output += f"|  晚餐：{day['meals']['dinner']}\n"
        
        output += "|_ - - - - - - - - - - -\n"
    
    return output


def main():
    """主入口函数"""
    print_welcome()
    
    while True:
        user_input = input("\n请输入您的旅行需求（输入 'exit' 退出）：")
        
        if user_input.lower() == 'exit':
            print("感谢使用 TravAgent！祝您旅途愉快！")
            break
        
        if not user_input.strip():
            print("请输入有效的旅行需求")
            continue
        
        try:
            print("\n[分析] 正在分析您的需求...")
            
            manager = TravelManager()
            parsed = manager.parse_requirement(user_input)
            
            print(f"[OK] 出发地：{parsed['origin'] or '未指定'}")
            print(f"[OK] 目的地：{parsed['destination']}")
            print(f"[OK] 出发日期：{parsed['start_date']}")
            print(f"[OK] 返回日期：{parsed['end_date']}")
            print(f"[OK] 旅行天数：{parsed['travel_days']}天")
            print(f"[OK] 预算：￥{parsed['budget']}" if parsed['budget'] > 0 else "[OK] 预算：未指定")
            print(f"[OK] 兴趣偏好：{', '.join(parsed['interests']) if parsed['interests'] else '未指定'}")
            
            print("\n[搜索] 正在搜索景点...")
            attractions_result = call_tool("search_attractions", city=parsed["destination"], page_size=10)
            if attractions_result["success"]:
                attractions = attractions_result["data"]["attractions"]
                print(f"[OK] 找到 {len(attractions)} 个景点")
            
            print("\n[搜索] 正在搜索餐厅...")
            restaurants_result = call_tool("search_restaurants", city=parsed["destination"], page_size=5)
            if restaurants_result["success"]:
                restaurants = restaurants_result["data"]["restaurants"]
                print(f"[OK] 找到 {len(restaurants)} 家餐厅")
            
            print("\n[生成] 正在生成行程...")
            
            itinerary = {
                "destination": parsed["destination"],
                "days": []
            }
            
            selected_attractions = attractions[:parsed["travel_days"] * 2]
            
            for day_num in range(1, parsed["travel_days"] + 1):
                day_attractions = selected_attractions[(day_num - 1) * 2:day_num * 2]
                day_plan = {
                    "day": day_num,
                    "date": parsed["start_date"],
                    "attractions": day_attractions,
                    "meals": {
                        "lunch": restaurants[(day_num - 1) % len(restaurants)]["name"],
                        "dinner": restaurants[day_num % len(restaurants)]["name"]
                    }
                }
                itinerary["days"].append(day_plan)
            
            budget_agent = BudgetAgent()
            cost_result = budget_agent.estimate_cost(itinerary, parsed["budget"])
            
            print("\n" + "=" * 60)
            print("[行程] 您的旅行行程已生成！")
            print("=" * 60)
            
            print(format_itinerary(itinerary))
            
            print(f"[费用] 预计总费用：￥{cost_result['data']['total_cost']:.2f}")
            if cost_result['data']['warning']:
                print(f"[WARN] {cost_result['data']['warning']}")
            
            if parsed['interests']:
                content_agent = ContentAgent()
                print("\n[攻略] 景点深度攻略：")
                print("-" * 50)
                
                for day in itinerary["days"]:
                    for attraction in day["attractions"]:
                        guide = content_agent.generate_guide(attraction["name"])
                        if guide["success"]:
                            print(f"\n[景点] {attraction['name']}")
                            print(f"  攻略：{guide['data']['guide']}")
                            print(f"  小贴士：{'；'.join(guide['data']['tips'])}")
            
            food_agent = FoodAgent()
            specialties = food_agent.get_local_specialties(parsed["destination"])
            if specialties["success"]:
                print("\n[美食] 当地特色美食推荐：")
                print("-" * 50)
                for specialty in specialties["data"]["specialties"][:3]:
                    print(f"- {specialty['name']}：{specialty['description']}")
                    print(f"  推荐餐厅：{specialty['recommend_restaurant']}")
            
            print("\n" + "=" * 60)
            print("如需调整行程，请告诉我您的想法！")
            print("=" * 60)
        
        except Exception as e:
            print(f"[ERROR] 生成行程时发生错误：{str(e)}")


if __name__ == "__main__":
    main()