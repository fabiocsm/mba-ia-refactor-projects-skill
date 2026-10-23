from sqlalchemy import func

from database import db
from models.task import Task
from models.user import User
from utils.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from utils.time import utc_now


def _fake_token_for(user):
    return f'fake-jwt-token-{user.id}'


def list_users():
    users = User.query.all()
    task_counts = dict(
        db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
    )
    result = []
    for user in users:
        data = user.to_dict()
        data['task_count'] = task_counts.get(user.id, 0)
        result.append(data)
    return result


def get_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [task.to_dict() for task in tasks]
    return data


def create_user(payload):
    if User.find_by_email(payload['email']) is not None:
        raise ConflictError('Email já cadastrado')

    user = User()
    user.name = payload['name']
    user.email = payload['email']
    user.set_password(payload['password'])
    user.role = payload['role']

    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, updates):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    if 'name' in updates:
        user.name = updates['name']
    if 'email' in updates:
        existing = User.find_by_email(updates['email'])
        if existing is not None and existing.id != user_id:
            raise ConflictError('Email já cadastrado')
        user.email = updates['email']
    if 'password' in updates:
        user.set_password(updates['password'])
    if 'role' in updates:
        user.role = updates['role']
    if 'active' in updates:
        user.active = updates['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    for task in tasks:
        db.session.delete(task)

    db.session.delete(user)
    db.session.commit()


def get_user_tasks(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    now = utc_now()
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': task.is_overdue(now),
        })
    return result


def login(email, password):
    user = User.find_by_email(email)
    if user is None or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')

    if not user.active:
        raise ForbiddenError('Usuário inativo')

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': _fake_token_for(user),
    }
