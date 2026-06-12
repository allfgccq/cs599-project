#!/usr/bin/env python3
"""完整流程测试脚本"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import generate_itinerary
from map_generator import generate_map_content

def test_full_flow():
    print('=== 测试完整流程: 北京→杭州，3天，3000元 ===')
    
    # 1. 生成行程
    print('\n1. 生成行程...')
    itinerary = generate_itinerary(
        destination='杭州',
        days=3,
        budget=3000,
        departure_city='北京',
        currency_symbol='¥',
        currency_name='人民币',
        currency_suffix='元'
    )
    print(f'   ✓ 行程生成成功')
    print(f'   - 出发地: {itinerary.get("departure_city")}')
    print(f'   - 目的地: {itinerary.get("destination")}')
    
    # 2. 生成地图内容
    print('\n2. 生成地图内容...')
    map_content = generate_map_content(itinerary)
    print(f'   ✓ 地图内容生成成功')
    print(f'   - HTML长度: {len(map_content)} 字符')
    
    # 3. 保存地图文件
    print('\n3. 保存地图文件...')
    map_path = './public/test_map.html'
    os.makedirs('./public', exist_ok=True)
    
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write(map_content)
    
    full_path = os.path.abspath(map_path)
    print(f'   ✓ 地图文件已保存')
    print(f'   - 路径: {full_path}')
    
    # 4. 验证文件内容
    print('\n4. 验证文件内容...')
    with open(map_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('DOCTYPE', '<!DOCTYPE html>'),
        ('Leaflet CSS', 'leaflet.css'),
        ('Leaflet JS', 'leaflet.js'),
        ('initMap', 'function initMap()'),
        ('L.map', 'L.map'),
        ('routes', 'var routes = '),
        ('route_segments', 'route_segments'),  # 真实路线数据
        ('drawRoutes', 'function drawRoutes()')  # 路线绘制函数
    ]
    
    all_passed = True
    for name, pattern in checks:
        if pattern in content:
            print(f'   ✓ {name}')
        else:
            print(f'   ✗ {name}')
            all_passed = False
    
    # 5. 检查JSON数据
    print('\n5. 检查JSON数据...')
    idx = content.find('var routes = ')
    if idx != -1:
        end_idx = content.find(';', idx)
        json_str = content[idx+12:end_idx]
        try:
            routes = json.loads(json_str)
            print(f'   ✓ JSON解析成功')
            print(f'   - 天数: {len(routes)}')
            for day in routes:
                points = day.get('points', [])
                print(f'     Day {day["day"]}: {len(points)} 个景点')
        except json.JSONDecodeError as e:
            print(f'   ✗ JSON解析失败: {e}')
            all_passed = False
    
    if all_passed:
        print('\n✅ 所有测试通过！')
        print(f'请打开文件查看地图: {full_path}')
    else:
        print('\n❌ 部分测试失败')
    
    return all_passed

if __name__ == '__main__':
    test_full_flow()
