"""交通票务模块 - 提供高铁和飞机票查询功能"""
import random
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# 模拟高铁数据（当API调用失败时使用）
HIGH_SPEED_TRAINS = [
    # 北京 <-> 武汉
    {"train_no": "G1585", "train_type": "G", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "08:00", "arrival_time": "12:30", "duration": "4小时30分", "price": 520, "seat_type": "二等座"},
    {"train_no": "G1587", "train_type": "G", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "10:00", "arrival_time": "14:35", "duration": "4小时35分", "price": 520, "seat_type": "二等座"},
    {"train_no": "G81", "train_type": "G", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "12:00", "arrival_time": "15:50", "duration": "3小时50分", "price": 600, "seat_type": "二等座"},
    {"train_no": "G1591", "train_type": "G", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "14:00", "arrival_time": "18:40", "duration": "4小时40分", "price": 520, "seat_type": "二等座"},
    {"train_no": "G1593", "train_type": "G", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "16:00", "arrival_time": "20:35", "duration": "4小时35分", "price": 520, "seat_type": "二等座"},
    {"train_no": "G1586", "train_type": "G", "departure_city": "武汉", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "12:35", "duration": "4小时35分", "price": 520, "seat_type": "二等座"},
    {"train_no": "G1588", "train_type": "G", "departure_city": "武汉", "arrival_city": "北京", "departure_time": "10:00", "arrival_time": "14:40", "duration": "4小时40分", "price": 520, "seat_type": "二等座"},
    {"train_no": "G82", "train_type": "G", "departure_city": "武汉", "arrival_city": "北京", "departure_time": "12:00", "arrival_time": "15:55", "duration": "3小时55分", "price": 600, "seat_type": "二等座"},
    # 武汉 <-> 杭州
    {"train_no": "G591", "train_type": "G", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "07:00", "arrival_time": "11:15", "duration": "4小时15分", "price": 420, "seat_type": "二等座"},
    {"train_no": "G593", "train_type": "G", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "09:00", "arrival_time": "13:20", "duration": "4小时20分", "price": 420, "seat_type": "二等座"},
    {"train_no": "G1443", "train_type": "G", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "11:00", "arrival_time": "15:30", "duration": "4小时30分", "price": 400, "seat_type": "二等座"},
    {"train_no": "G1445", "train_type": "G", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "14:00", "arrival_time": "18:25", "duration": "4小时25分", "price": 400, "seat_type": "二等座"},
    {"train_no": "G592", "train_type": "G", "departure_city": "杭州", "arrival_city": "武汉", "departure_time": "07:30", "arrival_time": "11:45", "duration": "4小时15分", "price": 420, "seat_type": "二等座"},
    {"train_no": "G594", "train_type": "G", "departure_city": "杭州", "arrival_city": "武汉", "departure_time": "09:30", "arrival_time": "13:50", "duration": "4小时20分", "price": 420, "seat_type": "二等座"},
    {"train_no": "G1444", "train_type": "G", "departure_city": "杭州", "arrival_city": "武汉", "departure_time": "11:30", "arrival_time": "15:55", "duration": "4小时25分", "price": 400, "seat_type": "二等座"},
    # 北京 <-> 上海
    {"train_no": "G101", "train_type": "G", "departure_city": "北京", "arrival_city": "上海", "departure_time": "06:20", "arrival_time": "12:38", "duration": "6小时18分", "price": 669, "seat_type": "二等座"},
    {"train_no": "G103", "train_type": "G", "departure_city": "北京", "arrival_city": "上海", "departure_time": "07:00", "arrival_time": "12:32", "duration": "5小时32分", "price": 607, "seat_type": "二等座"},
    {"train_no": "G2", "train_type": "G", "departure_city": "北京", "arrival_city": "上海", "departure_time": "08:00", "arrival_time": "11:36", "duration": "3小时36分", "price": 669, "seat_type": "二等座"},
    {"train_no": "G1", "train_type": "G", "departure_city": "北京", "arrival_city": "上海", "departure_time": "09:00", "arrival_time": "12:37", "duration": "3小时37分", "price": 669, "seat_type": "二等座"},
    {"train_no": "G107", "train_type": "G", "departure_city": "北京", "arrival_city": "上海", "departure_time": "07:25", "arrival_time": "13:12", "duration": "5小时47分", "price": 607, "seat_type": "二等座"},
    {"train_no": "G102", "train_type": "G", "departure_city": "上海", "arrival_city": "北京", "departure_time": "06:17", "arrival_time": "12:38", "duration": "6小时21分", "price": 669, "seat_type": "二等座"},
    {"train_no": "G104", "train_type": "G", "departure_city": "上海", "arrival_city": "北京", "departure_time": "06:37", "arrival_time": "12:24", "duration": "5小时47分", "price": 607, "seat_type": "二等座"},
    {"train_no": "G106", "train_type": "G", "departure_city": "上海", "arrival_city": "北京", "departure_time": "07:22", "arrival_time": "13:12", "duration": "5小时50分", "price": 607, "seat_type": "二等座"},
    # 西安 <-> 北京
    {"train_no": "G651", "train_type": "G", "departure_city": "北京", "arrival_city": "西安", "departure_time": "08:00", "arrival_time": "12:21", "duration": "4小时21分", "price": 515, "seat_type": "二等座"},
    {"train_no": "G653", "train_type": "G", "departure_city": "北京", "arrival_city": "西安", "departure_time": "10:00", "arrival_time": "14:21", "duration": "4小时21分", "price": 515, "seat_type": "二等座"},
    {"train_no": "G655", "train_type": "G", "departure_city": "北京", "arrival_city": "西安", "departure_time": "12:00", "arrival_time": "16:26", "duration": "4小时26分", "price": 515, "seat_type": "二等座"},
    {"train_no": "G652", "train_type": "G", "departure_city": "西安", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "12:26", "duration": "4小时26分", "price": 515, "seat_type": "二等座"},
    {"train_no": "G654", "train_type": "G", "departure_city": "西安", "arrival_city": "北京", "departure_time": "10:00", "arrival_time": "14:21", "duration": "4小时21分", "price": 515, "seat_type": "二等座"},
    # 青岛 <-> 北京
    {"train_no": "G2", "train_type": "G", "departure_city": "北京", "arrival_city": "青岛", "departure_time": "08:00", "arrival_time": "11:36", "duration": "3小时36分", "price": 335, "seat_type": "二等座"},
    {"train_no": "G26", "train_type": "G", "departure_city": "北京", "arrival_city": "青岛", "departure_time": "14:00", "arrival_time": "17:38", "duration": "3小时38分", "price": 335, "seat_type": "二等座"},
    {"train_no": "G25", "train_type": "G", "departure_city": "青岛", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "11:38", "duration": "3小时38分", "price": 335, "seat_type": "二等座"},
    {"train_no": "G27", "train_type": "G", "departure_city": "青岛", "arrival_city": "北京", "departure_time": "14:30", "arrival_time": "18:08", "duration": "3小时38分", "price": 335, "seat_type": "二等座"},
    # 上海 <-> 杭州
    {"train_no": "G7301", "train_type": "G", "departure_city": "上海", "arrival_city": "杭州", "departure_time": "06:17", "arrival_time": "07:38", "duration": "1小时21分", "price": 73, "seat_type": "二等座"},
    {"train_no": "G7303", "train_type": "G", "departure_city": "上海", "arrival_city": "杭州", "departure_time": "07:00", "arrival_time": "08:26", "duration": "1小时26分", "price": 73, "seat_type": "二等座"},
    {"train_no": "G7305", "train_type": "G", "departure_city": "上海", "arrival_city": "杭州", "departure_time": "08:00", "arrival_time": "09:24", "duration": "1小时24分", "price": 73, "seat_type": "二等座"},
    {"train_no": "G7302", "train_type": "G", "departure_city": "杭州", "arrival_city": "上海", "departure_time": "06:30", "arrival_time": "07:58", "duration": "1小时28分", "price": 73, "seat_type": "二等座"},
    {"train_no": "G7304", "train_type": "G", "departure_city": "杭州", "arrival_city": "上海", "departure_time": "07:30", "arrival_time": "08:55", "duration": "1小时25分", "price": 73, "seat_type": "二等座"},
    # 广州 <-> 北京
    {"train_no": "G77", "train_type": "G", "departure_city": "北京", "arrival_city": "广州", "departure_time": "07:00", "arrival_time": "17:16", "duration": "10小时16分", "price": 1021, "seat_type": "二等座"},
    {"train_no": "G79", "train_type": "G", "departure_city": "北京", "arrival_city": "广州", "departure_time": "10:00", "arrival_time": "19:24", "duration": "9小时24分", "price": 1021, "seat_type": "二等座"},
    {"train_no": "G78", "train_type": "G", "departure_city": "广州", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "18:16", "duration": "10小时16分", "price": 1021, "seat_type": "二等座"},
    {"train_no": "G80", "train_type": "G", "departure_city": "广州", "arrival_city": "北京", "departure_time": "10:00", "arrival_time": "19:24", "duration": "9小时24分", "price": 1021, "seat_type": "二等座"},
    # 深圳 <-> 北京
    {"train_no": "G81", "train_type": "G", "departure_city": "北京", "arrival_city": "深圳", "departure_time": "07:10", "arrival_time": "19:35", "duration": "12小时25分", "price": 1083, "seat_type": "二等座"},
    {"train_no": "G83", "train_type": "G", "departure_city": "北京", "arrival_city": "深圳", "departure_time": "08:00", "arrival_time": "20:21", "duration": "12小时21分", "price": 1083, "seat_type": "二等座"},
    {"train_no": "G82", "train_type": "G", "departure_city": "深圳", "arrival_city": "北京", "departure_time": "07:00", "arrival_time": "19:35", "duration": "12小时35分", "price": 1083, "seat_type": "二等座"},
    {"train_no": "G84", "train_type": "G", "departure_city": "深圳", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "20:21", "duration": "12小时21分", "price": 1083, "seat_type": "二等座"},
    # 成都 <-> 北京
    {"train_no": "G351", "train_type": "G", "departure_city": "北京", "arrival_city": "成都", "departure_time": "08:00", "arrival_time": "17:32", "duration": "9小时32分", "price": 630, "seat_type": "二等座"},
    {"train_no": "G353", "train_type": "G", "departure_city": "北京", "arrival_city": "成都", "departure_time": "10:00", "arrival_time": "19:30", "duration": "9小时30分", "price": 630, "seat_type": "二等座"},
    {"train_no": "G352", "train_type": "G", "departure_city": "成都", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "17:32", "duration": "9小时32分", "price": 630, "seat_type": "二等座"},
    {"train_no": "G354", "train_type": "G", "departure_city": "成都", "arrival_city": "北京", "departure_time": "10:00", "arrival_time": "19:30", "duration": "9小时30分", "price": 630, "seat_type": "二等座"},
    # 重庆 <-> 北京
    {"train_no": "G371", "train_type": "G", "departure_city": "北京", "arrival_city": "重庆", "departure_time": "07:00", "arrival_time": "18:12", "duration": "11小时12分", "price": 720, "seat_type": "二等座"},
    {"train_no": "G373", "train_type": "G", "departure_city": "北京", "arrival_city": "重庆", "departure_time": "08:00", "arrival_time": "19:12", "duration": "11小时12分", "price": 720, "seat_type": "二等座"},
    {"train_no": "G372", "train_type": "G", "departure_city": "重庆", "arrival_city": "北京", "departure_time": "07:00", "arrival_time": "18:12", "duration": "11小时12分", "price": 720, "seat_type": "二等座"},
    {"train_no": "G374", "train_type": "G", "departure_city": "重庆", "arrival_city": "北京", "departure_time": "08:00", "arrival_time": "19:12", "duration": "11小时12分", "price": 720, "seat_type": "二等座"},
    # 南京 <-> 北京
    {"train_no": "G101", "train_type": "G", "departure_city": "北京", "arrival_city": "南京", "departure_time": "06:20", "arrival_time": "10:40", "duration": "4小时20分", "price": 443, "seat_type": "二等座"},
    {"train_no": "G103", "train_type": "G", "departure_city": "北京", "arrival_city": "南京", "departure_time": "07:00", "arrival_time": "11:12", "duration": "4小时12分", "price": 443, "seat_type": "二等座"},
    {"train_no": "G102", "train_type": "G", "departure_city": "南京", "arrival_city": "北京", "departure_time": "06:17", "arrival_time": "10:35", "duration": "4小时18分", "price": 443, "seat_type": "二等座"},
    {"train_no": "G104", "train_type": "G", "departure_city": "南京", "arrival_city": "北京", "departure_time": "06:37", "arrival_time": "10:49", "duration": "4小时12分", "price": 443, "seat_type": "二等座"},
]

