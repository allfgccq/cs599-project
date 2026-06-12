import sys
sys.path.insert(0, 'd:\\trae\\TravAgent')

from app import generate_itinerary

# 测试数据
destination = "杭州"
days = 2
budget = 2000
departure_city = "武汉"

# 用户选择的餐厅
selected_foods = [
    {"name": "牛New寿喜烧(来福士店)", "address": "来福士广场", "rating": 4.8, "cost": "人均100元"}
]

# 生成行程
itinerary = generate_itinerary(
    destination=destination,
    days=days,
    budget=budget,
    departure_city=departure_city,
    foods=selected_foods
)

# 打印行程中的餐饮安排
print("=== 行程餐饮安排 ===")
for day, day_plan in itinerary['days'].items():
    print(f"\nDay {day}:")
    meals = day_plan.get('meals', {})
    meal_times = day_plan.get('meal_times', {})
    
    if meal_times.get('lunch'):
        print(f"  午餐 ({meal_times['lunch']}): {meals.get('lunch', '')}")
    if meal_times.get('dinner'):
        print(f"  晚餐 ({meal_times['dinner']}): {meals.get('dinner', '')}")

# 检查重复
print("\n=== 检查重复 ===")
all_meals = []
for day, day_plan in itinerary['days'].items():
    meals = day_plan.get('meals', {})
    if meals.get('lunch'):
        all_meals.append(('Day'+str(day), '午餐', meals['lunch']))
    if meals.get('dinner'):
        all_meals.append(('Day'+str(day), '晚餐', meals['dinner']))

meal_counts = {}
for day, meal_type, meal_name in all_meals:
    if meal_name not in meal_counts:
        meal_counts[meal_name] = []
    meal_counts[meal_name].append(f"{day} {meal_type}")

for meal_name, occurrences in meal_counts.items():
    if len(occurrences) > 1:
        print(f"❌ 重复: {meal_name} 出现在 {', '.join(occurrences)}")
    else:
        print(f"✅ 唯一: {meal_name} 只出现在 {', '.join(occurrences)}")
