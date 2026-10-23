from sqlalchemy.orm import joinedload

from database import db
from utils.constants import CLOSED_TASK_STATUSES
from utils.time import utc_now


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def is_overdue(self, now):
        return bool(self.due_date) and self.due_date < now and self.status not in CLOSED_TASK_STATUSES

    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_all_with_relations(cls):
        return cls.query.options(joinedload(cls.user), joinedload(cls.category)).all()

    @classmethod
    def search(cls, term=None, status=None, priority=None, user_id=None):
        query = cls.query
        if term:
            query = query.filter(
                db.or_(cls.title.like(f'%{term}%'), cls.description.like(f'%{term}%'))
            )
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.all()
