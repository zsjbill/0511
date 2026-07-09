# AI-CSM-2026 实现设计方案

**日期**: 2026-07-09
**状态**: 待实现

---

## 1. 项目范围

两个独立子模块，使用不同 MySQL 数据库：

| 模块 | 数据库 | 表数量 |
|------|--------|--------|
| 企业智能助手 | `enterprise_assistant` | 4 张（已建） |
| 学生智能助手 | `student_assistant` | 4 张（已建）+ 3 张（新建） |

### 技术栈

- **Web框架**: FastAPI
- **数据库**: 仅本地 MySQL 8.0（无向量数据库、无 Redis）
- **LLM**: 通义千问 qwen-plus，DashScope 兼容端点
- **消息通知**: 前端轮询（5秒/30秒），站内信表持久化
- **定时任务**: APScheduler

### LLM 配置

```env
LLM_PROVIDER=qwen
LLM_API_KEY=sk-ws-H.EMIPLRL.G3GE.MEQCIAzvTiL5X-bLJqefJd89j-RxO1f_beqzpODrvjQLLXvYAiBd0O4XSY7ga_hkD6PL0rRdZzB5Ya5pvDbsRdREOqmlpA
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

---

## 2. 数据库设计

### 2.1 双数据库连接

`src/common/database.py` 改为双引擎架构：

- `enterprise_async_engine` → `enterprise_assistant` 库
- `student_async_engine` → `student_assistant` 库
- 各自 `AsyncSessionLocal` + `get_db` 依赖注入

### 2.2 已有表结构（8张，只做 ORM 映射）

#### enterprise_assistant 库（4张）

**intent_customers**（意向客户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| customer_name | varchar(50) NOT NULL | 客户姓名，索引 |
| age | tinyint | 年龄 |
| gender | varchar(10) | 性别 |
| education | varchar(50) | 学历 |
| major | varchar(100) | 专业 |
| follow_up_record | text | 跟进记录 |
| status | varchar(20) NOT NULL | 状态，默认"跟进中"，索引 |
| created_at | datetime NOT NULL | 创建时间，索引 |
| updated_at | datetime NOT NULL | 更新时间 |

**employee_daily_reports**（员工日报表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| employee_id | varchar(50) NOT NULL | 员工ID，索引 |
| employee_name | varchar(50) NOT NULL | 员工姓名，索引 |
| gender | varchar(10) | 性别 |
| report_content | text NOT NULL | 汇报内容 |
| submitted_at | datetime NOT NULL | 提交时间，索引，默认CURRENT_TIMESTAMP |
| department | varchar(100) | 所属部门，索引 |
| created_at | datetime NOT NULL | 创建时间 |

**complaint_feedback**（投诉反馈表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| student_id | varchar(50) NOT NULL | 学生ID，索引 |
| student_name | varchar(50) NOT NULL | 学生姓名，索引 |
| complaint_detail | text NOT NULL | 投诉详情 |
| status | varchar(20) NOT NULL | 状态，默认"跟进中"，索引 |
| follower | varchar(50) | 跟进人，索引 |
| created_at | datetime NOT NULL | 创建时间，索引 |
| updated_at | datetime NOT NULL | 更新时间 |

**student_scores**（学生成绩表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| student_id | varchar(50) NOT NULL | 学生ID，索引 |
| student_name | varchar(50) NOT NULL | 学生姓名，索引 |
| ielts_score | decimal(5,2) | 雅思成绩，索引 |
| major_course_score | decimal(5,2) | 专业课程成绩 |
| lab_score | decimal(5,2) | 实验成绩 |
| created_at | datetime NOT NULL | 创建时间 |
| updated_at | datetime NOT NULL | 更新时间 |

#### student_assistant 库（4张）

**student_admin_services**（学生行政服务表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| student_id | varchar(50) NOT NULL | 学生ID，索引 |
| student_name | varchar(50) NOT NULL | 学生姓名 |
| application_type | varchar(50) NOT NULL | 申请类型（请假/考务），索引 |
| application_content | text NOT NULL | 申请内容 |
| approval_status | varchar(20) NOT NULL | 审批状态，默认"待审批"，索引 |
| academic_related_data | json | 教务关联数据 |
| approver | varchar(50) | 审批人 |
| approved_at | datetime | 审批时间 |
| created_at | datetime NOT NULL | 创建时间，索引 |
| updated_at | datetime NOT NULL | 更新时间 |

**mental_health_profiles**（心理健康画像表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| student_id | varchar(50) NOT NULL | 学生ID，索引 |
| student_name | varchar(50) NOT NULL | 学生姓名 |
| emotion_tags | json | 情绪标签 |
| emotion_score | decimal(5,2) | 情绪评分，索引 |
| historical_fluctuation | json | 历史波动记录 |
| last_assessed_at | datetime | 最近评估时间，索引 |
| created_at | datetime NOT NULL | 创建时间 |
| updated_at | datetime NOT NULL | 更新时间 |

**psychological_alerts**（心理预警表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| student_id | varchar(50) NOT NULL | 学生ID，索引 |
| student_name | varchar(50) NOT NULL | 学生姓名 |
| trigger_reason | text NOT NULL | 触发原因 |
| risk_level | varchar(20) NOT NULL | 风险等级（高/中/低），索引 |
| teacher_follow_up_status | varchar(20) NOT NULL | 老师跟进状态，索引 |
| follower | varchar(50) | 跟进人，索引 |
| followed_at | datetime | 跟进时间 |
| resolved_at | datetime | 解决时间 |
| created_at | datetime NOT NULL | 创建时间，索引 |
| updated_at | datetime NOT NULL | 更新时间 |

**after_sales_tickets**（售后反馈工单表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| ticket_no | varchar(50) UNIQUE NOT NULL | 工单编号 |
| student_id | varchar(50) NOT NULL | 学生ID，索引 |
| student_name | varchar(50) NOT NULL | 学生姓名 |
| complaint_content | text NOT NULL | 投诉内容 |
| processing_progress | varchar(20) NOT NULL | 处理进度，默认"待处理"，索引 |
| handler | varchar(50) | 处理人，索引 |
| final_solution | text | 最终解决方案 |
| resolved_at | datetime | 解决时间 |
| created_at | datetime NOT NULL | 创建时间，索引 |
| updated_at | datetime NOT NULL | 更新时间 |

### 2.3 新建表（3张，须建库DDL）

**notifications**（站内信通知表）— 存于 `student_assistant`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| recipient_id | varchar(50) NOT NULL | 接收人ID |
| recipient_type | varchar(20) NOT NULL | student / teacher |
| type | varchar(30) NOT NULL | new_application / approval_result / risk_alert |
| title | varchar(200) NOT NULL | 通知标题 |
| content | text NOT NULL | 通知内容 |
| is_read | tinyint NOT NULL DEFAULT 0 | 0未读 / 1已读 |
| related_id | int | 关联的申请单/预警ID |
| created_at | datetime NOT NULL | 创建时间 |
| INDEX idx_recipient_read (recipient_id, recipient_type, is_read) |

**sync_logs**（同步日志表）— 存于 `student_assistant`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| sync_type | varchar(30) NOT NULL | campus_ddl / crm_progress |
| status | varchar(20) NOT NULL | running / success / failed |
| records_count | int DEFAULT 0 | 同步记录数 |
| error_message | text | 失败原因 |
| started_at | datetime NOT NULL | 开始时间 |
| finished_at | datetime | 结束时间 |
| INDEX idx_type_time (sync_type, started_at) |

**kb_documents**（知识库文档表）— 存于 `student_assistant`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK AUTO_INCREMENT | 主键 |
| title | varchar(255) NOT NULL | 文档标题 |
| content | text NOT NULL | 文档正文 |
| category | varchar(50) | 分类（海外生活/升学指导/政策法规） |
| source_file | varchar(255) | 来源文件名 |
| created_at | datetime NOT NULL | 导入时间 |
| FULLTEXT INDEX ft_content (title, content) | | 全文索引 |

---

## 3. 公共层设计

### 3.1 通用 CRUD 基类

`src/common/crud_base.py` — 消除所有 CRUD 重复代码：

```python
class CRUDBase:
    def __init__(self, model, schema_create, schema_update):
        ...
    async def create(self, db, data) -> Model
    async def get(self, db, id) -> Model | None
    async def list(self, db, *, page, page_size, **filters) -> dict  # 分页+筛选
    async def update(self, db, id, data) -> Model
    async def delete(self, db, id) -> bool
