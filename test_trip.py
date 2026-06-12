"""测试行程生成功能"""
import sys
sys.path.insert(0, '.')
from app import generate_itinerary, generate_pdf_content
from datetime import datetime

# 测试生成北京5天行程
print('测试行程生成...')
itinerary = generate_itinerary('北京', 5, 5000)

print(f'目的地: {itinerary["destination"]}')
print(f'天数: {itinerary["days"]}天')
print(f'预算: ¥{itinerary["budget"]}')
print(f'总费用: ¥{itinerary["total_cost"]}')
print(f'预算状态: {"未超预算" if itinerary["budget_status"] == "under" else "已超预算"}')

print('\n每日行程:')
for day_plan in itinerary['daily_plan']:
    print(f"\nDay {day_plan['day']} ({day_plan['date']}):")
    for a in day_plan['attractions']:
        print(f"  - {a['name']} (¥{a['price']})")
    print(f"  预计费用: ¥{day_plan['estimated_cost']}")

# 生成PDF内容
print('\n生成PDF内容...')
pdf_content = generate_pdf_content(itinerary)
print(f'PDF内容长度: {len(pdf_content)} 字符')

# 保存测试文件
file_name = f'测试行程_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
with open(file_name, 'w', encoding='utf-8') as f:
    f.write(pdf_content)
print(f'测试文件已保存: {file_name}')
