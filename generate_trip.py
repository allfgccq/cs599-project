"""生成杭州3日游行程"""
import sys
sys.path.insert(0, '.')
from app import generate_itinerary, generate_pdf_content
from datetime import datetime

# 生成杭州三天行程
itinerary = generate_itinerary('杭州', 3, 3000)

# 生成PDF内容
pdf_content = generate_pdf_content(itinerary)

# 保存到文件
file_name = f'杭州3日游行程_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
with open(file_name, 'w', encoding='utf-8') as f:
    f.write(pdf_content)

print('行程文件已生成:', file_name)
print('行程概览: 杭州3日游, 预算¥3000')
print('预计总费用: ¥%d' % itinerary["total_cost"])
print('预算状态:', '未超预算' if itinerary["budget_status"] == "under" else "已超预算")
