#!/usr/bin/env python3
"""测试出发地显示和地图功能修复"""
import sys
sys.path.insert(0, 'd:\\trae\\TravAgent')

from app import generate_itinerary, USER_PROFILE

# 测试1：生成行程
print('=== 测试1: 行程数据 ===')
itinerary = generate_itinerary(
    destination='杭州',
    days=3,
    budget=3000,
    departure_city='北京',
    currency_symbol='¥',
    currency_name='人民币',
    currency_suffix='元'
)

print('出发地:', itinerary.get('departure_city'))
print('目的地:', itinerary.get('destination'))
print('总费用:', itinerary.get('total_cost'))
print('预算状态:', itinerary.get('budget_status'))
print('用户偏好:', USER_PROFILE)

# 测试2：验证format字符串索引
print()
print('=== 测试2: 验证format参数顺序 ===')
dest = itinerary['destination']
days = itinerary['days']
preference = USER_PROFILE['旅行偏好'][0]
symbol = itinerary.get('currency_symbol', '¥')
budget = itinerary['budget']
currency = itinerary.get('currency_name', '人民币')
dep_city = itinerary.get('departure_city', '武汉')
total_cost = itinerary['total_cost']
budget_status = "未超预算" if itinerary['budget_status'] == 'under' else "已超预算"

print(f"索引0 (目的地): {dest}")
print(f"索引1 (天数): {days}")
print(f"索引2 (偏好): {preference}")
print(f"索引3 (货币符号): {symbol}")
print(f"索引4 (预算): {budget}")
print(f"索引5 (货币名称): {currency}")
print(f"索引6 (出发地): {dep_city}")
print(f"索引7 (总费用): {total_cost}")
print(f"索引8 (预算状态): {budget_status}")

# 测试3：验证行程概览表格
print()
print('=== 测试3: 行程概览表格 ===')
table = """| 项目 | 详情 |
|------|------|
| 出发地 | {6} |
| 目的地 | {0} |
| 旅行天数 | {1}天 |
| 预算 | {3}{4} ({5}) |
| 预计总费用 | {3}{7} |
| 预算状态 | {8} |""".format(
    dest, days, preference, symbol, budget, currency,
    dep_city, total_cost, budget_status
)
print(table)