```

`list()` 方法核心逻辑：
- filters kwargs 自动转为 `WHERE column = value`
- 特殊后缀 `__like` → LIKE 模糊匹配
- 特殊后缀 `__gte`/`__lte` → 范围查询
- 特殊后缀 `__range` → start_date/end_date 时间范围

### 3.2 统一响应格式

所有接口返回：
```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": "2026-07-09T12:00:00"
}
```

分页数据包裹：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "..."
}
```

---

## 4. 企业智能助手（enterprise）

### 4.1 CRUD 接口（5端点 × 4表）

所有路由挂载在 `/api/v1/enterprise/` 下：

| 表 | 路由前缀 | 独有查询参数 |
|------|---------|-------------|
| intent_customers | `/customers` | customer_name, status, start_date, end_date |
| employee_daily_reports | `/reports` | department, employee_name, start_date, end_date |
| complaint_feedback | `/complaints` | status, follower |
| student_scores | `/scores` | student_id, student_name, min_score, max_score |

每个前缀提供：
```
GET    /api/v1/enterprise/{prefix}         # 列表+筛选+分页
GET    /api/v1/enterprise/{prefix}/{id}    # 详情
POST   /api/v1/enterprise/{prefix}         # 新增
PUT    /api/v1/enterprise/{prefix}/{id}    # 更新
DELETE /api/v1/enterprise/{prefix}/{id}    # 删除
```

