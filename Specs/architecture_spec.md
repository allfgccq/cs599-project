# TravAgent 旅行助手 - 架构规格文档

## 一、LangGraph State 数据结构定义

### 核心状态节点

```python
class TravelState(TypedDict):
    # 基础信息
    user_input: str                    # 用户原始输入
    session_id: str                    # 会话ID
    timestamp: float                   # 时间戳
    
    # 行程基础参数
    origin: str                        # 出发地
    destination: str                   # 目的地
    start_date: str                    # 出发日期 (YYYY-MM-DD)
    end_date: str                      # 返回日期 (YYYY-MM-DD)
    budget: float                      # 预算金额 (元)
    travel_days: int                   # 旅行天数
    
    # 偏好设置
    preferences: dict                  # 用户偏好 { "transport": "高铁", "accommodation": "舒适型" }
    interests: list                    # 兴趣点 ["历史文化", "美食", "自然风光"]
    avoid_places: list                 # 黑名单景点
    dietary_restrictions: list         # 饮食限制/过敏原
    
    # 行程数据
    itinerary: dict                    # 当前行程方案
    itinerary_history: list            # 历史行程版本（用于回滚）
    current_version: int               # 当前版本号
    
    # 外部数据
    weather_info: dict                 # 天气信息
    route_info: dict                   # 路线信息
    attractions: list                  # 景点列表
    restaurants: list                  # 餐厅推荐
    
    # 预算相关
    estimated_cost: float              # 预估总费用
    budget_status: str                 # 预算状态 ("under", "normal", "over")
    budget_warning: str                # 预算警告信息
    
    # 状态标志
    is_conflict: bool                  # 是否存在冲突
    conflict_details: list             # 冲突详情
    processing_step: str               # 当前处理步骤
    agent_info: dict                   # 各Agent处理信息
    
    # 记忆相关
    short_term_memory: dict            # 短期记忆（对话上下文）
    long_term_memory: dict             # 长期记忆（用户历史偏好）
```

## 二、状态转移条件

### 节点定义

| 节点名称 | 功能描述 |
|---------|---------|
| `Requirement_Parser` | 解析用户需求，提取关键参数 |
| `Search_Agent` | 调用地图/天气/景点工具收集信息 |
| `Itinerary_Generator` | 生成初版行程 |
| `Conflict_Validator` | 冲突检测专家 |
| `Fix_Node` | 自动修复节点 |
| `User_Review` | 用户确认环节 |

### 状态转移流程

```
Requirement_Parser -> Search_Agent -> Itinerary_Generator -> Conflict_Validator
                                                              |
                    ┌─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
    检测到冲突              无冲突
        │                       │
        ▼                       ▼
    Fix_Node            User_Review
        │                       │
        └───────────┬───────────┘
                    ▼
            结束/继续优化
```

### 转移条件详解

#### 1. Requirement_Parser → Search_Agent
**条件**：用户需求解析完成，关键参数（出发地、目的地、日期、预算）已提取

#### 2. Search_Agent → Itinerary_Generator
**条件**：所有外部数据（天气、路线、景点、餐厅）收集完成

#### 3. Itinerary_Generator → Conflict_Validator
**条件**：初版行程生成完成

#### 4. Conflict_Validator → Fix_Node
**条件**：检测到时间冲突或预算超支
```python
# 时间冲突检测
def has_time_conflict(state):
    # 检查相邻景点之间的交通时间是否足够
    for i in range(len(itinerary) - 1):
        current_end_time = itinerary[i]['end_time']
        next_start_time = itinerary[i+1]['start_time']
        travel_time = calculate_travel_time(itinerary[i]['location'], itinerary[i+1]['location'])
        if current_end_time + travel_time > next_start_time:
            return True
    return False

# 预算超支检测
def is_budget_over(state):
    return state['estimated_cost'] > state['budget'] * 1.15  # 超过15%
```

#### 5. Conflict_Validator → User_Review
**条件**：无时间冲突且预算在合理范围内

#### 6. Fix_Node → Conflict_Validator
**条件**：冲突修复完成，需要重新验证

#### 7. User_Review → 结束/继续
**条件**：用户确认或提出修改意见

## 三、多智能体架构

### 智能体职责分配

```
┌─────────────────────────────────────────────────────────────┐
│                    TravAgent 旅行助手                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌───────────┐  │
│   │  旅行总管    │────▶│  精算师      │     │ 特约导游  │  │
│   │ Router Agent │     │ Budget Agent │     │Content    │  │
│   │              │◀────│              │     │   Agent   │  │
│   └──────────────┘     └──────────────┘     └─────┬─────┘  │
│          │                                          │       │
│          ▼                                          ▼       │
│   ┌──────────────┐                         ┌───────────┐    │
│   │   用户交互   │                         │   RAG     │    │
│   │              │                         │ 知识库    │    │
│   └──────────────┘                         └───────────┘    │
│                                                             │
│   ┌──────────────┐     ┌──────────────┐                     │
│   │   美食助手   │     │   记忆系统   │                     │
│   │ Food Agent   │     │ Memory Sys   │                     │
│   └──────────────┘     └──────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 智能体交互协议

| 智能体 | 输入 | 输出 |
|-------|------|------|
| 旅行总管 | 用户自然语言输入 | 结构化需求参数 |
| 精算师 | 行程方案、预算 | 费用估算、预算状态 |
| 特约导游 | 景点列表 | 景点深度攻略 |
| 美食助手 | 目的地、日期 | 餐厅推荐 |

## 四、记忆机制架构

### 短期记忆（MemorySaver）
- 使用 LangGraph MemorySaver 存储对话历史
- 支持状态回滚（回滚到上一步行程）
- 生命周期：当前会话

### 长期记忆（向量数据库）
- 存储用户历史对话特征
- 存储黑名单景点
- 存储饮食限制/过敏原
- 通过 MCP 协议动态拉取

### MCP Memory Server 封装
- 提供标准 MCP 接口
- 支持 Resources 机制注入上下文
- 实现大模型无感调用长期记忆