from flask import Blueprint, Flask
import json
from flask_restful import Resource, Api, reqparse, marshal
from . import *
from blueprints.users import Users
from passlib.hash import sha256_crypt
from datetime import date, datetime
from blueprints import db

from flask_jwt_extended import create_access_token

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class CreateTokenResources(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        qry = Users.query.filter_by(username=args['username']).first()

        if (sha256_crypt.verify(args['password'], qry.password) == True) :
            token = create_access_token(marshal(qry, Users.response_field))
        else:
            return {'status' : 'UNAUTHORIZED', 'message' : 'Invalid key'}, 401, {'Content_type' : 'application/json'}
        return {'status': 'Successful login', 'token' : token}, 200, {'Content_type' : 'application/json'}

        # if qry is not None:
        #     token = create_access_token(identity=marshal(qry, Users.response_field))
        # else:
        #     return {'status': 'UNAUTHORIZED', 'message': 'invalid key or secret'}, 401
        # return {'token': token}, 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    def options(self):
        return {}, 200

class CreateTokenEmailResources(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('display_name', location='json', required=True)
        parser.add_argument('profile_picture', location='json', required=True)
        args = parser.parse_args()

        # password = sha256_crypt.verify(args['password']
        password = sha256_crypt.encrypt(args['email'])

        qry = Users.query.filter_by(email = args['email']).first()
        if qry is not None:
            token = create_access_token(identity = marshal(qry, Users.response_field))
        else:
            created_at = datetime.now()
            updated_at = datetime.now()
            user = Users(None, args['email'], password, args['email'], args['display_name'], None, args['profile_picture'], None, None, None, None, None, None, None, None, None, created_at, updated_at, 0, None, None)
            # users = Users(None, args['username'], passwrd, args['email'], args['display_name'], args['headline'], args['profile_picture'], args['cover_photo'], args['gender'], args['date_of_birth'], args['address'], args['phone_number'], args['facebook_link'], args['instagram_link'], args['twitter_link'], args['other_link'], created_at, updated_at, args['post_count'], args['job'], args['status'])

            db.session.add(user)
            db.session.commit()
            token = create_access_token(identity = marshal(user, Users.response_field))

        # return {
        #     'status': 'OK',
        #     'logged_in_as': args['email'],
        #     'token': token
        # }, 200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        return {'status': 'Successful login', 'token' : token}, 200, {'Content_type' : 'application/json'}

        if qry is not None:

            if (sha256_crypt.verify(args['password'], qry.password) == True) :
                token = create_access_token(marshal(qry, Users.response_field))
            else:
                return {'status' : 'UNAUTHORIZED', 'message' : 'Invalid Password'}, 400, {'Content_type' : 'application/json'}
            return {'status': 'Successful login', 'token' : token}, 200, {'Content_type' : 'application/json'}
    
        return {'status' : 'UNAUTHORIZED', 'message' : 'Invalid Username'}, 400, {'Content_type' : 'application/json'}
        
    def options(self):
        return {}, 200

api.add_resource(CreateTokenResources, '')
api.add_resource(CreateTokenEmailResources, '/email')