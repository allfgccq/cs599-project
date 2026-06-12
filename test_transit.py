#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from map_generator import generate_map_content, get_real_route_points

def test_transit():
    print('Testing transit route...')
    
    # 测试地铁交通方式
    try:
        # 测试雷峰塔到西溪湿地的地铁路线
        route_points = get_real_route_points(
            120.1618, 30.2337,  # 雷峰塔
            120.0895, 30.2882,  # 西溪湿地
            mode='transit',
            city='杭州'
        )
        print('SUCCESS: Transit route generated')
        print('Route points:', len(route_points))
        return True
    except Exception as e:
        print('ERROR:', str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_transit()