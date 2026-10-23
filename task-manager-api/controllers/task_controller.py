from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.constants import STATUS_CANCELLED, STATUS_DONE, STATUS_IN_PROGRESS, STATUS_PENDING
from utils.errors import NotFoundError
from utils.metrics import completion_rate
from utils.time import utc_now
from utils.validators import parse_date_strict, parse_int_query_param


def _serialize_with_overdue(task, now):
    data = task.to_dict()
    data['overdue'] = task.is_overdue(now)
    return data


def list_tasks():
    now = utc_now()
    tasks = Task.list_all_with_relations()
    result = []
    for task in tasks:
        data = _serialize_with_overdue(task, now)
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return result


def get_task(task_id):
    task = Task.get_by_id(task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')
    return _serialize_with_overdue(task, utc_now())


def create_task(payload):
    if payload['user_id']:
        if User.get_by_id(payload['user_id']) is None:
            raise NotFoundError('Usuário não encontrado')

    if payload['category_id']:
        if Category.get_by_id(payload['category_id']) is None:
            raise NotFoundError('Categoria não encontrada')

    task = Task()
    task.title = payload['title']
    task.description = payload['description']
    task.status = payload['status']
    task.priority = payload['priority']
    task.user_id = payload['user_id']
    task.category_id = payload['category_id']

    if payload['due_date']:
        task.due_date = parse_date_strict(payload['due_date'], 'Formato de data inválido. Use YYYY-MM-DD')

    if payload['tags']:
        task.tags = ','.join(payload['tags']) if isinstance(payload['tags'], list) else payload['tags']

    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def update_task(task_id, updates):
    task = Task.get_by_id(task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')

    if 'title' in updates:
        task.title = updates['title']
    if 'description' in updates:
        task.description = updates['description']
    if 'status' in updates:
        task.status = updates['status']
    if 'priority' in updates:
        task.priority = updates['priority']
    if 'user_id' in updates:
        if updates['user_id']:
            if User.get_by_id(updates['user_id']) is None:
                raise NotFoundError('Usuário não encontrado')
        task.user_id = updates['user_id']
    if 'category_id' in updates:
        if updates['category_id']:
            if Category.get_by_id(updates['category_id']) is None:
                raise NotFoundError('Categoria não encontrada')
        task.category_id = updates['category_id']
    if 'due_date' in updates:
        if updates['due_date']:
            task.due_date = parse_date_strict(updates['due_date'], 'Formato de data inválido')
        else:
            task.due_date = None
    if 'tags' in updates:
        tags = updates['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = utc_now()
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = Task.get_by_id(task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')
    db.session.delete(task)
    db.session.commit()


def search_tasks(args):
    term = args.get('q', '')
    status = args.get('status', '')
    priority_raw = args.get('priority', '')
    user_id_raw = args.get('user_id', '')

    priority = parse_int_query_param(priority_raw, 'Prioridade inválida') if priority_raw else None
    user_id = parse_int_query_param(user_id_raw, 'user_id inválido') if user_id_raw else None

    tasks = Task.search(term=term, status=status, priority=priority, user_id=user_id)
    return [task.to_dict() for task in tasks]


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status=STATUS_PENDING).count()
    in_progress = Task.query.filter_by(status=STATUS_IN_PROGRESS).count()
    done = Task.query.filter_by(status=STATUS_DONE).count()
    cancelled = Task.query.filter_by(status=STATUS_CANCELLED).count()

    now = utc_now()
    overdue_count = sum(1 for task in Task.query.all() if task.is_overdue(now))

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': completion_rate(done, total),
    }
