"""
调试美食推荐逻辑
"""

# 模拟用户选择的美食
selected_foods = [
    {"name": "杭州酒家(钱江新城市民中心店)", "address": "钱江新城", "rating": 4.8, "cost": "人均100元"}
]

# 预设的自动推荐餐厅列表
city_restaurants = {
    "杭州": ["楼外楼", "知味观", "绿茶餐厅", "外婆家", "弄堂里", "新白鹿", "杭帮菜博物馆餐厅"],
    "北京": ["四季民福", "大董", "东来顺", "护国寺小吃", "局气", "方砖厂69号炸酱面"],
    "上海": ["南翔馒头店", "老上海菜馆", "小杨生煎", "绿波廊", "上海1号"],
    "武汉": ["蔡林记", "户部巷小吃", "老通城", "四季美汤包", "精武鸭脖"]
}

destination = "杭州"
days = 3

# 获取用户选择的美食名称（去重）
food_names = []
seen_foods = set()
for f in selected_foods:
    name = f.get('name', '')
    if name and name not in seen_foods:
        food_names.append(name)
        seen_foods.add(name)

auto_restaurants = city_restaurants.get(destination, ["当地特色餐厅", "美食街小吃", "网红餐厅", "老字号餐馆"])

# 使用局部变量追踪已使用的餐厅
used_foods = []

print("=== 测试餐饮推荐逻辑 ===")
print(f"用户选择的餐厅: {food_names}")
print(f"自动推荐餐厅: {auto_restaurants}")
print()

for day in range(1, days + 1):
    print(f"--- Day {day} ---")
    
    # 午餐安排
    lunch_food = ""
    available_user_foods = [f for f in food_names if f not in used_foods]
    print(f"  午餐可用用户选择: {available_user_foods}")
    
    if available_user_foods:
        lunch_food = available_user_foods[0]
        used_foods.append(lunch_food)
        print(f"  午餐选择: {lunch_food} (用户选择)")
    else:
        available_restaurants = [r for r in auto_restaurants if r not in used_foods]
        print(f"  午餐可用自动推荐: {available_restaurants}")
        if available_restaurants:
            import random
            lunch_food = random.choice(available_restaurants)
            used_foods.append(lunch_food)
            print(f"  午餐选择: {lunch_food} (自动推荐)")
        else:
            lunch_food = f"{destination}附近餐厅"
            print(f"  午餐选择: {lunch_food} (默认)")
    
    # 晚餐安排
    dinner_food = ""
    available_user_foods = [f for f in food_names if f not in used_foods and f != lunch_food]
    print(f"  晚餐可用用户选择: {available_user_foods}")
    
    if available_user_foods:
        dinner_food = available_user_foods[0]
        used_foods.append(dinner_food)
        print(f"  晚餐选择: {dinner_food} (用户选择)")
    else:
        available_restaurants = [r for r in auto_restaurants if r not in used_foods and r != lunch_food]
        print(f"  晚餐可用自动推荐: {available_restaurants}")
        if available_restaurants:
            import random
            dinner_food = random.choice(available_restaurants)
            used_foods.append(dinner_food)
            print(f"  晚餐选择: {dinner_food} (自动推荐)")
        else:
            dinner_food = f"{destination}特色小吃"
            print(f"  晚餐选择: {dinner_food} (默认)")
    
    print(f"  已使用餐厅: {used_foods}")
    print()