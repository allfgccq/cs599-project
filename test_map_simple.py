#!/usr/bin/env python3
"""简单地图测试脚本"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from map_generator import generate_map_content

def test_map_generation():
    print('=== 测试地图生成功能 ===')
    
    # 创建模拟行程数据
    test_itinerary = {
        'destination': '杭州',
        'days': 3,
        'currency_symbol': '¥',
        'hotel': {'name': '杭州西湖国宾馆'},
        'daily_plan': [
            {
                'day': 1,
                'date': '2024-01-01',
                'attractions': [
                    {'name': '西湖', 'coord': [120.1552, 30.2741]},
                    {'name': '灵隐寺', 'coord': [120.1416, 30.2964]}
                ],
                'transports': [
                    {'from': '西湖', 'to': '灵隐寺', 'name': '打车', 'icon': '🚗', 'time': 25, 'cost': 35}
                ]
            },
            {
                'day': 2,
                'date': '2024-01-02',
                'attractions': [
                    {'name': '雷峰塔', 'coord': [120.1618, 30.2337]},
                    {'name': '西溪湿地', 'coord': [120.0895, 30.2882]}
                ],
                'transports': [
                    {'from': '雷峰塔', 'to': '西溪湿地', 'name': '地铁', 'icon': '🚇', 'time': 45, 'cost': 6}
                ]
            },
            {
                'day': 3,
                'date': '2024-01-03',
                'attractions': [
                    {'name': '宋城', 'coord': [120.1093, 30.1987]}
                ],
                'transports': []
            }
        ]
    }
    
    # 生成地图内容
    print('\n1. 生成地图内容...')
    try:
        map_content = generate_map_content(test_itinerary)
        print(f'   ✓ 地图内容生成成功')
        print(f'   - HTML长度: {len(map_content)} 字符')
    except Exception as e:
        print(f'   ✗ 地图生成失败: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    # 保存地图文件
    print('\n2. 保存地图文件...')
    map_path = './public/test_map_simple.html'
    os.makedirs('./public', exist_ok=True)
    
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write(map_content)
    
    full_path = os.path.abspath(map_path)
    print(f'   ✓ 地图文件已保存')
    print(f'   - 路径: {full_path}')
    
    # 验证文件内容
    print('\n3. 验证文件内容...')
    with open(map_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('DOCTYPE', '<!DOCTYPE html>'),
        ('Leaflet CSS', 'leaflet.css'),
        ('Leaflet JS', 'leaflet.js'),
        ('initMap', 'function initMap()'),
        ('L.map', 'L.map'),
        ('routes', 'var routes = '),
        ('西湖', '西湖'),
        ('灵隐寺', '灵隐寺'),
        ('雷峰塔', '雷峰塔'),
        ('西溪湿地', '西溪湿地'),
        ('宋城', '宋城')
    ]
    
    all_passed = True
    for name, pattern in checks:
        if pattern in content:
            print(f'   ✓ {name}')
        else:
            print(f'   ✗ {name}')
            all_passed = False
    
    # 检查JSON数据
    print('\n4. 检查JSON数据...')
    idx = content.find('var routes = ')
    if idx != -1:
        end_idx = content.find(';', idx)
        json_str = content[idx+12:end_idx]
        try:
            routes = json.loads(json_str)
            print(f'   ✓ JSON解析成功')
            print(f'   - 路线数: {len(routes)}')
            for day in routes:
                points = day.get('points', [])
                print(f'     Day {day["day"]}: {len(points)} 个点')
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
    test_map_generation()