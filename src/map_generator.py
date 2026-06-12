#!/usr/bin/env python3
"""地图生成模块 - 使用高德地图API获取真实路线"""
import json
import sys
sys.path.insert(0, 'd:\\trae\\TravAgent')

from amap_api import geocode, get_driving_route, get_transit_route, get_walking_route

def get_real_route_points(start_lng, start_lat, end_lng, end_lat, mode='driving', city='杭州'):
    """
    获取真实路线的坐标点序列
    :param start_lng: 起点经度
    :param start_lat: 起点纬度
    :param end_lng: 终点经度
    :param end_lat: 终点纬度
    :param mode: 交通方式：driving, transit, walking
    :param city: 城市名称（用于公交路线查询）
    :return: 坐标点列表 [(lng, lat), ...]
    """
    if mode == 'driving':
        route = get_driving_route(start_lng, start_lat, end_lng, end_lat)
    elif mode == 'transit':
        route = get_transit_route(city, start_lng, start_lat, end_lng, end_lat)
    elif mode == 'walking':
        route = get_walking_route(start_lng, start_lat, end_lng, end_lat)
    else:
        route = get_driving_route(start_lng, start_lat, end_lng, end_lat)
    
    if route and 'polyline' in route:
        polyline = route['polyline']
        points = []
        for segment in polyline.split(';'):
            coords = segment.split(',')
            if len(coords) == 2:
                points.append((float(coords[0]), float(coords[1])))
        return points
    
    # 如果获取不到真实路线，返回直线
    return [(start_lng, start_lat), (end_lng, end_lat)]

