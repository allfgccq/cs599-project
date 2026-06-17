# TravAgent - 智能旅行助手

基于大语言模型的智能旅行规划助手，支持多智能体协作、记忆机制和动态行程规划。

## ✨ 功能特性

- 🗺️ **智能行程规划**：根据用户预算、时间和偏好生成个性化旅行方案
- 🍽️ **美食推荐**：智能推荐当地特色餐厅，避免重复
- 📍 **地图生成**：生成带路线的旅行地图
- 🚀 **交通方案**：多种交通方式推荐
- 🏨 **酒店预订**：根据预算推荐合适酒店
- 🤝 **多智能体协作**：旅行总管、精算师、特约导游、美食助手协同工作
- 🧠 **双轨记忆系统**：短期记忆保持对话上下文，长期记忆存储用户偏好

## 🛠️ 技术栈

- Python 3.9+
- Chainlit - Web UI框架
- LangGraph - 状态机管理
- LangChain - LLM集成
- FAISS - 向量数据库
- 高德地图API - 路线查询
- 和风天气API - 天气查询

## 📁 项目结构

```
cs599-project/
├── docs/                    # 项目文档
│   ├── CS599_大作业报告.pdf   # 最终提交的报告（PDF）
│   └── architecture.md       # 详细架构说明（可选）
├── src/                      # 项目源代码
│   ├── agents/               # 智能体模块
│   ├── tools/                # 工具模块
│   ├── graph/                # 状态图管理
│   ├── memory/               # 记忆系统
│   ├── utils/                # 工具函数
│   └── app.py                # 主应用入口
├── README.md                 # 项目入口，必填
├── .gitignore                # 排除编译文件
├── requirements.txt          # 依赖清单
└── LICENSE                   # 开源协议（Public Repository 必填）
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件并填写API密钥：

```bash
# 高德地图API
AMAP_KEY=your_amap_key

# 和风天气API
WEATHER_KEY=your_weather_key

# OpenAI API
OPENAI_API_KEY=your_openai_key
```

### 运行项目

```bash
chainlit run src/app.py
```

## 📝 课程信息

**课程**: 企业级应用软件设计与开发  
**项目**: 智能旅行助手 (TravAgent)  
**方向**: 方向一：Agentic AI 原生开发  
**作者**: [吴思涵]  
**学号**: [2025302908]  
**专业**: [计算机技术]  
**指导教师**: 戚欣  
**提交日期**: 2026年6月22日

## 📄 许可证

pache-2.0 license
