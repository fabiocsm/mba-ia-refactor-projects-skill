from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from utils.errors import NotFoundError


def list_categories():
    categories = Category.query.all()
    task_counts = dict(
        db.session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).all()
    )
    result = []
    for category in categories:
        data = category.to_dict()
        data['task_count'] = task_counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(payload):
    category = Category()
    category.name = payload['name']
    category.description = payload['description']
    category.color = payload['color']
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(category_id, updates):
    category = Category.get_by_id(category_id)
    if category is None:
        raise NotFoundError('Categoria não encontrada')

    if 'name' in updates:
        category.name = updates['name']
    if 'description' in updates:
        category.description = updates['description']
    if 'color' in updates:
        category.color = updates['color']

    db.session.commit()
    return category.to_dict()


def delete_category(category_id):
    category = Category.get_by_id(category_id)
    if category is None:
        raise NotFoundError('Categoria não encontrada')
    db.session.delete(category)
    db.session.commit()
