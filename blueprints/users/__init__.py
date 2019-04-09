from flask_restful import fields
from blueprints import db
    
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(50), unique=True)
    display_name = db.Column(db.String(50))
    headline = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    cover_photo = db.Column(db.String(255))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.String(50))
    address = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    facebook_link = db.Column(db.String(50))
    instagram_link = db.Column(db.String(50))
    twitter_link = db.Column(db.String(50))
    other_link = db.Column(db.String(50))
    created_at = db.Column(db.String(50))
    updated_at = db.Column(db.String(50))
    post_count = db.Column(db.Integer)
    job = db.Column(db.String(50))
    status = db.Column(db.String(50))

    response_field = {
        "id" : fields.Integer,
        "username" : fields.String,
        # "password" : fields.String,
        "email" : fields.String,
        "display_name" : fields.String,
        "headline" : fields.String,
        "profile_picture" : fields.String,
        "cover_photo" : fields.String,
        "gender" : fields.String,
        "date_of_birth" : fields.String,
        "address" : fields.String,
        "phone_number" : fields.String,
        "facebook_link" : fields.String,
        "instagram_link" : fields.String,
        "twitter_link" : fields.String,
        "other_link" : fields.String,
        "created_at" : fields.String,
        "updated_at": fields.String,
        "post_count" : fields.Integer,
        "job" : fields.String,
        "status" : fields.String
    }

    def __init__(self, id, username, password, email, display_name, headline, profile_picture, cover_photo, gender, date_of_birth, address, phone_number, facebook_link, instagram_link, twitter_link, other_link, created_at, updated_at, post_count, job, status):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.display_name = display_name
        self.headline = headline
        self.profile_picture = profile_picture
        self.cover_photo = cover_photo
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.address = address
        self.phone_number = phone_number
        self.facebook_link = facebook_link
        self.instagram_link = instagram_link
        self.twitter_link = twitter_link
        self.other_link = other_link
        self.created_at = created_at
        self.updated_at = updated_at
        self.post_count = post_count
        self.job = job
        self.status = status

    def __repr__(self):
        return f'<Users {self.id}>'

db.create_all()