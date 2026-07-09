# AI-CSM-2026 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement dual-module FastAPI backend (enterprise + student) with 8-table CRUD, NL2SQL engine, approval workflow, system sync, MySQL FULLTEXT knowledge base, and 3 AI capabilities.

**Architecture:** Two independent FastAPI router groups backed by separate MySQL databases. Shared common layer (dual DB engines, CRUD base class, LLM client configured for Qwen qwen-plus).

**Tech Stack:** FastAPI, SQLAlchemy 2.0 async, MySQL 8.0, Qwen (DashScope compatible), APScheduler, jieba, pytest

## Global Constraints

- Framework: FastAPI
- DB: MySQL 8.0 only (no Redis/VectorDB/message queue)
- LLM: Qwen qwen-plus, base_url=https://dashscope.aliyuncs.com/compatible-mode/v1
- API Key: sk-ws-H.EMIPLRL.G3GE.MEQCIAzvTiL5X-bLJqefJd89j-RxO1f_beqzpODrvjQLLXvYAiBd0O4XSY7ga_hkD6PL0rRdZzB5Ya5pvDbsRdREOqmlpA
- Notification: in-app message table + frontend polling (5s student, 30s teacher)
- Response format: { code, message, data, timestamp }
- Pagination: page(default=1), page_size(default=20)
- MySQL credentials: root / 123456

---

## Implementation Tasks

**23 tasks organized in 7 phases.** Each task has concrete steps with exact file paths, code snippets, and verification commands. Tasks are independently testable and commit-worthy.

Projects files: ~30 new, 4 modified.
Key modules: src/common/ (database, models_enterprise, models_student, schemas_enterprise, schemas_student, crud_base), src/module_enterprise/ (api_crud, api_nl2sql, api_tasks, nl2sql_engine, task_scanner, instruction_handler), src/module_student/ (api_crud, api_application, api_sync, api_kb, api_ai, approval_service, sync_service, kb_service, notification_service, risk_monitor, summarizer, marketing)

---

## Phase 1: Foundation

### Task 1: Environment config

**Files:** Modify `.env`, `config/settings.py`
**Produces:** Qwen LLM defaults + dual DB URLs

- [ ] Update `.env` LLM section to: LLM_PROVIDER=qwen, LLM_API_KEY=sk-ws-H.EMIPLRL..., LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1, LLM_MODEL=qwen-plus, ENTERPRISE_DB_URL=mysql+aiomysql://root:123456@localhost:3306/enterprise_assistant, STUDENT_DB_URL=mysql+aiomysql://root:123456@localhost:3306/student_assistant
- [ ] Add to `config/settings.py` Settings class: ENTERPRISE_DB_URL and STUDENT_DB_URL properties (os.getenv with defaults)
- [ ] Verify: `python -c "from config.settings import settings; print(settings.LLM_MODEL)"` outputs `qwen-plus`
- [ ] Commit: `git commit -m "feat: configure Qwen LLM and dual database URLs"`

### Task 2: Create 3 new tables

**Files:** Create `scripts/init_new_tables.sql`
**Produces:** notifications, sync_logs, kb_documents in student_assistant

- [ ] Write SQL DDL (see spec section 2.3 for full column definitions): notifications (recipient_id, recipient_type, type, title, content, is_read, related_id, created_at), sync_logs (sync_type, status, records_count, error_message, started_at, finished_at), kb_documents (title, content, category, source_file, created_at) with FULLTEXT INDEX ft_content ON (title, content)
- [ ] Execute: `mysql -uroot -p123456 < scripts/init_new_tables.sql`
- [ ] Verify: `mysql -uroot -p123456 -e "USE student_assistant; SHOW TABLES;"` shows 7 total
- [ ] Commit: `git commit -m "feat: add 3 new tables (notifications, sync_logs, kb_documents)"`

### Task 3: Dual database engine

**Files:** Modify `src/common/database.py`
**Produces:** get_enterprise_db(), get_student_db() dependency functions

- [ ] Rewrite database.py: remove single-engine pattern, create enterprise_async_engine and student_async_engine with separate EnterpriseSessionLocal/StudentSessionLocal, two get_db deps, init_db creates tables in both, close_db disposes both
- [ ] Verify: `python -c "from src.common.database import get_enterprise_db, get_student_db; print('OK')"`
- [ ] Commit: `git commit -m "refactor: dual database engine for enterprise and student assistants"`