# 模拟航班数据（当API调用失败时使用）
FLIGHTS = [
    # 北京 <-> 武汉
    {"flight_no": "CA8227", "airline": "国航", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "07:30", "arrival_time": "09:50", "duration": "2小时20分", "price": 800, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "天河T3"},
    {"flight_no": "MU2456", "airline": "东航", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "09:00", "arrival_time": "11:20", "duration": "2小时20分", "price": 900, "seat_type": "经济舱", "departure_airport": "大兴", "arrival_airport": "天河T3"},
    {"flight_no": "CZ3128", "airline": "南航", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "11:30", "arrival_time": "13:55", "duration": "2小时25分", "price": 750, "seat_type": "经济舱", "departure_airport": "大兴", "arrival_airport": "天河T2"},
    {"flight_no": "HU7156", "airline": "海航", "departure_city": "北京", "arrival_city": "武汉", "departure_time": "14:00", "arrival_time": "16:25", "duration": "2小时25分", "price": 850, "seat_type": "经济舱", "departure_airport": "首都T2", "arrival_airport": "天河T3"},
    {"flight_no": "CA8228", "airline": "国航", "departure_city": "武汉", "arrival_city": "北京", "departure_time": "10:30", "arrival_time": "12:50", "duration": "2小时20分", "price": 800, "seat_type": "经济舱", "departure_airport": "天河T3", "arrival_airport": "首都T3"},
    {"flight_no": "MU2455", "airline": "东航", "departure_city": "武汉", "arrival_city": "北京", "departure_time": "12:00", "arrival_time": "14:20", "duration": "2小时20分", "price": 900, "seat_type": "经济舱", "departure_airport": "天河T3", "arrival_airport": "大兴"},
    # 武汉 <-> 杭州
    {"flight_no": "MU5321", "airline": "东航", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "08:00", "arrival_time": "09:30", "duration": "1小时30分", "price": 550, "seat_type": "经济舱", "departure_airport": "天河T3", "arrival_airport": "萧山T3"},
    {"flight_no": "CA1832", "airline": "国航", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "10:00", "arrival_time": "11:35", "duration": "1小时35分", "price": 600, "seat_type": "经济舱", "departure_airport": "天河T2", "arrival_airport": "萧山T4"},
    {"flight_no": "CZ3867", "airline": "南航", "departure_city": "武汉", "arrival_city": "杭州", "departure_time": "13:00", "arrival_time": "14:30", "duration": "1小时30分", "price": 500, "seat_type": "经济舱", "departure_airport": "天河T3", "arrival_airport": "萧山T3"},
    {"flight_no": "MU5322", "airline": "东航", "departure_city": "杭州", "arrival_city": "武汉", "departure_time": "09:00", "arrival_time": "10:35", "duration": "1小时35分", "price": 550, "seat_type": "经济舱", "departure_airport": "萧山T3", "arrival_airport": "天河T3"},
    {"flight_no": "CA1831", "airline": "国航", "departure_city": "杭州", "arrival_city": "武汉", "departure_time": "11:00", "arrival_time": "12:30", "duration": "1小时30分", "price": 600, "seat_type": "经济舱", "departure_airport": "萧山T4", "arrival_airport": "天河T2"},
    # 北京 <-> 上海
    {"flight_no": "CA1501", "airline": "国航", "departure_city": "北京", "arrival_city": "上海", "departure_time": "07:00", "arrival_time": "09:10", "duration": "2小时10分", "price": 500, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "浦东T2"},
    {"flight_no": "MU5101", "airline": "东航", "departure_city": "北京", "arrival_city": "上海", "departure_time": "08:00", "arrival_time": "10:15", "duration": "2小时15分", "price": 550, "seat_type": "经济舱", "departure_airport": "大兴", "arrival_airport": "虹桥T2"},
    {"flight_no": "CA1502", "airline": "国航", "departure_city": "上海", "arrival_city": "北京", "departure_time": "09:00", "arrival_time": "11:10", "duration": "2小时10分", "price": 500, "seat_type": "经济舱", "departure_airport": "浦东T2", "arrival_airport": "首都T3"},
    {"flight_no": "MU5102", "airline": "东航", "departure_city": "上海", "arrival_city": "北京", "departure_time": "10:00", "arrival_time": "12:15", "duration": "2小时15分", "price": 550, "seat_type": "经济舱", "departure_airport": "虹桥T2", "arrival_airport": "大兴"},
    # 北京 <-> 广州
    {"flight_no": "CA1301", "airline": "国航", "departure_city": "北京", "arrival_city": "广州", "departure_time": "07:00", "arrival_time": "10:30", "duration": "3小时30分", "price": 1200, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "白云T2"},
    {"flight_no": "CZ3501", "airline": "南航", "departure_city": "北京", "arrival_city": "广州", "departure_time": "08:00", "arrival_time": "11:35", "duration": "3小时35分", "price": 1150, "seat_type": "经济舱", "departure_airport": "大兴", "arrival_airport": "白云T2"},
    {"flight_no": "CA1302", "airline": "国航", "departure_city": "广州", "arrival_city": "北京", "departure_time": "09:00", "arrival_time": "12:30", "duration": "3小时30分", "price": 1200, "seat_type": "经济舱", "departure_airport": "白云T2", "arrival_airport": "首都T3"},
    {"flight_no": "CZ3502", "airline": "南航", "departure_city": "广州", "arrival_city": "北京", "departure_time": "10:00", "arrival_time": "13:35", "duration": "3小时35分", "price": 1150, "seat_type": "经济舱", "departure_airport": "白云T2", "arrival_airport": "大兴"},
    # 北京 <-> 深圳
    {"flight_no": "CA1331", "airline": "国航", "departure_city": "北京", "arrival_city": "深圳", "departure_time": "07:30", "arrival_time": "11:10", "duration": "3小时40分", "price": 1300, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "宝安T3"},
    {"flight_no": "ZH9101", "airline": "深航", "departure_city": "北京", "arrival_city": "深圳", "departure_time": "08:30", "arrival_time": "12:15", "duration": "3小时45分", "price": 1250, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "宝安T3"},
    {"flight_no": "CA1332", "airline": "国航", "departure_city": "深圳", "arrival_city": "北京", "departure_time": "09:30", "arrival_time": "13:10", "duration": "3小时40分", "price": 1300, "seat_type": "经济舱", "departure_airport": "宝安T3", "arrival_airport": "首都T3"},
    # 北京 <-> 成都
    {"flight_no": "CA4101", "airline": "国航", "departure_city": "北京", "arrival_city": "成都", "departure_time": "07:00", "arrival_time": "10:15", "duration": "3小时15分", "price": 900, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "天府T2"},
    {"flight_no": "HU7141", "airline": "海航", "departure_city": "北京", "arrival_city": "成都", "departure_time": "08:00", "arrival_time": "11:20", "duration": "3小时20分", "price": 850, "seat_type": "经济舱", "departure_airport": "首都T2", "arrival_airport": "双流T2"},
    {"flight_no": "CA4102", "airline": "国航", "departure_city": "成都", "arrival_city": "北京", "departure_time": "09:00", "arrival_time": "12:15", "duration": "3小时15分", "price": 900, "seat_type": "经济舱", "departure_airport": "天府T2", "arrival_airport": "首都T3"},
    # 北京 <-> 重庆
    {"flight_no": "CA4119", "airline": "国航", "departure_city": "北京", "arrival_city": "重庆", "departure_time": "07:30", "arrival_time": "10:45", "duration": "3小时15分", "price": 800, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "江北T3"},
    {"flight_no": "3U8831", "airline": "川航", "departure_city": "北京", "arrival_city": "重庆", "departure_time": "08:30", "arrival_time": "11:50", "duration": "3小时20分", "price": 750, "seat_type": "经济舱", "departure_airport": "大兴", "arrival_airport": "江北T3"},
    {"flight_no": "CA4120", "airline": "国航", "departure_city": "重庆", "arrival_city": "北京", "departure_time": "09:30", "arrival_time": "12:45", "duration": "3小时15分", "price": 800, "seat_type": "经济舱", "departure_airport": "江北T3", "arrival_airport": "首都T3"},
    # 北京 <-> 西安
    {"flight_no": "CA1201", "airline": "国航", "departure_city": "北京", "arrival_city": "西安", "departure_time": "07:00", "arrival_time": "09:30", "duration": "2小时30分", "price": 650, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "咸阳T3"},
    {"flight_no": "MU2201", "airline": "东航", "departure_city": "北京", "arrival_city": "西安", "departure_time": "08:00", "arrival_time": "10:35", "duration": "2小时35分", "price": 600, "seat_type": "经济舱", "departure_airport": "大兴", "arrival_airport": "咸阳T5"},
    {"flight_no": "CA1202", "airline": "国航", "departure_city": "西安", "arrival_city": "北京", "departure_time": "09:00", "arrival_time": "11:30", "duration": "2小时30分", "price": 650, "seat_type": "经济舱", "departure_airport": "咸阳T3", "arrival_airport": "首都T3"},
    # 北京 <-> 青岛
    {"flight_no": "CA1521", "airline": "国航", "departure_city": "北京", "arrival_city": "青岛", "departure_time": "07:30", "arrival_time": "09:20", "duration": "1小时50分", "price": 550, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "胶东"},
    {"flight_no": "SC4614", "airline": "山航", "departure_city": "北京", "arrival_city": "青岛", "departure_time": "08:30", "arrival_time": "10:25", "duration": "1小时55分", "price": 500, "seat_type": "经济舱", "departure_airport": "首都T3", "arrival_airport": "胶东"},
    {"flight_no": "CA1522", "airline": "国航", "departure_city": "青岛", "arrival_city": "北京", "departure_time": "09:30", "arrival_time": "11:20", "duration": "1小时50分", "price": 550, "seat_type": "经济舱", "departure_airport": "胶东", "arrival_airport": "首都T3"},
    # 上海 <-> 杭州
    {"flight_no": "MU5191", "airline": "东航", "departure_city": "上海", "arrival_city": "杭州", "departure_time": "07:00", "arrival_time": "08:00", "duration": "1小时", "price": 350, "seat_type": "经济舱", "departure_airport": "虹桥T2", "arrival_airport": "萧山T3"},
    {"flight_no": "CA1701", "airline": "国航", "departure_city": "上海", "arrival_city": "杭州", "departure_time": "08:00", "arrival_time": "09:05", "duration": "1小时5分", "price": 380, "seat_type": "经济舱", "departure_airport": "浦东T2", "arrival_airport": "萧山T4"},
    {"flight_no": "MU5192", "airline": "东航", "departure_city": "杭州", "arrival_city": "上海", "departure_time": "08:30", "arrival_time": "09:30", "duration": "1小时", "price": 350, "seat_type": "经济舱", "departure_airport": "萧山T3", "arrival_airport": "虹桥T2"},
    # 上海 <-> 广州
    {"flight_no": "MU5311", "airline": "东航", "departure_city": "上海", "arrival_city": "广州", "departure_time": "07:00", "arrival_time": "09:50", "duration": "2小时50分", "price": 850, "seat_type": "经济舱", "departure_airport": "虹桥T2", "arrival_airport": "白云T2"},
    {"flight_no": "CA8561", "airline": "国航", "departure_city": "上海", "arrival_city": "广州", "departure_time": "08:00", "arrival_time": "10:55", "duration": "2小时55分", "price": 800, "seat_type": "经济舱", "departure_airport": "浦东T2", "arrival_airport": "白云T2"},
    {"flight_no": "MU5312", "airline": "东航", "departure_city": "广州", "arrival_city": "上海", "departure_time": "09:00", "arrival_time": "11:50", "duration": "2小时50分", "price": 850, "seat_type": "经济舱", "departure_airport": "白云T2", "arrival_airport": "虹桥T2"},
    # 杭州 <-> 广州
    {"flight_no": "CA1795", "airline": "国航", "departure_city": "杭州", "arrival_city": "广州", "departure_time": "07:00", "arrival_time": "09:40", "duration": "2小时40分", "price": 750, "seat_type": "经济舱", "departure_airport": "萧山T4", "arrival_airport": "白云T2"},
    {"flight_no": "CZ3861", "airline": "南航", "departure_city": "杭州", "arrival_city": "广州", "departure_time": "08:00", "arrival_time": "10:45", "duration": "2小时45分", "price": 700, "seat_type": "经济舱", "departure_airport": "萧山T3", "arrival_airport": "白云T2"},
    {"flight_no": "CA1796", "airline": "国航", "departure_city": "广州", "arrival_city": "杭州", "departure_time": "09:00", "arrival_time": "11:40", "duration": "2小时40分", "price": 750, "seat_type": "经济舱", "departure_airport": "白云T2", "arrival_airport": "萧山T4"},
    # 西安 <-> 杭州
    {"flight_no": "MU2301", "airline": "东航", "departure_city": "西安", "arrival_city": "杭州", "departure_time": "07:00", "arrival_time": "09:10", "duration": "2小时10分", "price": 600, "seat_type": "经济舱", "departure_airport": "咸阳T5", "arrival_airport": "萧山T3"},
    {"flight_no": "CA1765", "airline": "国航", "departure_city": "西安", "arrival_city": "杭州", "departure_time": "08:00", "arrival_time": "10:15", "duration": "2小时15分", "price": 650, "seat_type": "经济舱", "departure_airport": "咸阳T3", "arrival_airport": "萧山T4"},
    {"flight_no": "MU2302", "airline": "东航", "departure_city": "杭州", "arrival_city": "西安", "departure_time": "09:00", "arrival_time": "11:10", "duration": "2小时10分", "price": 600, "seat_type": "经济舱", "departure_airport": "萧山T3", "arrival_airport": "咸阳T5"},
    # 青岛 <-> 杭州
    {"flight_no": "SC4751", "airline": "山航", "departure_city": "青岛", "arrival_city": "杭州", "departure_time": "07:00", "arrival_time": "08:40", "duration": "1小时40分", "price": 450, "seat_type": "经济舱", "departure_airport": "胶东", "arrival_airport": "萧山T3"},
    {"flight_no": "CA1741", "airline": "国航", "departure_city": "青岛", "arrival_city": "杭州", "departure_time": "08:00", "arrival_time": "09:45", "duration": "1小时45分", "price": 500, "seat_type": "经济舱", "departure_airport": "胶东", "arrival_airport": "萧山T4"},
    {"flight_no": "SC4752", "airline": "山航", "departure_city": "杭州", "arrival_city": "青岛", "departure_time": "09:00", "arrival_time": "10:40", "duration": "1小时40分", "price": 450, "seat_type": "经济舱", "departure_airport": "萧山T3", "arrival_airport": "胶东"},
]


