from database import db
from utils.security import hash_password, verify_password
from utils.time import utc_now

USER_PUBLIC_FIELDS = ('id', 'name', 'email', 'role', 'active', 'created_at')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        data = {field: getattr(self, field) for field in USER_PUBLIC_FIELDS}
        data['created_at'] = str(data['created_at'])
        return data

    def set_password(self, raw_password):
        self.password = hash_password(raw_password)

    def check_password(self, raw_password):
        return verify_password(raw_password, self.password)

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
