from datetime import datetime

from starks.extensions import db


class Task(db.Model):

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    task_type = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