def search_high_speed_trains(departure_city: str, arrival_city: str, date: Optional[str] = None) -> List[Dict]:
    """
    查询高铁车次
    :param departure_city: 出发城市
    :param arrival_city: 到达城市
    :param date: 日期（可选）
    :return: 高铁车次列表
    """
    # 优先尝试使用真实API
    results = _try_train_api(departure_city, arrival_city, date)
    
    # 如果API调用失败，使用模拟数据
    if not results:
        results = _get_mock_trains(departure_city, arrival_city)
    
    return results


def search_flights(departure_city: str, arrival_city: str, date: Optional[str] = None) -> List[Dict]:
    """
    查询航班
    :param departure_city: 出发城市
    :param arrival_city: 到达城市
    :param date: 日期（可选）
    :return: 航班列表
    """
    # 优先尝试使用真实API
    results = _try_flight_api(departure_city, arrival_city, date)
    
    # 如果API调用失败，使用模拟数据
    if not results:
        results = _get_mock_flights(departure_city, arrival_city)
    
    return results


def _try_train_api(departure_city: str, arrival_city: str, date: str) -> List[Dict]:
    """
    尝试调用真实高铁API
    """
    rapid_api_key = os.getenv("RAPID_API_KEY")
    
    if not rapid_api_key:
        return []
    
    # 城市名称映射
    city_mapping = {
        "北京": "Beijing",
        "上海": "Shanghai",
        "杭州": "Hangzhou",
        "西安": "Xian",
        "武汉": "Wuhan",
        "青岛": "Qingdao",
        "南京": "Nanjing",
        "成都": "Chengdu",
        "重庆": "Chongqing",
        "广州": "Guangzhou",
        "深圳": "Shenzhen"
    }
    
    url = "https://booking-search.p.rapidapi.com/flights/search"
    
    querystring = {
        "from": city_mapping.get(departure_city, departure_city),
        "to": city_mapping.get(arrival_city, arrival_city),
        "date": date if date else datetime.now().strftime("%Y-%m-%d"),
        "currency": "CNY"
    }
    
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "booking-search.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if isinstance(data, list) and data:
            for item in data[:10]:
                try:
                    # 尝试解析高铁数据
                    results.append({
                        "train_no": item.get("train_no", item.get("number", "G000")),
                        "train_type": "G",
                        "departure_city": departure_city,
                        "arrival_city": arrival_city,
                        "departure_time": item.get("departure_time", "08:00"),
                        "arrival_time": item.get("arrival_time", "12:00"),
                        "duration": item.get("duration", "4小时"),
                        "price": int(item.get("price", {}).get("current", 500)),
                        "seat_type": "二等座",
                        "available_seats": random.randint(10, 100)
                    })
                except Exception:
                    continue
        
        return results
    except Exception:
        return []


