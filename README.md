# AI-CSM-2026
# 智能客服与学生管理系统

## 项目简介
AI-CSM-2026 是一个基于大语言模型的智能客服与学生管理系统，覆盖从客户获取到售后服务的全链路业务场景。

## 模块架构

| 模块 | 名称 | 功能 |
|------|------|------|
| M1 | 客户研判 | 客户画像匹配、打分、服务推荐 |
| M2 | 客服Agent | 7大意图路由、RAG问答、活动报名 |
| M3 | 企业智能助手 | NL2SQL、语音处理、指令执行、待办推送 |
| M4 | 学生智能助手 | 请假审批、心理风险识别、投诉摘要、营销生成 |
| M5 | 智能报告 | 日报/周报/月报自动生成与定时推送 |

## 快速开始

### 1. 环境准备
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置
```bash
cp .env.example .env
# 编辑 .env 填入实际的数据库连接和 API Key
```

### 3. 初始化数据库
```bash
python scripts/init_db.py
python scripts/seed_test_data.py
```

### 4. 导入知识库
```bash
python scripts/vectorize_knowledge.py
python scripts/import_faq.py
```

### 5. 启动服务
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问
- API 文档: http://localhost:8000/docs
- 测试对话页面: http://localhost:8000/

## 技术栈
- **框架**: FastAPI
- **数据库**: MySQL + SQLAlchemy (async)
- **LLM**: OpenAI / 通义千问 / 智谱 (统一接口)
- **向量库**: Chroma / FAISS / Pinecone
- **前端**: 原生 HTML/JS (可替换为 React/Vue)

## 项目结构
参见项目目录树（`tree` 命令输出）。

## API Documentation

### Enterprise Assistant (`/api/v1/enterprise`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/customers` | Intent customers CRUD |
| GET/PUT/DELETE | `/customers/{id}` | Customer detail/update/delete |
| GET/POST | `/reports` | Employee daily reports CRUD |
| GET/PUT/DELETE | `/reports/{id}` | Report detail/update/delete |
| GET/POST | `/complaints` | Complaint feedback CRUD |
| GET/PUT/DELETE | `/complaints/{id}` | Complaint detail/update/delete |
| GET/POST | `/scores` | Student scores CRUD |
| GET/PUT/DELETE | `/scores/{id}` | Score detail/update/delete |
| POST | `/nl2sql/query` | Natural language to SQL |
| GET | `/tasks/pending` | Pending task polling |
| POST | `/tasks/scan` | Trigger task scan |
| POST | `/instruction/execute` | Natural language instruction |

### Student Assistant (`/api/v1/student`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/admin-services` | Admin services CRUD |
| GET/PUT/DELETE | `/admin-services/{id}` | Service detail/update/delete |
| GET/POST | `/mental-health` | Mental health profiles CRUD |
| GET/PUT/DELETE | `/mental-health/{id}` | Profile detail/update/delete |
| GET/POST | `/alerts` | Psychological alerts CRUD |
| GET/PUT/DELETE | `/alerts/{id}` | Alert detail/update/delete |
| GET/POST | `/tickets` | After-sales tickets CRUD |
| GET/PUT/DELETE | `/tickets/{id}` | Ticket detail/update/delete |
| POST | `/application/submit` | Submit application |
| POST | `/application/approve` | Approve/reject/transfer |
| GET | `/application/{id}/status` | Application status |
| GET | `/notifications/pending` | Poll pending notifications |
| POST | `/sync/campus/ddl` | Sync campus DDL |
| POST | `/sync/crm/progress` | Sync CRM progress |
| GET | `/sync/status` | Sync status |
| POST | `/kb/search` | Knowledge base search |
| POST | `/ai/risk-detect` | Risk detection |
| POST | `/ai/summarize` | Complaint summarization |
| POST | `/ai/marketing` | Marketing copy generation |

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create new tables
mysql -uroot -p123456 < scripts/init_new_tables.sql

# Import knowledge base (optional)
python scripts/import_kb.py

# Start server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
open http://localhost:8000/docs
```

## License
MIT