### 4.2 NL2SQL 引擎

```
POST /api/v1/enterprise/nl2sql/query
  请求: { "query": "帮我查一下张三的最近跟进记录" }
  响应: { "sql": "SELECT ...", "result": [...], "explanation": "..." }
```

**安全约束（硬性）**：
1. 仅允许 SELECT 语句
2. 仅限 enterprise_assistant 库 4 张表
3. 拦截关键词：DELETE、UPDATE、DROP、ALTER、TRUNCATE、INSERT、CREATE
4. SQL 执行前 sqlparse 语法校验

**Prompt 策略**：将 4 张表的完整 DDL 嵌入 system prompt，加 few-shot 示例引导。

### 4.3 智能主动推送

```
GET  /api/v1/enterprise/tasks/pending       # 教师端轮询（30秒）
POST /api/v1/enterprise/tasks/{task_id}/ack  # 确认已读
```

后台 APScheduler（每分钟）：扫描 `complaint_feedback.status != '已跟进'` 生成待办。

### 4.4 指令式业务处理

```
POST /api/v1/enterprise/instruction/execute
  请求: { "instruction": "把李四的投诉状态更新为已跟进" }
  响应: { "parsed": {...}, "action": "update", "result": "操作成功" }
```

LLM 解析指令 → 提取（操作对象、动作、目标值）→ 调用对应 CRUD 方法。

---

## 5. 学生智能助手（student）

### 5.1 CRUD 接口（5端点 × 4表）

所有路由挂载在 `/api/v1/student/` 下：

| 表 | 路由前缀 | 独有查询参数 |
|------|---------|-------------|
| student_admin_services | `/admin-services` | student_id, application_type, approval_status |
| mental_health_profiles | `/mental-health` | student_id, start_date, end_date |
| psychological_alerts | `/alerts` | risk_level, teacher_follow_up_status, follower |
| after_sales_tickets | `/tickets` | processing_progress, student_id, ticket_no |

### 5.2 审批闭环

```
POST   /api/v1/student/application/submit         # 学生提交
POST   /api/v1/student/application/approve        # 老师审批（通过/驳回/转交）
GET    /api/v1/student/application/{id}/status    # 查询状态
GET    /api/v1/student/notifications/pending      # 待审批轮询（5秒）
```

**审批状态流转**：待审批 → 已通过 / 已驳回 / 已转交

**通知机制**：
- 学生提交后 → 写入 notifications 表（type=new_application，recipient=老师端）
- 老师审批后 → 写入 notifications 表（type=approval_result，recipient=学生端）
- 前端轮询 `GET /notifications/pending` 按 recipient_id + type 过滤未读消息

### 5.3 系统对接同步

```
POST /api/v1/student/sync/campus/ddl        # 手动触发教务DDL同步
POST /api/v1/student/sync/crm/progress      # 手动触发CRM进度同步
GET  /api/v1/student/sync/status            # 查询最近同步状态
```

APScheduler 每小时自动执行一次。同步结果写入 sync_logs 表。

### 5.4 知识库检索（MySQL FULLTEXT）

```
POST /api/v1/student/kb/search
  请求: { "query": "澳洲租房注意事项", "top_k": 5 }
  响应: { "results": [{ "title", "content_snippet", "score" }] }
```

实现：`MATCH(title, content) AGAINST(:query IN NATURAL LANGUAGE MODE) WITH QUERY EXPANSION`