---

## Phase 2: Models & Schemas

### Task 4: ORM Models (11 tables)

**Files:** Create `src/common/models_enterprise.py`, `src/common/models_student.py`
**Produces:** All ORM model classes mapped to actual DB columns

- [ ] Create models_enterprise.py with 4 classes (IntentCustomer, EmployeeDailyReport, ComplaintFeedback, StudentScore) — map ALL columns from spec section 2.2
- [ ] Create models_student.py with 7 classes (StudentAdminService, MentalHealthProfile, PsychologicalAlert, AfterSalesTicket, Notification, SyncLog, KBDocument) — map ALL columns
- [ ] Verify: python imports succeed without errors
- [ ] Commit: `git commit -m "feat: add ORM models for all 11 tables"`

### Task 5: Pydantic Schemas

**Files:** Create `src/common/schemas_enterprise.py`, `src/common/schemas_student.py`
**Produces:** Create/Update/Response schemas for all tables + API-specific request/response schemas

- [ ] Create schemas_enterprise.py: APIResponse, PaginatedData, IntentCustomer*, EmployeeDailyReport*, ComplaintFeedback*, StudentScore* (Create/Update/Response for each)
- [ ] Create schemas_student.py: APIResponse, PaginatedData, StudentAdminService*, MentalHealthProfile*, PsychologicalAlert*, AfterSalesTicket*, NotificationResponse, SyncLogResponse, ApplicationSubmitRequest, ApplicationApproveRequest, ApplicationStatusResponse, KBSearchRequest, RiskDetectRequest/Response, SummarizeRequest/Response, MarketingGenerateRequest/Response, NL2SQLRequest/Response, InstructionRequest/Response
- [ ] Verify: `python -c "from src.common.schemas_enterprise import *; from src.common.schemas_student import *; print('OK')"`
- [ ] Commit: `git commit -m "feat: add Pydantic schemas for all tables and API endpoints"`

---

## Phase 3: Common + Enterprise CRUD

### Task 6: Generic CRUD Base Class

**Files:** Create `src/common/crud_base.py`
**Produces:** CRUDBase class with create/get/list/update/delete + filter support

- [ ] Implement CRUDBase with: __init__(model, schema_create, schema_update), async create(self, db, data), async get(self, db, id), async list(self, db, *, page, page_size, **filters), async update(self, db, id, data), async delete(self, db, id) -> bool
- [ ] list() filter support: exact match on column names, __like suffix for LIKE %value%, __gte/__lte for range, start_date/end_date for created_at range, min_score/max_score for score column range
- [ ] list() returns: dict with items, total, page, page_size, total_pages
- [ ] Verify: `python -c "from src.common.crud_base import CRUDBase; print('OK')"`
- [ ] Commit: `git commit -m "feat: add generic async CRUD base class with filtering and pagination"`

### Task 7: Enterprise 4-Table CRUD APIs

**Files:** Create `src/module_enterprise/__init__.py`, `src/module_enterprise/api_crud.py`
**Produces:** 20 CRUD endpoints at /api/v1/enterprise/

- [ ] Create module init and api_crud.py with APIRouter(prefix="/api/v1/enterprise")
- [ ] Create CRUDBase instances: customer_crud, report_crud, complaint_crud, score_crud
- [ ] Implement custom list endpoints with table-specific filters:
    - GET /customers: customer_name (LIKE), status, start_date/end_date
    - GET /reports: department, employee_name (LIKE), submitted_at range
    - GET /complaints: status, follower
    - GET /scores: student_id, student_name (LIKE), min_score/max_score
- [ ] Register standard get/post/put/delete for each prefix
- [ ] All responses use APIResponse wrapper with PaginatedData for lists
- [ ] Verify: `python -m src.module_enterprise.api_crud` imports cleanly
- [ ] Commit: `git commit -m "feat: enterprise assistant 4-table CRUD APIs"`

---

## Phase 4: Enterprise Advanced Features

### Task 8: NL2SQL Engine

