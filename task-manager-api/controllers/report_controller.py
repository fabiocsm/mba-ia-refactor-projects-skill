from datetime import timedelta

from models.category import Category
from models.task import Task
from models.user import User
from utils.constants import (
    HIGH_PRIORITY_THRESHOLD,
    PRIORITY_LABELS,
    RECENT_ACTIVITY_WINDOW_DAYS,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
)
from utils.errors import NotFoundError
from utils.metrics import completion_rate
from utils.time import utc_now


def summary_report():
    now = utc_now()

    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status=STATUS_PENDING).count()
    in_progress = Task.query.filter_by(status=STATUS_IN_PROGRESS).count()
    done = Task.query.filter_by(status=STATUS_DONE).count()
    cancelled = Task.query.filter_by(status=STATUS_CANCELLED).count()

    priority_counts = {}
    for level, label in PRIORITY_LABELS.items():
        priority_counts[label] = Task.query.filter_by(priority=level).count()

    all_tasks = Task.query.all()
    overdue_list = []
    for task in all_tasks:
        if task.is_overdue(now):
            overdue_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (now - task.due_date).days,
            })

    since = now - timedelta(days=RECENT_ACTIVITY_WINDOW_DAYS)
    recent_tasks = Task.query.filter(Task.created_at >= since).count()
    recent_done = Task.query.filter(Task.status == STATUS_DONE, Task.updated_at >= since).count()

    task_counts_by_user = {}
    for task in all_tasks:
        bucket = task_counts_by_user.setdefault(task.user_id, {'total': 0, 'completed': 0})
        bucket['total'] += 1
        if task.status == STATUS_DONE:
            bucket['completed'] += 1

    users = User.query.all()
    user_stats = []
    for user in users:
        bucket = task_counts_by_user.get(user.id, {'total': 0, 'completed': 0})
        total = bucket['total']
        completed = bucket['completed']
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': completion_rate(completed, total),
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': priority_counts,
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    now = utc_now()
    tasks = Task.query.filter_by(user_id=user_id).all()

    total = len(tasks)
    done = sum(1 for task in tasks if task.status == STATUS_DONE)
    pending = sum(1 for task in tasks if task.status == STATUS_PENDING)
    in_progress = sum(1 for task in tasks if task.status == STATUS_IN_PROGRESS)
    cancelled = sum(1 for task in tasks if task.status == STATUS_CANCELLED)
    high_priority = sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD)
    overdue = sum(1 for task in tasks if task.is_overdue(now))

    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': completion_rate(done, total),
        },
    }
