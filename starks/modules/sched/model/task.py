import json
from datetime import datetime

from starks.extensions import db


class Task(db.Model):

    __tablename__ = "starks_tasks"

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_SUCCESS = "success"
    STATUS_ERROR = "error"

    TASK_TYPE_DOCKER = "docker"
    TASK_TYPE_BASH = "bash"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.String(64), )
    status = db.Column(db.String(32), nullable=False)
    task_type = db.Column(db.String(32), nullable=False)
    _requirement = db.Column("requirement", db.JSON, default="{}")
    _params = db.Column("params", db.JSON, default="{}")
    _result = db.Column("result", db.JSON, default="{}")
    started_at = db.Column(db.DateTime, nullable=True, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, user_id, status=STATUS_PENDING, params=None, _commit=True):
        obj = cls(user_id=user_id, status=status)
        obj.params = params or {}
        db.session.add(obj)
        if _commit is True:
            db.session.commit()
        return obj

    @classmethod
    def list_latest_jobs(cls, limit=50):
        return cls.query.order_by(cls.id.desc()).limit(limit).all()

    @property
    def requirement(self):
        return json.loads(self._requirement)

    @requirement.setter
    def requirement(self, value):
        self._requirement = json.dumps(value)

    @property
    def params(self):
        return json.loads(self._params)

    @params.setter
    def params(self, value):
        self._params = json.dumps(value)

    @property
    def result(self):
        if self._result:
            return json.loads(self._result)

    @result.setter
    def result(self, value):
        self._result = json.dumps(value)

    def save(self):
        db.session.add(self)
        db.session.commit()