**Files:** Create `src/module_enterprise/nl2sql_engine.py`, `src/module_enterprise/api_nl2sql.py`
**Produces:** POST /api/v1/enterprise/nl2sql/query

- [ ] Create NL2SQLEngine with: query(natural_query) -> {sql, result, explanation}
- [ ] _generate_sql(): embed 4-table DDL in system prompt, call llm_client.chat(temperature=0.1)
- [ ] _security_check(): reject DELETE/UPDATE/DROP/ALTER/TRUNCATE/INSERT/CREATE, reject non-SELECT, reject tables outside allowed set {intent_customers, employee_daily_reports, complaint_feedback, student_scores}
- [ ] _execute_sql(): run via enterprise_async_engine.connect(), return list of dicts
- [ ] Create api_nl2sql.py with POST /query endpoint, catch ValueError -> 400, Exception -> 500
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: NL2SQL engine with security guard and LLM SQL generation"`

### Task 9: Task Scanner + Pending Tasks

**Files:** Create `src/module_enterprise/task_scanner.py`, `src/module_enterprise/api_tasks.py`
**Produces:** GET /api/v1/enterprise/tasks/pending (teacher polls every 30s)

- [ ] Create task_scanner.py: scan_tasks() queries complaint_feedback WHERE status != '已跟进', stores results in _pending_tasks list; start_scanner() loops every 60s; get_pending_tasks() returns current list
- [ ] Create api_tasks.py: GET /pending returns tasks+count, POST /scan triggers immediate scan, POST /{task_id}/ack marks read
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: enterprise pending task scanner and polling API"`

### Task 10: Instruction Handler

**Files:** Create `src/module_enterprise/instruction_handler.py`; add route to api_tasks.py
**Produces:** POST /api/v1/enterprise/instruction/execute

- [ ] Create instruction_handler.py: execute_instruction() calls LLM to parse instruction -> JSON {target_table, action, identifiers, fields}; route to _handle_complaint_update() or _handle_customer_update(); execute CRUD update via direct DB session
- [ ] LLM prompt constrains to complaint_feedback and intent_customers tables only
- [ ] Add POST /instruction/execute endpoint to api_tasks.py
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: instruction handler for natural language command execution"`

---

## Phase 5: Student Module

### Task 11: Student 4-Table CRUD APIs

**Files:** Create `src/module_student/__init__.py`, `src/module_student/api_crud.py`
**Produces:** 20 CRUD endpoints at /api/v1/student/

- [ ] Create api_crud.py with APIRouter(prefix="/api/v1/student")
- [ ] Create CRUDBase instances: admin_crud, mental_crud, alert_crud, ticket_crud
- [ ] Implement custom list endpoints with table-specific filters:
    - GET /admin-services: student_id, application_type, approval_status
    - GET /mental-health: student_id, start_date/end_date
    - GET /alerts: risk_level, teacher_follow_up_status, follower
    - GET /tickets: processing_progress, student_id, ticket_no
- [ ] Register standard get/post/put/delete for each prefix with APIResponse wrapper
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: student assistant 4-table CRUD APIs"`

### Task 12: Notification Service

**Files:** Create `src/module_student/notification_service.py`
**Produces:** create_notification(), get_pending_notifications(), mark_as_read()

- [ ] Implement create_notification(recipient_id, recipient_type, type, title, content, related_id) -> Notification
- [ ] Implement get_pending_notifications(recipient_id, recipient_type, limit=20) -> list[Notification] (is_read=0)
- [ ] Implement mark_as_read(notification_id) -> bool
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: in-app notification service for approval workflow"`

### Task 13: Approval Workflow

**Files:** Create `src/module_student/approval_service.py`, `src/module_student/api_application.py`
**Produces:** Full approval loop: submit -> approve -> notify -> poll

- [ ] Create approval_service.py: submit_application(data) creates StudentAdminService record + notification (type=new_application, recipient_type=teacher); approve_application(id, action, approver, comment, transfer_to) updates status + creates notifications (approval_result for student, new_application for transfer recipient)
- [ ] Create api_application.py with endpoints:
    - POST /application/submit -> 201 + ApplicationStatusResponse
    - POST /application/approve -> approve + notify
    - GET /application/{id}/status -> current status
    - GET /notifications/pending?recipient_id=X&recipient_type=Y -> unread notifications
    - POST /notifications/{id}/read -> mark as read