def _try_flight_api(departure_city: str, arrival_city: str, date: str) -> List[Dict]:
    """
    尝试调用真实航班API
    """
    rapid_api_key = os.getenv("RAPID_API_KEY")
    
    if not rapid_api_key:
        return []
    
    # 城市名称映射
    city_mapping = {
        "北京": "Beijing",
        "上海": "Shanghai",
        "杭州": "Hangzhou",
        "西安": "Xian",
        "武汉": "Wuhan",
        "青岛": "Qingdao",
        "南京": "Nanjing",
        "成都": "Chengdu",
        "重庆": "Chongqing",
        "广州": "Guangzhou",
        "深圳": "Shenzhen"
    }
    
    url = "https://booking-search.p.rapidapi.com/flights/search"
    
    querystring = {
        "from": city_mapping.get(departure_city, departure_city),
        "to": city_mapping.get(arrival_city, arrival_city),
        "date": date if date else datetime.now().strftime("%Y-%m-%d"),
        "currency": "CNY"
    }
    
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "booking-search.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if isinstance(data, list) and data:
            for item in data[:10]:
                try:
                    results.append({
                        "flight_no": item.get("number", "CA0000"),
                        "airline": item.get("airline", "未知航司"),
                        "departure_city": departure_city,
                        "arrival_city": arrival_city,
                        "departure_time": item.get("departure_time", "08:00"),
                        "arrival_time": item.get("arrival_time", "10:00"),
                        "duration": item.get("duration", "2小时"),
                        "price": int(item.get("price", {}).get("current", 800)),
                        "seat_type": "经济舱",
                        "available_seats": random.randint(10, 100),
                        "departure_airport": item.get("departure_airport", "机场"),
                        "arrival_airport": item.get("arrival_airport", "机场")
                    })
                except Exception:
                    continue
        
        return results
    except Exception:
        return []


