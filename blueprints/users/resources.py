import json
from flask_restful import Resource, Api, reqparse, marshal
from flask import Blueprint, Flask
from . import *
from blueprints import db
from datetime import date, datetime
from passlib.hash import sha256_crypt
import re

from flask_jwt_extended import jwt_required, get_jwt_claims

bp_users = Blueprint('users', __name__)
api = Api(bp_users)

class UsersRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", location='json', required=True)
        parser.add_argument("password", location='json', required=True)
        parser.add_argument("email", location='json', required=True)
        parser.add_argument("display_name", location='json', default="")
        parser.add_argument("headline", location='json', default="")
        parser.add_argument("profile_picture", location='json', default="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png")
        parser.add_argument("cover_photo", location='json', default="https://www.qmatchup.com/images/default-cover.jpg")
        parser.add_argument("gender", location='json', default="")
        parser.add_argument("date_of_birth", location='json', default="")
        parser.add_argument("address", location='json', default="")
        parser.add_argument("phone_number", location='json', default="")
        parser.add_argument("facebook_link", location='json', default="")
        parser.add_argument("instagram_link", location='json', default="")
        parser.add_argument("twitter_link", location='json', default="")
        parser.add_argument("other_link", location='json', default="")
        parser.add_argument("post_count", location='json', default=0)
        parser.add_argument("job", location='json', default="")
        parser.add_argument("status", location='json', default="")
        args = parser.parse_args()

        all_user_qry = Users.query.all()

        for element in all_user_qry:
            if args['username'] == element.username:
                return {'status': 'Error', 'message': 'Username already registered'}, 400, {'Content-Type': 'application/json'}
            if args['email'] == element.email:
                return {'status': 'Error', 'message': 'Email already registered'}, 400, {'Content-Type': 'application/json'}

        # Username Validation
        pattern = "^(?![_.])"  
        result = re.match(pattern, args['username'])
        if not result:
            return {'status': 'Error', 'message': 'Username must not . or _ at the beginning'}, 400, {'Content-Type': 'application/json'}

        pattern = "^(?!.*[_.]{2})"  
        result = re.match(pattern, args['username'])
        if not result:
            return {'status': 'Error', 'message': 'Username must not contain .. or __'}, 400, {'Content-Type': 'application/json'}

        pattern = "[a-zA-Z0-9._]"
        result = re.match(pattern, args['username'])
        if not result:
            return {'status': 'Error', 'message': 'Username can only contain Alphanumeric'}, 400, {'Content-Type': 'application/json'}

        # Password Validation
        pattern = ".{8,}"
        result = re.match(pattern, args['password'])
        if not result:
            return {'status': 'Error', 'message': 'Password minimum 8 in length'}, 400, {'Content-Type': 'application/json'}
        
        pattern = "(?=.*?[A-Z])"
        result = re.match(pattern, args['password'])
        if not result:
            return {'status': 'Error', 'message': 'Password must at least one upper case'}, 400, {'Content-Type': 'application/json'}

        pattern = "(?=.*?[a-z])"
        result = re.match(pattern, args['password'])
        if not result:
            return {'status': 'Error', 'message': 'Password must at least one lower case'}, 400, {'Content-Type': 'application/json'}

        pattern = "(?=.*?[0-9])"
        result = re.match(pattern, args['password'])
        if not result:
            return {'status': 'Error', 'message': 'Password must at least one digit'}, 400, {'Content-Type': 'application/json'}

        # Email Validation
        pattern = "[^@]+@[^@]+\.[^@]+"
        result = re.match(pattern, args['email'])
        if not result:
            return {'status': 'Error', 'message': 'Email invalid'}, 400, {'Content-Type': 'application/json'}

        created_at = datetime.now()
        updated_at = datetime.now()
        passwrd = sha256_crypt.encrypt(args['password'])
        
        users = Users(None, args['username'], passwrd, args['email'], args['display_name'], args['headline'], args['profile_picture'], args['cover_photo'], args['gender'], args['date_of_birth'], args['address'], args['phone_number'], args['facebook_link'], args['instagram_link'], args['twitter_link'], args['other_link'], created_at, updated_at, args['post_count'], args['job'], args['status'])
        db.session.add(users)
        db.session.commit()

        if users is not None:
            return {'status': 'Success', 'message': 'User added', 'data': marshal(users, Users.response_field)}, 200, {'Content-Type': 'application/json'}
        return {'status': 'Failed', 'message': 'Please fill the field correctly'}, 400, {'Content-Type': 'application/json'}

    def options(self):
        return {}, 200

