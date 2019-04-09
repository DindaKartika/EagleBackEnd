import random, logging
import random, logging
from blueprints import db
from flask_restful import fields
import datetime

from blueprints.users import *
from blueprints.PostFeed import *

class Bookmark(db.Model):

    __tablename__ = "bookmark"

    id_bookmark = db.Column(db.Integer, primary_key = True, autoincrement = True)
    id_feed = db.Column(db.Integer)
    id_user = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    response_field = {
        'id_bookmark' : fields.Integer,
        'id_feed' : fields.Integer,
        'id_user' : fields.Integer,
        'created_at' : fields.DateTime,
        'updated_at' : fields.DateTime
    }

    def __init__ (self, id_bookmark, id_feed, id_user, created_at, updated_at):
        self.id_bookmark = id_bookmark
        self.id_feed = id_feed
        self.id_user = id_user
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Bookmark %r>' % self.id_bookmark