def _get_mock_trains(departure_city: str, arrival_city: str) -> List[Dict]:
    """
    获取模拟高铁数据
    """
    results = []
    for train in HIGH_SPEED_TRAINS:
        if train["departure_city"] == departure_city and train["arrival_city"] == arrival_city:
            price_variation = random.uniform(-0.1, 0.1)
            result = train.copy()
            result["price"] = int(train["price"] * (1 + price_variation))
            result["available_seats"] = random.randint(10, 100)
            results.append(result)
    
    results.sort(key=lambda x: x["departure_time"])
    return results


def _get_mock_flights(departure_city: str, arrival_city: str) -> List[Dict]:
    """
    获取模拟航班数据
    """
    results = []
    for flight in FLIGHTS:
        if flight["departure_city"] == departure_city and flight["arrival_city"] == arrival_city:
            price_variation = random.uniform(-0.2, 0.3)
            result = flight.copy()
            result["price"] = int(flight["price"] * (1 + price_variation))
            result["available_seats"] = random.randint(10, 100)
            results.append(result)
    
    results.sort(key=lambda x: x["departure_time"])
    return results


def calculate_arrival_datetime(departure_date: str, departure_time: str, duration: str) -> str:
    """
    计算到达日期时间
    """
    departure_dt = datetime.strptime(f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M")
    
    hours = 0
    minutes = 0
    if "小时" in duration:
        parts = duration.split("小时")
        hours = int(parts[0])
        if len(parts) > 1 and "分" in parts[1]:
            minutes = int(parts[1].replace("分", "").strip())
    elif "分" in duration:
        minutes = int(duration.replace("分", "").strip())
    
    arrival_dt = departure_dt + timedelta(hours=hours, minutes=minutes)
    return arrival_dt.strftime("%Y-%m-%d %H:%M")


def get_travel_time_hours(duration: str) -> float:
    """
    将时长转换为小时数
    """
    hours = 0
    minutes = 0
    if "小时" in duration:
        parts = duration.split("小时")
        hours = int(parts[0])
        if len(parts) > 1 and "分" in parts[1]:
            minutes = int(parts[1].replace("分", "").strip())
    elif "分" in duration:
        minutes = int(duration.replace("分", "").strip())
    
    return hours + minutes / 60.0


def generate_transport_options_html(departure_city: str, arrival_city: str, date: str, transport_type: str = "both") -> str:
    """
    生成交通工具选择的HTML（带下拉列表）
    """
    trains = []
    flights = []
    
    if transport_type in ["train", "both"]:
        trains = search_high_speed_trains(departure_city, arrival_city, date)
    
    if transport_type in ["flight", "both"]:
        flights = search_flights(departure_city, arrival_city, date)
    
    html = f"""
    <div style="margin-bottom: 20px;">
        <h4>🚄 选择去程交通方案</h4>
        <p style="color: #888; font-size: 14px;">{departure_city} → {arrival_city}</p>
    </div>
    """
    
    # 高铁选项
    if trains:
        train_options = ""
        for train in trains:
            train_options += f"""
            <option value="train_{train['train_no']}">
                🚄 {train['train_no']} | {train['departure_time']} → {train['arrival_time']} | ¥{train['price']} | {train['duration']}
            </option>
            """
        
        html += f"""
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 8px; font-weight: bold;">高铁车次:</label>
            <select id="departure_train" style="width: 100%; padding: 10px; border-radius: 8px; background: #2a2a2a; color: white; border: 1px solid #444;">
                <option value="">请选择高铁车次</option>
                {train_options}
            </select>
        </div>
        """
    
    # 航班选项
    if flights:
        flight_options = ""
        for flight in flights:
            flight_options += f"""
            <option value="flight_{flight['flight_no']}">
                ✈️ {flight['flight_no']} ({flight['airline']}) | {flight['departure_time']} → {flight['arrival_time']} | ¥{flight['price']} | {flight['duration']}
            </option>
            """
        
        html += f"""
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 8px; font-weight: bold;">航班:</label>
            <select id="departure_flight" style="width: 100%; padding: 10px; border-radius: 8px; background: #2a2a2a; color: white; border: 1px solid #444;">
                <option value="">请选择航班</option>
                {flight_options}
            </select>
        </div>
        """
    
    return html


if __name__ == "__main__":
    print("=== 高铁查询测试 ===")
    trains = search_high_speed_trains("北京", "武汉")
    for train in trains:
        print(f"{train['train_no']}: {train['departure_time']} -> {train['arrival_time']}, ¥{train['price']}")
    
    print("\n=== 航班查询测试 ===")
    flights = search_flights("北京", "武汉")
    for flight in flights:
        print(f"{flight['flight_no']} ({flight['airline']}): {flight['departure_time']} -> {flight['arrival_time']}, ¥{flight['price']}")
