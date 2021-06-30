from starks.extensions import db


class Empty(db.Model):

    __tablename__ = '_DELETE_ME_'

    id = db.Column(db.Integer, primary_key=True)