class UsersProfile(Resource):
    @jwt_required
    def get(self, id = None):
        qry = Users.query.get(get_jwt_claims()['id'])
        if qry is not None:
            return {'status': 'Success', 'data': marshal(qry, Users.response_field)}, 200, {'Content-Type': 'application/json'}
        return {'status': 'Not Found', 'message': 'User not found'}, 400, {'Content-Type': 'application/json'}

    @jwt_required
    def patch(self, id):        
        parser = reqparse.RequestParser()
        parser.add_argument("username", location='json')
        parser.add_argument("password", location='json')
        parser.add_argument("email", location='json')
        parser.add_argument("display_name", location='json')
        parser.add_argument("headline", location='json')
        parser.add_argument("profile_picture", location='json')
        parser.add_argument("cover_photo", location='json')
        parser.add_argument("gender", location='json')
        parser.add_argument("date_of_birth", location='json')
        parser.add_argument("address", location='json') 
        parser.add_argument("phone_number", location='json')
        parser.add_argument("facebook_link", location='json')
        parser.add_argument("instagram_link", location='json')
        parser.add_argument("twitter_link", location='json')
        parser.add_argument("other_link", location='json')
        parser.add_argument("post_count", location='json')
        parser.add_argument("job", location='json')
        parser.add_argument("status", location='json')
        args = parser.parse_args()

        user_qry = Users.query.get(get_jwt_claims()['id'])

        qry = Users.query.get(id)
        if qry is not None:
            if args['password'] is not None:
                qry.password = sha256_crypt.encrypt(args['password'])
            if args['email'] is not None:
                qry.email = args['email']
            if args['display_name'] is not None:
                qry.display_name = args['display_name']
            if args['headline'] is not None:
                qry.headline = args['headline']
            if args['profile_picture'] is not None:
                qry.profile_picture = args['profile_picture']
            if args['cover_photo'] is not None:
                qry.cover_photo = args['cover_photo']
            if args['gender'] is not None:
                qry.gender = args['gender']
            if args['date_of_birth'] is not None:
                qry.date_of_birth = args['date_of_birth']
            if args['address'] is not None:
                qry.address = args['address']
            if args['phone_number'] is not None:
                if args['phone_number'][0] == '0':
                    args['phone_number'] = '+62' + args['phone_number'][1:]
                elif args['phone_number'][0] != '+':
                    args['phone_number'] = '+62' + args['phone_number']
                qry.phone_number = args['phone_number']
            if args['facebook_link'] is not None:
                qry.facebook_link = args['facebook_link']
            if args['instagram_link'] is not None:
                qry.instagram_link = args['instagram_link']
            if args['twitter_link'] is not None:
                qry.twitter_link = args['twitter_link']
            if args['other_link'] is not None:
                qry.other_link = args['other_link']
            if args['post_count'] is not None:
                qry.post_count = args['post_count']
            if args['job'] is not None:
                qry.job = args['job']
            if args['status'] is not None:
                qry.status = args['status']

            db.session.commit()
        
            return {'status': 'Success', 'data': marshal(qry, Users.response_field)}, 200, {'Content-Type': 'application/json'}

        return {'status': 'Not Found', 'message': 'User not found'}, 400, {'Content-Type': 'application/json'}

    @jwt_required
    def delete(self, id):
        qry = Users.query.get(id)
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return {'status': "Success", 'message': 'User deleted'}, 200, {'Content-Type': 'application/json'}

        return {'status': 'Not Found', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}
    
    def options(self, id = None):
        return {}, 200

class AnotherUsersProfile(Resource):
    def get(self, id = None):
        if id == None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type = int, location = 'args', default = 1)
            parser.add_argument('rp', type = int, location = 'args', default = 20)
            parser.add_argument("username", location='json')
            parser.add_argument("email", location='json')
            parser.add_argument("display_name", location='json')
            parser.add_argument("headline", location='json')
            parser.add_argument("profile_picture", location='json')
            parser.add_argument("cover_photo", location='json')
            parser.add_argument("gender", location='json')
            parser.add_argument("date_of_birth", location='json')
            parser.add_argument("address", location='json') 
            parser.add_argument("phone_number", location='json')
            parser.add_argument("facebook_link", location='json')
            parser.add_argument("instagram_link", location='json')
            parser.add_argument("twitter_link", location='json')
            parser.add_argument("other_link", location='json')
            parser.add_argument("post_count", location='json')
            parser.add_argument("job", location='json')
            parser.add_argument("status", location='json')
            args = parser.parse_args()

            offsets = (args['p'] * args['rp']) - args['rp']
            qry = Users.query

            if args['username'] is not None:
                qry = qry.filter(Users.username == args['username'])

            if args['email'] is not None:
                qry = qry.filter(Users.email.like("%"+args['email']+"%"))

            if args['display_name'] is not None:
                qry = qry.filter(Users.display_name.like("%"+args['display_name']+"%"))
            
            if args['headline'] is not None:
                qry = qry.filter(Users.headline.like("%"+args['headline']+"%"))

            if args['gender'] is not None:
                qry = qry.filter(Users.gender.like("%"+args['gender']+"%"))

            if args['address'] is not None:
                qry = qry.filter(Users.address.like("%"+args['address']+"%"))

            if args['job'] is not None:
                qry = qry.filter(Users.job.like("%"+args['job']+"%"))

            if args['status'] is not None:
                qry = qry.filter(Users.status.like("%"+args['status']+"%"))

            rows = []
            for row in qry.limit(args['rp']).offset(offsets).all():
                users = marshal(row, Users.response_field)
                # users = Users.query.get(row.id)
                # users['user'] = marshal(users, Users.response_field)
                rows.append(users)
            return rows, 200, {'Content_type' : 'application/json'}
        
        else:
            qry = Users.query.get(id)
            if qry is not None:
                users = marshal(qry, Users.response_field)
                return users, 200, {'Content_type' : 'application/json'}
            else:
                return {'status' : 'NOT_FOUND'}, 404, {'Content_type' : 'application/json'}

api.add_resource(UsersRegister, '/register')
api.add_resource(UsersProfile, '/profile', '/profile/<int:id>')
api.add_resource(AnotherUsersProfile, '/userprofile', '/userprofile/<int:id>')