- [ ] Verify: import succeeds, approval_service functions are callable
- [ ] Commit: `git commit -m "feat: approval workflow with submit/approve/status/notifications"`

### Task 14: System Sync Service

**Files:** Create `src/module_student/sync_service.py`, `src/module_student/api_sync.py`
**Produces:** Manual + scheduled sync for campus DDL and CRM progress

- [ ] Create sync_service.py: run_sync(sync_type) creates SyncLog, calls external API stub (endpoints TBD by other teams), saves result; get_sync_status() returns last sync state; start_scheduler() runs every 3600s
- [ ] Create api_sync.py: POST /sync/campus/ddl, POST /sync/crm/progress, GET /sync/status
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: system sync service for campus DDL and CRM progress"`

### Task 15: Knowledge Base Search

**Files:** Create `src/module_student/kb_service.py`, `src/module_student/api_kb.py`
**Produces:** POST /api/v1/student/kb/search using MySQL FULLTEXT

- [ ] Create kb_service.py: search_kb(query, top_k=5) uses jieba.cut() for Chinese tokenization, then MATCH(title, content) AGAINST(:q IN NATURAL LANGUAGE MODE) with SUBSTRING(content, 1, 200) as snippet, returns [{title, score, content_snippet}]
- [ ] Create api_kb.py: POST /search endpoint
- [ ] Verify: import succeeds
- [ ] Commit: `git commit -m "feat: MySQL FULLTEXT knowledge base search with jieba tokenization"`

### Task 16: AI Capabilities

**Files:** Create risk_monitor.py, summarizer.py, marketing.py, api_ai.py (all in src/module_student/)
**Produces:** 3 AI endpoints: risk-detect, summarize, marketing

- [ ] Create risk_monitor.py: detect_risk(student_id, student_name, conversation_text) calls LLM with RISK_PROMPT, parses JSON response; if medium/high, writes PsychologicalAlert + creates notification to counselor
- [ ] Create summarizer.py: summarize_complaint(complaint_text) calls LLM, returns {complainant, core_issue, urgency, suggested_handler, summary}
- [ ] Create marketing.py: generate_marketing(student_id, student_name, emotion_tags, scores, study_interest) calls LLM, returns {conservative, moderate, aggressive}
- [ ] Create api_ai.py: POST /risk-detect, POST /summarize, POST /marketing
- [ ] All LLM calls use llm_client.chat() with temperature=0.2-0.7 depending on creativity needed
- [ ] Verify: all imports succeed
- [ ] Commit: `git commit -m "feat: AI capabilities - risk detection, summarization, marketing generation"`

---

## Phase 6: Integration & Scripts

### Task 17: Update main.py

**Files:** Modify `src/main.py`
**Produces:** App with all 8 routers registered, background scanners started

- [ ] Rewrite main.py: register 8 routers (enterprise_crud, enterprise_nl2sql, enterprise_tasks, student_crud, student_approval, student_sync, student_kb, student_ai), start task_scanner and sync_scheduler as asyncio background tasks in lifespan, keep CORS/static/health
- [ ] Test startup: `uvicorn src.main:app --host 127.0.0.1 --port 8000` (verify no import errors)
- [ ] Test health: `curl http://127.0.0.1:8000/health` returns healthy
- [ ] Commit: `git commit -m "feat: integrate all enterprise and student routers into main app"`

### Task 18: KB Import Script

**Files:** Create `scripts/import_kb.py`
**Produces:** Script to parse documents and insert into kb_documents

- [ ] Create import_kb.py: iterates data/knowledge_base/, uses file_parser.parse_file() for PDF/DOCX/TXT, auto-categorizes by filename keywords, inserts KBDocument records
- [ ] Verify: `python scripts/import_kb.py` runs (may report "no files found" if dir empty)
- [ ] Commit: `git commit -m "feat: knowledge base document import script with auto-categorization"`

---

## Phase 7: Testing

### Task 19: NL2SQL Tests (20 cases)