配合 jieba 分词预处理中文查询。文档导入脚本 `scripts/import_kb.py` 复用已有 `file_parser.py`。

### 5.5 AI 能力

```
POST /api/v1/student/ai/risk-detect    # 情绪分析，高危→写预警表+通知
POST /api/v1/student/ai/summarize      # 投诉摘要（200字→100字）
POST /api/v1/student/ai/marketing      # 营销话术（保守/稳健/激进）
```

**风险识别链**：分析文本 → 返回风险等级 → 高危则写 psychological_alerts + notifications

---

## 6. 模型选择

各任务使用的 LLM 模型：

| 任务 | 模型 | 理由 |
|------|------|------|
| NL2SQL | qwen-plus | SQL语法需要较高精度，turbo不够稳 |
| 指令解析 | qwen-plus | 结构化提取需要稳定性 |
| 风险识别 | qwen-plus | 情绪理解需要细节 |
| 智能摘要 | qwen-turbo | 标准摘要任务，turbo足够 |
| 营销话术 | qwen-turbo | 模板化生成，turbo足够 |
| 意图识别 | qwen-turbo | 简单分类任务 |

> 代码通过环境变量 `LLM_MODEL` 统一控制，可随时切换。未来如果需要分任务指定不同模型，可在 llm_client 增加 model 参数。

---

## 7. 文件结构总览

```
src/
├── common/
│   ├── database.py              # 【改】双引擎：enterprise + student
│   ├── models_enterprise.py     # 【新】企业助手4表 ORM
│   ├── models_student.py        # 【新】学生助手7表 ORM（4已有+3新建）
│   ├── schemas_enterprise.py    # 【新】企业助手 Pydantic
│   ├── schemas_student.py       # 【新】学生助手 Pydantic
│   ├── crud_base.py             # 【新】通用CRUD基类
│   ├── llm_client.py            # 【改】通义千问配置
│   └── ...                      # file_parser, nlp_tools, utils 不变
│
├── module_enterprise/
│   ├── __init__.py
│   ├── api_crud.py              # 4表 CRUD 路由
│   ├── api_nl2sql.py            # NL2SQL 路由
│   ├── api_tasks.py             # 待办推送 + 指令处理 路由
│   ├── nl2sql_engine.py         # NL2SQL 核心（安全校验+调用+执行）
│   ├── instruction_handler.py   # 指令解析与路由执行
│   ├── task_scanner.py          # APScheduler 定时扫描待办
│   └── tests/
│       └── test_nl2sql.py
│
├── module_student/
│   ├── __init__.py
│   ├── api_crud.py              # 4表 CRUD 路由
│   ├── api_application.py       # 审批闭环路由
│   ├── api_sync.py              # 系统对接同步路由
│   ├── api_kb.py                # 知识库检索路由
│   ├── api_ai.py                # AI 能力路由
│   ├── approval_service.py      # 审批业务逻辑
│   ├── sync_service.py          # 同步服务 + 定时任务
│   ├── kb_service.py            # 全文检索逻辑
│   ├── notification_service.py  # 站内信通知
│   ├── risk_monitor.py          # 风险识别 + 预警写入
│   ├── summarizer.py            # 投诉摘要
│   ├── marketing.py             # 营销话术生成
│   └── tests/
│       ├── test_approval.py
│       └── test_kb.py
│
├── main.py                      # 【改】注册 enterprise + student 路由
│
├── scripts/
│   ├── init_notifications.sql   # 【新】建 notifications 表
│   ├── init_sync_logs.sql       # 【新】建 sync_logs 表
│   ├── init_kb_documents.sql    # 【新】建 kb_documents 表
│   ├── import_kb.py             # 【新】知识库文档导入脚本
│   └── ...                      # 已有脚本保留
│
└── tests/
    ├── test_e2e_approval.py     # 【新】审批闭环 E2E
    └── ...                      # 已有测试保留
```

---

## 8. 验收标准

| 交付物 | 标准 |
|--------|------|
| 8表 CRUD | Swagger 可调试，所有字段覆盖，分页筛选正常 |
| NL2SQL | 20 条测试用例通过率 ≥ 80%（≥16条） |
| 审批闭环 | 提交→审批→通知 全链路可跑通 |
| 同步接口 | 手动触发写入 sync_logs，定时任务正常运行 |
| 知识库检索 | 输入查询返回相关文档片段 |
| 单元测试 | 核心模块测试覆盖率 ≥ 80% |
| 项目启动 | `uvicorn src.main:app --reload` 无报错 |
