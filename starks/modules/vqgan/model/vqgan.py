from datetime import datetime

from flask import url_for

from starks.extensions import db


class VQGAN(db.Model):

    __tablename__ = "vqgans"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.String(64), nullable=False)
    bucket_name = db.Column(db.String(128), nullable=False)
    obj_key = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, text, bucket_name, obj_key, _commit=True):
        obj = cls(
            text=text,
            bucket_name=bucket_name,
            obj_key=obj_key,
        )
        db.session.add(obj)
        if _commit is True:
            db.session.commit()
        return obj

    @classmethod
    def get(cls, id_):
        return cls.query.get(id_)

    @classmethod
    def paginate(cls, page, page_size):
        return cls.query.order_by(cls.id.desc()).paginate(
            page, page_size, error_out=False)

    def marshal(self):
        return {
            "id": self.id,
            "text": self.text,
            "preview_url": url_for("vqgan.preview_vqgan",
                                   id_=self.id, _external=True),
        }
