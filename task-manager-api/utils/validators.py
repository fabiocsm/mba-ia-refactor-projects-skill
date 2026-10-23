import re
from datetime import datetime

from utils.constants import (
    DATE_FORMAT,
    DEFAULT_CATEGORY_COLOR,
    DEFAULT_PRIORITY,
    EMAIL_PATTERN,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    ROLE_USER,
    STATUS_PENDING,
    TASK_STATUSES,
    USER_ROLES,
)
from utils.errors import ValidationError


def require_json_object(data):
    if not isinstance(data, dict) or not data:
        raise ValidationError('Dados inválidos')
    return data


def parse_date_strict(value, invalid_message):
    if not isinstance(value, str):
        raise ValidationError(invalid_message)
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValidationError(invalid_message)


def parse_int_query_param(value, invalid_message):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(invalid_message)


def _validate_title_length(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _validate_priority_value(priority):
    if not isinstance(priority, (int, float)) or isinstance(priority, bool):
        raise ValidationError('Prioridade deve ser entre 1 e 5')
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError('Prioridade deve ser entre 1 e 5')
    return priority


def validate_task_create_payload(data):
    data = require_json_object(data)

    title = data.get('title')
    if not title:
        raise ValidationError('Título é obrigatório')
    title = _validate_title_length(title)

    status = data.get('status', STATUS_PENDING)
    if status not in TASK_STATUSES:
        raise ValidationError('Status inválido')

    priority = _validate_priority_value(data.get('priority', DEFAULT_PRIORITY))

    return {
        'title': title,
        'description': data.get('description', ''),
        'status': status,
        'priority': priority,
        'user_id': data.get('user_id'),
        'category_id': data.get('category_id'),
        'due_date': data.get('due_date'),
        'tags': data.get('tags'),
    }


def validate_task_update_payload(data):
    data = require_json_object(data)
    updates = {}

    if 'title' in data:
        updates['title'] = _validate_title_length(data['title'])
    if 'description' in data:
        updates['description'] = data['description']
    if 'status' in data:
        if data['status'] not in TASK_STATUSES:
            raise ValidationError('Status inválido')
        updates['status'] = data['status']
    if 'priority' in data:
        updates['priority'] = _validate_priority_value(data['priority'])
    if 'user_id' in data:
        updates['user_id'] = data['user_id']
    if 'category_id' in data:
        updates['category_id'] = data['category_id']
    if 'due_date' in data:
        updates['due_date'] = data['due_date']
    if 'tags' in data:
        updates['tags'] = data['tags']

    return updates


def validate_user_create_payload(data):
    data = require_json_object(data)

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', ROLE_USER)

    if not name:
        raise ValidationError('Nome é obrigatório')
    if not email:
        raise ValidationError('Email é obrigatório')
    if not password:
        raise ValidationError('Senha é obrigatória')
    if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
        raise ValidationError('Email inválido')
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError('Senha deve ter no mínimo 4 caracteres')
    if role not in USER_ROLES:
        raise ValidationError('Role inválido')

    return {'name': name, 'email': email, 'password': password, 'role': role}


def validate_user_update_payload(data):
    data = require_json_object(data)
    updates = {}

    if 'name' in data:
        updates['name'] = data['name']
    if 'email' in data:
        email = data['email']
        if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
            raise ValidationError('Email inválido')
        updates['email'] = email
    if 'password' in data:
        password = data['password']
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError('Senha muito curta')
        updates['password'] = password
    if 'role' in data:
        if data['role'] not in USER_ROLES:
            raise ValidationError('Role inválido')
        updates['role'] = data['role']
    if 'active' in data:
        updates['active'] = data['active']

    return updates


def validate_login_payload(data):
    data = require_json_object(data)
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')
    return {'email': email, 'password': password}


def validate_category_create_payload(data):
    data = require_json_object(data)
    name = data.get('name')
    if not name:
        raise ValidationError('Nome é obrigatório')
    return {
        'name': name,
        'description': data.get('description', ''),
        'color': data.get('color', DEFAULT_CATEGORY_COLOR),
    }


def validate_category_update_payload(data):
    data = require_json_object(data)
    updates = {}
    if 'name' in data:
        updates['name'] = data['name']
    if 'description' in data:
        updates['description'] = data['description']
    if 'color' in data:
        updates['color'] = data['color']
    return updates