**Files:** Create `src/module_enterprise/tests/__init__.py`, `test_nl2sql.py`
**Produces:** 10 security tests (always pass) + 10 integration tests (require LLM)

- [ ] Security tests (no LLM needed): test_rejects_delete, test_rejects_update, test_rejects_drop, test_rejects_insert, test_rejects_alter, test_allows_select, test_allows_select_with_join, test_rejects_unknown_table, test_rejects_non_select_start, test_allows_select_with_where
- [ ] Integration tests (require LLM): test_query_generates_sql, test_query_customer_by_name, test_query_status_filter, test_query_time_range, test_query_aggregate, test_query_order, test_query_score_range, test_query_multi_table, test_query_follow_up_incomplete, test_total_test_count
- [ ] Run security tests: `pytest src/module_enterprise/tests/test_nl2sql.py::TestNL2SQLSecurity -v` (all pass)
- [ ] Commit: `git commit -m "test: 20 NL2SQL test cases including security and query generation"`

### Task 20: Approval Workflow Tests

**Files:** Create `src/module_student/tests/__init__.py`, `test_approval.py`
**Produces:** 7 unit tests for approval service

- [ ] Tests: test_submit_creates_record, test_submit_creates_notification, test_approve_application, test_reject_application, test_transfer_application, test_get_status_not_found, test_get_status_found
- [ ] Run: `pytest src/module_student/tests/test_approval.py -v`
- [ ] Commit: `git commit -m "test: approval workflow unit tests (submit/approve/reject/transfer/status)"`

### Task 21: CRUD + KB Tests

**Files:** Create `tests/test_crud.py`, `src/module_student/tests/test_kb.py`
**Produces:** 8 CRUD list endpoint tests + 3 KB search tests

- [ ] CRUD tests (using httpx AsyncClient + ASGITransport): test_list_customers, test_list_reports, test_list_complaints, test_list_scores, test_list_admin_services, test_list_mental_health, test_list_alerts, test_list_tickets — all verify 200 status and APIResponse structure
- [ ] KB tests: test_search_returns_results, test_search_empty_query, test_search_top_k_limit
- [ ] Run: `pytest tests/test_crud.py src/module_student/tests/test_kb.py -v`
- [ ] Commit: `git commit -m "test: KB search tests and CRUD integration tests for all 8 tables"`

### Task 22: E2E Approval Flow Test

**Files:** Modify `tests/test_e2e_student_flow.py`
**Produces:** Full end-to-end approval flow test

- [ ] Implement test_full_approval_flow: POST submit (verify 201 + status=待审批) -> POST approve (verify 200 + status=已通过) -> GET status (verify same status) -> GET notifications/pending (verify approval_result notification exists)
- [ ] Implement test_health_check: GET /health returns 200 + healthy
- [ ] Run: `pytest tests/test_e2e_student_flow.py -v`
- [ ] Commit: `git commit -m "test: E2E approval flow (submit->approve->status->notification)"`

### Task 23: Final Verification & Docs

**Files:** Modify `requirements.txt`, `README.md`
**Produces:** Runnable project with complete documentation

- [ ] Add `apscheduler>=3.10.0` to requirements.txt
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run all tests: `pytest -v --tb=short`
- [ ] Start app: `uvicorn src.main:app --host 127.0.0.1 --port 8000` — verify no errors, Ctrl+C
- [ ] Check Swagger at http://127.0.0.1:8000/docs shows all 8 tag groups
- [ ] Update README.md with complete API table (all endpoints by module)
- [ ] Commit: `git commit -m "docs: update README with API documentation and add apscheduler dependency"`

---

## Dependency Graph

```
Task1(config) -> Task2(DDL) + Task3(DB engine)
  -> Task4(models) + Task5(schemas)
    -> Task6(CRUD base)
      -> Task7(enterprise CRUD) + Task11(student CRUD)
      -> Task8(NL2SQL) + Task9(tasks) + Task10(instructions)
      -> Task12(notifications)
        -> Task13(approval)
      -> Task14(sync) + Task15(KB) + Task16(AI)
        -> Task17(main.py) + Task18(import script)
          -> Task19-22(tests)
            -> Task23(final)
```

**Total: 23 tasks, ~30 new files, 4 modified files**