def generate_map_content(itinerary):
    """生成地图HTML内容"""
    destination = itinerary['destination']
    days = itinerary['days']
    currency_symbol = itinerary.get('currency_symbol', '¥')
    
    day_colors = [
        {"line": "#3498db", "marker": "#2980b9"},
        {"line": "#e74c3c", "marker": "#c0392b"},
        {"line": "#2ecc71", "marker": "#27ae60"},
        {"line": "#f39c12", "marker": "#d68910"},
        {"line": "#9b59b6", "marker": "#8e44ad"},
        {"line": "#1abc9c", "marker": "#16a085"},
        {"line": "#e91e63", "marker": "#c2185b"},
    ]
    
    # 获取酒店坐标
    hotel_coord = None
    hotel_name = itinerary.get('hotel', {}).get('name', '')
    if hotel_name:
        hotel_geocode = geocode(hotel_name, destination)
        if hotel_geocode and hotel_geocode.get('success'):
            hotel_coord = [hotel_geocode['lng'], hotel_geocode['lat']]
    
    all_points = []
    # 添加酒店坐标
    if hotel_coord:
        all_points.append({'name': hotel_name, 'coord': hotel_coord, 'type': 'hotel'})
    
    # 添加景点坐标
    for day_plan in itinerary['daily_plan']:
        for attraction in day_plan['attractions']:
            if 'coord' in attraction:
                all_points.append({
                    'name': attraction['name'],
                    'coord': attraction['coord'],
                    'type': 'attraction'
                })
    
    # 计算地图中心点和缩放级别
    if all_points:
        lons = [p['coord'][0] for p in all_points]
        lats = [p['coord'][1] for p in all_points]
        center_lon = (min(lons) + max(lons)) / 2
        center_lat = (min(lats) + max(lats)) / 2
        lon_diff = max(lons) - min(lons)
        lat_diff = max(lats) - min(lats)
        max_diff = max(lon_diff, lat_diff)
        if max_diff < 0.05:
            zoom = 15
        elif max_diff < 0.1:
            zoom = 14
        elif max_diff < 0.3:
            zoom = 13
        elif max_diff < 0.5:
            zoom = 12
        else:
            zoom = 11
    else:
        center_lon, center_lat = 120.15, 30.27
        zoom = 12
    
    routes_data = []
    for day_idx, day_plan in enumerate(itinerary['daily_plan']):
        day_route = {
            "day": day_idx + 1,
            "color": day_colors[day_idx % len(day_colors)],
            "points": [],
            "transports": [],
            "route_segments": []
        }
        
        # 添加当天景点
        for i, attraction in enumerate(day_plan['attractions']):
            point_data = {
                "name": attraction['name'],
                "index": i + 1
            }
            if 'coord' in attraction:
                point_data["coord"] = attraction['coord']
            day_route["points"].append(point_data)
        
        # 添加交通方式和真实路线
        previous_coord = None
        for i, transport in enumerate(day_plan.get('transports', [])):
            transport_data = {
                "from": transport['from'],
                "to": transport['to'],
                "name": transport['name'],
                "icon": transport['icon'],
                "time": transport['time'],
                "cost": transport['cost'],
                "mode": transport.get('mode', 'driving')
            }
            
            # 获取路线坐标
            if 'coord' in day_route["points"][i] and 'coord' in day_route["points"][i+1]:
                start_coord = day_route["points"][i]["coord"]
                end_coord = day_route["points"][i+1]["coord"]
                
                # 根据交通方式获取真实路线
                mode = 'driving'
                if transport['icon'] == '🚇':
                    mode = 'transit'
                elif transport['icon'] == '🚶':
                    mode = 'walking'
                elif transport['icon'] == '🚌':
                    mode = 'transit'
                else:
                    mode = 'driving'
                
                route_points = get_real_route_points(
                    start_coord[0], start_coord[1],
                    end_coord[0], end_coord[1],
                    mode=mode,
                    city=destination
                )
                transport_data["route_points"] = route_points
                day_route["route_segments"].append({
                    "from": transport['from'],
                    "to": transport['to'],
                    "route_points": route_points,
                    "mode": mode
                })
            
            day_route["transports"].append(transport_data)
        
        routes_data.append(day_route)
    
    # 生成图例HTML
    legend_html = ""
    for r in routes_data:
        points_str = ", ".join([p["name"] for p in r["points"]])
        legend_html += '<div class="legend-item" data-day="{0}" onclick="toggleDay({0})"><div class="legend-color" style="background:{1}"></div><div><div class="legend-day">Day {0}</div><div class="legend-attractions">{2}</div></div></div>'.format(r["day"], r["color"]["line"], points_str)
    
    # 生成交通卡片HTML
    transport_html = ""
    for r in routes_data:
        transport_html += '<div class="day-transport" id="transport-day-{0}"><div class="day-header"><div class="day-badge" style="background:{1}">{0}</div><div class="day-title">第{0}天路线</div></div>'.format(r["day"], r["color"]["line"])
        if r["transports"]:
            for t in r["transports"]:
                transport_html += '<div class="transport-card" onclick="toggleDay({0})"><span class="transport-icon">{1}</span><div class="transport-info"><div class="transport-name">{2}</div><div class="transport-details">{3} → {4} · 约{5}分钟</div></div><div class="transport-cost">{6}{7}</div></div>'.format(r["day"], t["icon"], t["name"], t["from"], t["to"], t["time"], currency_symbol, t["cost"])
        else:
            transport_html += '<p style="color:#95a5a6; text-align:center; padding:10px;">当日景点间步行可达</p>'
        transport_html += '</div>'
    
    # 添加酒店信息到JSON数据
    routes_data.append({
        "day": 0,
        "color": {"line": "#667eea", "marker": "#5a6fd6"},
        "points": [{
            "name": hotel_name,
            "index": 0,
            "coord": hotel_coord
        }] if hotel_coord and hotel_name else [],
        "transports": [],
        "route_segments": []
    })
    
    routes_json = json.dumps(routes_data, ensure_ascii=False)
    
    # 使用字符串替换方式，避免格式化冲突
    html_content = HTML_TEMPLATE
    html_content = html_content.replace('{{destination}}', destination)
    html_content = html_content.replace('{{days}}', str(days))
    html_content = html_content.replace('{{legend_html}}', legend_html)
    html_content = html_content.replace('{{transport_html}}', transport_html)
    html_content = html_content.replace('{{routes_json}}', routes_json)
    html_content = html_content.replace('{{center_lat}}', str(center_lat))
    html_content = html_content.replace('{{center_lon}}', str(center_lon))
    html_content = html_content.replace('{{zoom}}', str(zoom))
    
    return html_content

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TravAgent - {{destination}}旅行地图</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 28px; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .map-container { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        #map { width: 100%; height: 500px; border-radius: 12px; }
        .legend { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .legend h3 { margin: 0 0 15px 0; color: #2c3e50; font-size: 18px; }
        .legend-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
        .legend-item { display: flex; align-items: center; padding: 10px; background: #f8f9fa; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
        .legend-item:hover, .legend-item.active { background: #e8f4fd; }
        .legend-color { width: 24px; height: 4px; border-radius: 2px; margin-right: 10px; }
        .legend-day { font-weight: bold; color: #2c3e50; }
        .legend-attractions { font-size: 12px; color: #7f8c8d; margin-top: 4px; }
        .transport-section { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 20px; }
        .transport-section h3 { margin: 0 0 15px 0; color: #2c3e50; font-size: 18px; }
        .day-transport { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee; opacity: 0.7; transition: opacity 0.3s; }
        .day-transport.active { opacity: 1; }
        .day-transport:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .day-header { display: flex; align-items: center; margin-bottom: 12px; }
        .day-badge { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px; }
        .day-title { font-weight: bold; color: #2c3e50; }
        .transport-card { display: flex; align-items: center; padding: 12px 15px; background: #f8f9fa; border-radius: 10px; margin: 8px 0; cursor: pointer; transition: all 0.3s; border-left: 4px solid transparent; }
        .transport-card:hover, .transport-card.active { background: #e8f4fd; transform: translateX(5px); }
        .transport-icon { font-size: 28px; margin-right: 15px; }
        .transport-info { flex: 1; }
        .transport-name { font-weight: bold; color: #2c3e50; }
        .transport-details { font-size: 13px; color: #7f8c8d; }
        .transport-cost { font-weight: bold; color: #3498db; }
        .map-controls { margin-bottom: 15px; display: flex; gap: 10px; }
        .control-btn { padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
        .control-btn:hover { background: #5a6fd6; }
        .control-btn.active { background: #2ecc71; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ {{destination}}旅行路线地图</h1>
            <p>共{{days}}天行程 · 点击图例或交通卡片高亮对应路线</p>
        </div>
        
        <div class="map-container">
            <div class="map-controls">
                <button class="control-btn active" onclick="showAllRoutes()">显示全部路线</button>
                <button class="control-btn" onclick="clearHighlight()">清除高亮</button>
            </div>
            <div id="map"></div>
        </div>
        
        <div class="legend">
            <h3>📅 每日路线图例</h3>
            <div class="legend-grid">
                {{legend_html}}
            </div>
        </div>
        
        <div class="transport-section">
            <h3>🚗 交通方式详情</h3>
            {{transport_html}}
        </div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var routes = {{routes_json}};
        var map;
        var markers = [];
        var polylines = [];
        var highlightedDay = null;
        
        function initMap() {
            map = L.map('map').setView([{{center_lat}}, {{center_lon}}], {{zoom}});
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            L.control.scale().addTo(map);
            drawRoutes();
        }
        
        function drawRoutes() {
            // 绘制酒店标记
            for (var r = 0; r < routes.length; r++) {
                var route = routes[r];
                
                // 绘制景点标记
                for (var i = 0; i < route.points.length; i++) {
                    var point = route.points[i];
                    if (point.coord) {
                        var markerIcon;
                        var popupContent;
                        
                        if (route.day === 0) {
                            // 酒店标记
                            markerIcon = L.divIcon({
                                className: 'custom-marker',
                                html: '<div style="background:#667eea; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; color:white; font-size:16px; box-shadow:0 2px 8px rgba(0,0,0,0.2);">🏨</div>',
                                iconSize: [32, 32],
                                iconAnchor: [16, 32]
                            });
                            popupContent = '<div style="min-width:150px;"><strong>🏨 ' + point.name + '</strong><br/>酒店位置</div>';
                        } else {
                            // 景点标记
                            markerIcon = L.divIcon({
                                className: 'custom-marker',
                                html: '<div style="background:' + route.color.marker + '; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; color:white; font-size:16px; font-weight:bold; box-shadow:0 2px 8px rgba(0,0,0,0.2);">' + point.index + '</div>',
                                iconSize: [36, 36],
                                iconAnchor: [18, 36]
                            });
                            popupContent = '<div style="min-width:150px;"><strong>Day ' + route.day + ': ' + point.name + '</strong></div>';
                        }
                        
                        var marker = L.marker([point.coord[1], point.coord[0]], {icon: markerIcon})
                            .addTo(map)
                            .bindPopup(popupContent);
                        markers.push({day: route.day, marker: marker});
                    }
                }
                
                // 绘制路线（真实路线而非直线）
                if (route.route_segments && route.route_segments.length > 0) {
                    for (var s = 0; s < route.route_segments.length; s++) {
                        var segment = route.route_segments[s];
                        if (segment.route_points && segment.route_points.length > 1) {
                            var latlngs = [];
                            for (var p = 0; p < segment.route_points.length; p++) {
                                latlngs.push([segment.route_points[p][1], segment.route_points[p][0]]);
                            }
                            
                            var polyline = L.polyline(latlngs, {
                                color: route.color.line,
                                weight: 6,
                                opacity: 0.7,
                                smoothFactor: 1,
                                day: route.day
                            }).addTo(map);
                            
                            // 添加点击事件
                            (function(polyline, route, segment) {
                                polyline.on('click', function(e) {
                                    showRoutePopup(e.latlng, route, segment);
                                    toggleDay(route.day);
                                });
                            })(polyline, route, segment);
                            
                            polylines.push({day: route.day, polyline: polyline});
                        }
                    }
                } else if (route.points && route.points.length > 1 && route.day > 0) {
                    // 如果没有真实路线，绘制简化路线
                    var latlngs = [];
                    for (var i = 0; i < route.points.length; i++) {
                        if (route.points[i].coord) {
                            latlngs.push([route.points[i].coord[1], route.points[i].coord[0]]);
                        }
                    }
                    if (latlngs.length > 1) {
                        var polyline = L.polyline(latlngs, {
                            color: route.color.line,
                            weight: 6,
                            opacity: 0.7,
                            dashArray: '10, 10',
                            day: route.day
                        }).addTo(map);
                        
                        (function(polyline, route) {
                            polyline.on('click', function(e) {
                                showRoutePopup(e.latlng, route);
                                toggleDay(route.day);
                            });
                        })(polyline, route);
                        
                        polylines.push({day: route.day, polyline: polyline});
                    }
                }
            }
        }
        
        function toggleDay(day) {
            if (highlightedDay === day) {
                clearHighlight();
                return;
            }
            
            highlightedDay = day;
            
            // 更新路线透明度
            for (var i = 0; i < polylines.length; i++) {
                if (polylines[i].day === day) {
                    polylines[i].polyline.setStyle({opacity: 1, weight: 8});
                } else {
                    polylines[i].polyline.setStyle({opacity: 0.2, weight: 4});
                }
            }
            
            // 更新标记
            for (var i = 0; i < markers.length; i++) {
                if (markers[i].day === day || day === 0 || markers[i].day === 0) {
                    markers[i].marker.setOpacity(1);
                } else {
                    markers[i].marker.setOpacity(0.3);
                }
            }
            
            // 更新图例
            try {
                var legendItems = document.querySelectorAll('.legend-item');
                legendItems.forEach(function(item) {
                    item.classList.remove('active');
                });
                var activeLegend = document.querySelector('.legend-item[data-day="' + day + '"]');
                if (activeLegend && activeLegend.classList) {
                    activeLegend.classList.add('active');
                }
            } catch(e) {
                console.log('Error updating legend:', e);
            }
            
            // 更新交通卡片
            try {
                var transportSections = document.querySelectorAll('.day-transport');
                transportSections.forEach(function(section) {
                    if (section && section.classList) {
                        section.classList.remove('active');
                    }
                });
                var activeTransport = document.getElementById('transport-day-' + day);
                if (activeTransport && activeTransport.classList) {
                    activeTransport.classList.add('active');
                }
            } catch(e) {
                console.log('Error updating transport sections:', e);
            }
        }
        
        function showRoutePopup(latlng, route, segment) {
            var pointsHtml = '<ul style="margin:0; padding-left:20px;">';
            route.points.forEach(function(point, idx) {
                pointsHtml += '<li><strong>' + (idx + 1) + '. ' + point.name + '</strong></li>';
            });
            pointsHtml += '</ul>';
            
            var transportHtml = '<div style="margin-top:8px; padding-top:8px; border-top:1px solid #eee;">';
            if (route.transports && route.transports.length > 0) {
                transportHtml += '<strong>交通方式：</strong><br/>';
                route.transports.forEach(function(t) {
                    transportHtml += t.icon + ' ' + t.name + ': ' + t.from + ' → ' + t.to + ' · 约' + t.time + '分钟<br/>';
                });
            } else {
                transportHtml += '<strong>交通方式：</strong>步行可达';
            }
            transportHtml += '</div>';
            
            var popupContent = '<div style="min-width:200px;">' +
                '<h4 style="margin:0 0 8px 0; color:#2c3e50;">Day ' + route.day + ' 路线详情</h4>' +
                '<div style="color:#7f8c8d;">途经景点：</div>' +
                pointsHtml +
                transportHtml +
                '</div>';
            
            L.popup({
                maxWidth: 300,
                closeButton: true,
                autoClose: false,
                closeOnClick: false
            })
            .setLatLng(latlng)
            .setContent(popupContent)
            .openOn(map);
        }
        
        function showAllRoutes() {
            highlightedDay = null;
            
            for (var i = 0; i < polylines.length; i++) {
                polylines[i].polyline.setStyle({opacity: 0.7, weight: 6});
            }
            
            for (var i = 0; i < markers.length; i++) {
                markers[i].marker.setOpacity(1);
            }
            
            // 更新图例
            try {
                var legendItems = document.querySelectorAll('.legend-item');
                legendItems.forEach(function(item) {
                    if (item && item.classList) {
                        item.classList.remove('active');
                    }
                });
            } catch(e) {
                console.log('Error updating legend:', e);
            }
            
            // 更新交通卡片
            try {
                var transportSections = document.querySelectorAll('.day-transport');
                transportSections.forEach(function(section) {
                    if (section && section.classList) {
                        section.classList.remove('active');
                    }
                });
            } catch(e) {
                console.log('Error updating transport sections:', e);
            }
        }
        
        function clearHighlight() {
            showAllRoutes();
        }
        
        // 页面加载完成后初始化地图
        document.addEventListener('DOMContentLoaded', initMap);
    </script>
</body>
</html>'''

if __name__ == "__main__":
    # 测试
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
                    {'name': '西溪湿地', 'coord': [120.0396, 30.2554]}
                ],
                'transports': [
                    {'from': '雷峰塔', 'to': '西溪湿地', 'name': '地铁', 'icon': '🚇', 'time': 45, 'cost': 6}
                ]
            },
            {
                'day': 3,
                'date': '2024-01-03',
                'attractions': [
                    {'name': '宋城', 'coord': [120.1215, 30.1954]}
                ],
                'transports': []
            }
        ]
    }
    
    content = generate_map_content(test_itinerary)
    with open('test_map.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('测试地图已生成: test_map.html')
