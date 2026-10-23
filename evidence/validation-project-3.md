# Validation Evidence — task-manager-api

| Item | Value |
|---|---|
| Result | CLEAN |
| Failure type | — |
| Date | 2026-10-23 04:48 |
| Skill version | b106f86 |
| Restore point | 073e4d5 |
| Audit report | reports/audit-project-3.md |

## Environment
- Dependency environment: .venv/ (reused)
- Setup steps: `python seed.py`
- Boot command: `python app.py`
- Port: 5000 (free before boot: yes)
- Runtime artifacts removed: instance/ (created by Flask-SQLAlchemy's relative sqlite URI; removed after baseline and after validation boots)
- Code fingerprint: 3438962108-1067 at first boot / 3438962108-1067 at end (unchanged: yes)

## Boot
```text
 * Serving Flask app 'app'
 * Debug mode: off
2026-10-23 04:41:41,757 INFO werkzeug WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2026-10-23 04:41:41,757 INFO werkzeug Press CTRL+C to quit
2026-10-23 04:41:48,633 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:48] "GET /health HTTP/1.1" 200 -
2026-10-23 04:41:53,225 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /health HTTP/1.1" 200 -
2026-10-23 04:41:53,234 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET / HTTP/1.1" 200 -
2026-10-23 04:41:53,250 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /tasks HTTP/1.1" 200 -
2026-10-23 04:41:53,262 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /tasks/1 HTTP/1.1" 200 -
2026-10-23 04:41:53,274 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /tasks/search?status=pending HTTP/1.1" 200 -
2026-10-23 04:41:53,287 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /tasks/stats HTTP/1.1" 200 -
2026-10-23 04:41:53,298 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /users HTTP/1.1" 200 -
2026-10-23 04:41:53,309 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /users/1 HTTP/1.1" 200 -
2026-10-23 04:41:53,319 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /users/1/tasks HTTP/1.1" 200 -
2026-10-23 04:41:53,333 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /reports/summary HTTP/1.1" 200 -
2026-10-23 04:41:53,344 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /reports/user/1 HTTP/1.1" 200 -
2026-10-23 04:41:53,353 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "GET /categories HTTP/1.1" 200 -
2026-10-23 04:41:53,413 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "POST /login HTTP/1.1" 200 -
2026-10-23 04:41:53,428 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "POST /tasks HTTP/1.1" 201 -
2026-10-23 04:41:53,492 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "POST /users HTTP/1.1" 201 -
2026-10-23 04:41:53,503 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "POST /categories HTTP/1.1" 201 -
2026-10-23 04:41:53,515 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "PUT /tasks/5 HTTP/1.1" 200 -
2026-10-23 04:41:53,526 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "PUT /users/2 HTTP/1.1" 200 -
2026-10-23 04:41:53,536 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "PUT /categories/4 HTTP/1.1" 200 -
2026-10-23 04:41:53,546 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "DELETE /tasks/11 HTTP/1.1" 200 -
2026-10-23 04:41:53,557 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "DELETE /users/4 HTTP/1.1" 200 -
2026-10-23 04:41:53,568 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 04:41:53] "DELETE /categories/5 HTTP/1.1" 200 -
```

## Behavior baseline
Source: captured

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | GET | /health | 200 | {status,timestamp} | 200 | {status,timestamp} | ✓ |
| 2 | GET | / | 200 | {message,version} | 200 | {message,version} | ✓ |
| 3 | GET | /tasks | 200 | list<{category_id,category_name,created_at,description,due_date,id,overdue,priority,status,tags,title,updated_at,user_id,user_name}> | 200 | list<{category_id,category_name,created_at,description,due_date,id,overdue,priority,status,tags,title,updated_at,user_id,user_name}> | ✓ |
| 4 | GET | /tasks/<id> | 200 | {category_id,created_at,description,due_date,id,overdue,priority,status,tags,title,updated_at,user_id} | 200 | {category_id,created_at,description,due_date,id,overdue,priority,status,tags,title,updated_at,user_id} | ✓ |
| 5 | GET | /tasks/search | 200 | list<{category_id,created_at,description,due_date,id,priority,status,tags,title,updated_at,user_id}> | 200 | list<{category_id,created_at,description,due_date,id,priority,status,tags,title,updated_at,user_id}> | ✓ |
| 6 | GET | /tasks/stats | 200 | {cancelled,completion_rate,done,in_progress,overdue,pending,total} | 200 | {cancelled,completion_rate,done,in_progress,overdue,pending,total} | ✓ |
| 7 | GET | /users | 200 | list<{active,created_at,email,id,name,role,task_count}> | 200 | list<{active,created_at,email,id,name,role,task_count}> | ✓ |
| 8 | GET | /users/<id> | 200 | {active,created_at,email,id,name,password,role,tasks:list<{...}>} | 200 | {active,created_at,email,id,name,role,tasks:list<{...}>} | declared |
| 9 | GET | /users/<id>/tasks | 200 | list<{created_at,description,due_date,id,overdue,priority,status,title}> | 200 | list<{created_at,description,due_date,id,overdue,priority,status,title}> | ✓ |
| 10 | GET | /reports/summary | 200 | {generated_at,overdue:{count,tasks:list<{days_overdue,due_date,id,title}>},overview:{total_categories,total_tasks,total_users},recent_activity:{tasks_completed_last_7_days,tasks_created_last_7_days},tasks_by_priority:{critical,high,low,medium,minimal},tasks_by_status:{cancelled,done,in_progress,pending},user_productivity:list<{completed_tasks,completion_rate,total_tasks,user_id,user_name}>} | 200 | {generated_at,overdue:{count,tasks:list<{days_overdue,due_date,id,title}>},overview:{total_categories,total_tasks,total_users},recent_activity:{tasks_completed_last_7_days,tasks_created_last_7_days},tasks_by_priority:{critical,high,low,medium,minimal},tasks_by_status:{cancelled,done,in_progress,pending},user_productivity:list<{completed_tasks,completion_rate,total_tasks,user_id,user_name}>} | ✓ |
| 11 | GET | /reports/user/<id> | 200 | {statistics:{cancelled,completion_rate,done,high_priority,in_progress,overdue,pending,total_tasks},user:{email,id,name}} | 200 | {statistics:{cancelled,completion_rate,done,high_priority,in_progress,overdue,pending,total_tasks},user:{email,id,name}} | ✓ |
| 12 | GET | /categories | 200 | list<{color,created_at,description,id,name,task_count}> | 200 | list<{color,created_at,description,id,name,task_count}> | ✓ |
| 13 | POST | /login | 200 | {message,token,user:{active,created_at,email,id,name,password,role}} | 200 | {message,token,user:{active,created_at,email,id,name,role}} | declared |
| 14 | POST | /tasks | 201 | {category_id,created_at,description,due_date,id,priority,status,tags,title,updated_at,user_id} | 201 | {category_id,created_at,description,due_date,id,priority,status,tags,title,updated_at,user_id} | ✓ |
| 15 | POST | /users | 201 | {active,created_at,email,id,name,password,role} | 201 | {active,created_at,email,id,name,role} | declared |
| 16 | POST | /categories | 201 | {color,created_at,description,id,name} | 201 | {color,created_at,description,id,name} | ✓ |
| 17 | PUT | /tasks/<id> | 200 | {category_id,created_at,description,due_date,id,priority,status,tags,title,updated_at,user_id} | 200 | {category_id,created_at,description,due_date,id,priority,status,tags,title,updated_at,user_id} | ✓ |
| 18 | PUT | /users/<id> | 200 | {active,created_at,email,id,name,password,role} | 200 | {active,created_at,email,id,name,role} | declared |
| 19 | PUT | /categories/<id> | 200 | {color,created_at,description,id,name} | 200 | {color,created_at,description,id,name} | ✓ |
| 20 | DELETE | /tasks/<id> | 200 | {message} | 200 | {message} | ✓ |
| 21 | DELETE | /users/<id> | 200 | {message} | 200 | {message} | ✓ |
| 22 | DELETE | /categories/<id> | 200 | {message} | 200 | {message} | ✓ |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| GET /users/<id> | Removed `password` (hash) field from the response | AP-09 |
| POST /login | Removed `password` (hash) field from the `user` sub-object | AP-09 |
| POST /users | Removed `password` (hash) field from the response | AP-09 |
| PUT /users/<id> | Removed `password` (hash) field from the response | AP-09 |

## Re-audit
Reviewer: subagent
Remaining anti-patterns: 0
