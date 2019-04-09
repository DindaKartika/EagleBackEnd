import json, logging
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
import datetime

from . import *
from blueprints.users import *

bp_commentsLike = Blueprint('commentsLike', __name__)
api = Api(bp_commentsLike)

class CommentsLikeResources(Resource):

    def __init__(self):
        pass

    def get(self, id_like):

        qry = CommentsLike.query.filter_by(id_comment = id_like).all()
        comments = marshal(qry, CommentsLike.response_field)

        output = {}
        output['data'] = comments
        output['total'] = len(comments)

        if qry is not None:
            return output, 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Comment Like not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def post(self, id_like):
        jwtClaims = get_jwt_claims()
        liked_by = jwtClaims['id']

        qry = CommentsLike.query.filter_by(id_comment = id_like).filter(CommentsLike.liked_by == jwtClaims['id']).first()

        if qry is None:

            id_comment = id_like

            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()

            comments = CommentsLike(None, id_comment, liked_by, created_at, updated_at)
            db.session.add(comments)
            db.session.commit()
            users = Users.query.get(jwtClaims['id'])

            comment = {}
            comment['data'] = marshal(comments, CommentsLike.response_field)
            
            return comment, 200, {'Content_type' : 'application/json'}
        else:
            return "Comment sudah di Like oleh User", 200, {'Content_type' : 'application/json'}


    @jwt_required
    def put(self, id_like):
        parser = reqparse.RequestParser()
        parser.add_argument('id_comment', location = 'json')
        parser.add_argument('liked_by', location = 'json')
        args = parser.parse_args()
        
        qry = CommentsLike.query.get(id_like)
        if qry is not None:
            if args['id_comment'] is not None:
                qry.id_comment = args['id_comment']
            if args['liked_by'] is not None:
                qry.liked_by = args['liked_by']

            qry.updated_at = datetime.datetime.now()
            db.session.commit()
            return marshal(qry, CommentsLike.response_field), 200, {'Content_type' : 'application/json'}

        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Comment Like not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def delete(self, id_like):
        jwtClaims = get_jwt_claims()

        qry = CommentsLike.query.filter_by(id_comment = id_like).filter(CommentsLike.liked_by == jwtClaims['id']).first()
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return 'Deleted', 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Comment Like not found'}, 404, {'Content_type' : 'application/json'}

    def options(self, id_like = None):
        return {}, 200

api.add_resource(CommentsLikeResources, '', '/<int:id_like>')