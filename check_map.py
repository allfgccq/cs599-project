#!/usr/bin/env python3
import re

with open('test_hangzhou_map.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ('DOCTYPE', '<!DOCTYPE html>'),
    ('Leaflet JS', 'leaflet.js'),
    ('initMap', 'initMap'),
    ('window.onload', 'window.onload'),
    ('L.map', 'L.map')
]

print('=== HTML文件检查 ===')
for name, pattern in checks:
    if pattern in content:
        print('✓ ' + name)
    else:
        print('❌ ' + name)

print()
print('文件大小:', len(content), '字符')

# 检查是否有未闭合的引号
double_quotes = content.count('"')
single_quotes = content.count("'")
print(f'双引号数量: {double_quotes}')
print(f'单引号数量: {single_quotes}')

# 检查JSON数据是否正确
if 'var routes = ' in content:
    print('✓ routes变量存在')
else:
    print('❌ routes变量缺失')

# 检查坐标数据
if 'attractionCoords' in content:
    print('✓ 景点坐标数据存在')
else:
    print('❌ 景点坐标数据缺失')

print()
print('=== 查看文件开头 ===')
print(content[:500])
