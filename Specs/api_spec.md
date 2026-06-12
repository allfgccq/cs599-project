# TravAgent 旅行助手 - API 规格文档

## 一、自定义工具定义

### 工具列表

| 工具名称 | 功能描述 |
|---------|---------|
| `get_route_info` | 获取两地间路线信息（步行/驾车距离与时间） |
| `get_weather_info` | 获取目的地天气信息 |
| `search_attractions` | 搜索目的地景点 |
| `search_restaurants` | 搜索当地美食餐厅 |
| `calculate_cost` | 计算行程费用 |

---

## 二、工具输入输出规范

### 1. get_route_info - 获取路线信息

**输入格式：**
```json
{
    "origin": "string",      // 出发地点
    "destination": "string", // 目的地点
    "transport_type": "string" // 交通方式: "driving" | "walking" | "transit"
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "origin": "string",           // 出发地点
        "destination": "string",      // 目的地点
        "transport_type": "string",   // 交通方式
        "distance": "string",         // 距离描述 (如 "50公里")
        "distance_meters": number,    // 距离(米)
        "duration": "string",         // 时间描述 (如 "1小时30分钟")
        "duration_seconds": number,   // 时间(秒)
        "route_summary": "string"     // 路线摘要
    },
    "error": null
}
```

---

### 2. get_weather_info - 获取天气信息

**输入格式：**
```json
{
    "city": "string",        // 城市名称
    "date": "string"         // 查询日期 (YYYY-MM-DD)
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "city": "string",           // 城市名称
        "date": "string",           // 查询日期
        "weather": "string",        // 天气状况 (如 "晴", "多云", "雨")
        "temperature": "string",    // 温度范围 (如 "20-30°C")
        "high_temp": number,        // 最高温度
        "low_temp": number,         // 最低温度
        "wind": "string",           // 风力风向
        "humidity": number,         // 湿度百分比
        "tips": "string"            // 出行建议
    },
    "error": null
}
```

---

### 3. search_attractions - 搜索景点

**输入格式：**
```json
{
    "city": "string",        // 城市名称
    "keywords": "string",    // 搜索关键词 (可选)
    "category": "string",    // 景点类型: "all" | "natural" | "cultural" | "entertainment"
    "page_size": number      // 返回数量
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "city": "string",
        "attractions": [
            {
                "id": "string",          // 景点ID
                "name": "string",        // 景点名称
                "address": "string",     // 地址
                "category": "string",    // 类型
                "rating": number,        // 评分 (1-5)
                "price": number,         // 门票价格 (元)
                "opening_hours": "string", // 开放时间
                "description": "string", // 简介
                "image_url": "string"    // 图片URL
            }
        ]
    },
    "error": null
}
```

---

### 4. search_restaurants - 搜索餐厅

**输入格式：**
```json
{
    "city": "string",        // 城市名称
    "keywords": "string",    // 搜索关键词 (可选)
    "cuisine": "string",     // 菜系: "all" | "local" | "chinese" | "western"
    "price_range": "string", // 价格区间: "all" | "budget" | "mid" | "luxury"
    "page_size": number      // 返回数量
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "city": "string",
        "restaurants": [
            {
                "id": "string",          // 餐厅ID
                "name": "string",        // 餐厅名称
                "address": "string",     // 地址
                "cuisine": "string",     // 菜系
                "rating": number,        // 评分 (1-5)
                "price_per_person": number, // 人均消费
                "opening_hours": "string", // 营业时间
                "recommendations": "string", // 推荐菜品
                "image_url": "string"    // 图片URL
            }
        ]
    },
    "error": null
}
```

---

### 5. calculate_cost - 计算费用

**输入格式：**
```json
{
    "transport_cost": number,    // 交通费用
    "accommodation_cost": number, // 住宿费用
    "attraction_cost": number,    // 景点门票费用
    "food_cost": number,          // 餐饮费用
    "shopping_cost": number,      // 购物费用
    "other_cost": number          // 其他费用
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "breakdown": {
            "transport": number,    // 交通费用
            "accommodation": number, // 住宿费用
            "attractions": number,   // 景点门票费用
            "food": number,          // 餐饮费用
            "shopping": number,      // 购物费用
            "other": number          // 其他费用
        },
        "total_cost": number,       // 总费用
        "currency": "string",       // 货币类型 ("CNY")
        "budget_status": "string",  // 预算状态: "under" | "normal" | "over"
        "budget_ratio": number,     // 费用/预算比例
        "warning": "string"         // 警告信息 (如超预算时)
    },
    "error": null
}
```

---

## 三、MCP 协议接口

### 1. load_long_term_memory - 加载长期记忆

**输入格式：**
```json
{
    "user_id": "string"      // 用户标识
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "user_id": "string",
        "preferences": {
            "interests": ["string"],          // 兴趣点
            "avoid_places": ["string"],       // 黑名单景点
            "dietary_restrictions": ["string"] // 饮食限制
        },
        "history": [
            {
                "timestamp": "string",        // 时间戳
                "destination": "string",      // 目的地
                "rating": number              // 用户评分
            }
        ]
    },
    "error": null
}
```

### 2. save_long_term_memory - 保存长期记忆

**输入格式：**
```json
{
    "user_id": "string",
    "preferences": {
        "interests": ["string"],
        "avoid_places": ["string"],
        "dietary_restrictions": ["string"]
    },
    "new_trip": {
        "destination": "string",
        "rating": number
    }
}
```

**输出格式：**
```json
{
    "success": true,
    "data": {
        "message": "string"
    },
    "error": null
}
```

---

## 四、错误响应格式

所有工具的错误响应统一格式：

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "string",    // 错误码
        "message": "string", // 错误信息
        "details": "string"  // 详细信息 (可选)
    }
}
```

### 错误码列表

| 错误码 | 描述 |
|-------|------|
| `INVALID_INPUT` | 输入参数无效 |
| `API_ERROR` | 外部API调用失败 |
| `NETWORK_ERROR` | 网络连接错误 |
| `NOT_FOUND` | 未找到相关数据 |
| `RATE_LIMIT` | 请求频率超限 |