import json, logging
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
import datetime

from . import *
from blueprints.users import *

bp_feedLike = Blueprint('feedLike', __name__)
api = Api(bp_feedLike)

class FeedLikeResource(Resource):

    def __init__(self):
        pass

    def get(self, id_like):

        qry = FeedLike.query.filter_by(id_feed = id_like).all()
        feeds = marshal(qry, FeedLike.response_field)

        output = {}
        output['data'] = feeds
        output['total'] = len(feeds)

        if qry is not None:
            return output, 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Feed Like not found'}, 404, {'Content_type' : 'application/json'}
   
    @jwt_required
    def post(self, id_like):
        jwtClaims = get_jwt_claims()
        liked_by = jwtClaims['id']

        qry = FeedLike.query.filter_by(id_feed = id_like).filter(FeedLike.liked_by == jwtClaims['id']).first()

        if qry is None:

            id_feed = id_like

            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()

            feeds = FeedLike(None, id_feed, liked_by, created_at, updated_at)
            db.session.add(feeds)
            db.session.commit()
            users = Users.query.get(jwtClaims['id'])

            feed = {}
            feed['data'] = marshal(feeds, FeedLike.response_field)
            
            return feed, 200, {'Content_type' : 'application/json'}
        else:
            return "Feed sudah di Like oleh User", 200, {'Content_type' : 'application/json'}

    @jwt_required
    def put(self, id_like):
        parser = reqparse.RequestParser()
        parser.add_argument('id_feed', location = 'json')
        parser.add_argument('liked_by', location = 'json')
        args = parser.parse_args()
        
        qry = FeedLike.query.get(id_like)
        if qry is not None:
            if args['id_feed'] is not None:
                qry.id_feed = args['id_feed']
            if args['liked_by'] is not None:
                qry.liked_by = args['liked_by']
                
            qry.updated_at = datetime.datetime.now()
            db.session.commit()
            return marshal(qry, FeedLike.response_field), 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Feed Like not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def delete(self, id_like):
        jwtClaims = get_jwt_claims()

        qry = FeedLike.query.filter_by(id_feed = id_like).filter(FeedLike.liked_by == jwtClaims['id']).first()
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return 'Deleted', 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Feed Like not found'}, 404, {'Content_type' : 'application/json'}

    def options(self, id_like = None):
        return {}, 200

api.add_resource(FeedLikeResource, '', '/<int:id_like>')