import json

from datetime import datetime

from starks.extensions import db


class VQGANJob(db.Model):

    __tablename__ = 'vqgan_jobs'

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_SUCCESS = "success"
    STATUS_ERROR = "error"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), default=STATUS_PENDING)
    _params = db.Column('params', db.String(4096))
    _result = db.Column('result', db.String(4096))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, username, status=STATUS_PENDING, params=None, _commit=True):
        obj = cls(username=username, status=status)
        obj.params = params or {}
        db.session.add(obj)
        if _commit is True:
            db.session.commit()
        return obj

    @classmethod
    def get_next_job(cls):
        return cls.query.filter(
            cls.status == STATUS_PENDING,
        ).order_by(cls.id).first()

    @classmethod
    def list_latest_jobs(cls, limit=50):
        return cls.query.order_by(cls.id.desc()).limit(limit).all()

    @property
    def params(self):
        return json.loads(self._params)

    @params.setter
    def params(self, value):
        self._params = json.dumps(value)

    @property
    def result(self):
        return json.loads(self._result)

    @result.setter
    def result(self, value):
        self._result = json.dumps(value)

    def set_result(self, is_success, message, _commit=True):
        self.result = {
            'success': is_success,
            'message': message,
        }
        if _commit is True:
            self.save()
        return self.result

    def save(self):
        db.session.add(self)
        db.session.commit()
