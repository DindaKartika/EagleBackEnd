import json, logging
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
import datetime
from sqlalchemy import desc

from . import *
from blueprints.users import *
from blueprints.PostFeed import *

bp_bookmark = Blueprint('Bookmark', __name__)
api = Api(bp_bookmark)

class BookmarkResources(Resource):

    def __init__(self):
        pass

    @jwt_required
    def get(self, id_bookmark = None):
        jwtClaims = get_jwt_claims()

        if id_bookmark == None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type = int, location = 'args', default = 1)
            parser.add_argument('rp', type = int, location = 'args', default = 5)
            parser.add_argument('search', location = 'args')
            parser.add_argument('sort', location='args', choices=('desc','asc'))
            args = parser.parse_args()

            offsets = (args['p'] * args['rp']) - args['rp']
            qry = Feeds.query

            # if args['search'] is not None:
            #     qry = qry.filter(Feeds.content.like("%"+args['search']+"%"))
            #     if qry.first() is None:
            #         qry = Feeds.query.filter(Feeds.tag.like("%"+args['search']+"%"))
            #         if qry.first() is None:
            #             qry = Feeds.query
            #             qry1 = Farms.query.filter(Farms.plant_type.like("%"+args['search']+"%")).all()
            #             temp_list = []
            #             for element in qry1:
            #                 temp = marshal(element, Farms.response_field)
            #                 temp_list.append(temp['id_user'])
            #             qry = qry.filter(Feeds.id_user.in_(temp_list))
            #             if qry.first() is None:
            #                 qry = Feeds.query
            #                 qry1 = Users.query.filter(Users.address.like("%"+args['search']+"%")).all()
            #                 temp_list = []
            #                 for element in qry1:
            #                     temp = marshal(element, Users.response_field)
            #                     temp_list.append(temp['id'])
            #                 qry = qry.filter(Feeds.id_user.in_(temp_list))
            #                 if qry.first() is None:
            #                     return {'status': 'Not Found', 'message': 'Feed is not found'}, 404, {'Content-Type': 'application/json'}

            qry = qry.filter(Feeds.id_user==jwtClaims['id'])

            if args['sort']=='desc':
                qry = qry.order_by(desc(Feeds.created_at))
            else:
                qry = qry.order_by(Feeds.created_at)

            rows = []
            for row in qry.limit(args['rp']).offset(offsets).all():
                bookmarks = marshal(row, Bookmark.response_field)
                feeds = Feeds.query.get(row.id_feed)
                bookmarks['feed'] = marshal(feeds, Feeds.response_field)
                users = Users.query.get(row.id_user)
                bookmarks['user'] = marshal(users, Users.response_field)
                rows.append(bookmarks)
            return rows, 200, {'Content_type' : 'application/json'}
        else:
            qry = Bookmark.query.get(id_bookmark)
            if qry is not None:
                bookmarks = marshal(qry, Bookmark.response_field)
                feeds = Feeds.query.get(qry.id_feed)
                bookmarks['feed'] = marshal(feeds, Feeds.response_field)
                users = Users.query.get(qry.id_user)
                bookmarks['user'] = marshal(users, Users.response_field)
                return bookmarks, 200, {'Content_type' : 'application/json'}
            else:
                return {'status' : 'NOT_FOUND', 'message' : 'Post Feed not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def post(self, id_bookmark):
        jwtClaims = get_jwt_claims()
        id_user = jwtClaims['id']

        qry = Bookmark.query.filter_by(id_feed = id_bookmark).filter(Bookmark.id_user == jwtClaims['id']).first()

        if qry is None:

            id_feed = id_bookmark

            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()

            bookmarks = Bookmark(None, id_feed, jwtClaims['id'], created_at, updated_at)
            db.session.add(bookmarks)
            db.session.commit()
            users = Users.query.get(jwtClaims['id'])
            feeds = Feeds.query.get(id_feed)

            bookmark = {}
            bookmark['data'] = marshal(bookmarks, Bookmark.response_field)
            bookmark['user'] = marshal(users, Users.response_field)
            bookmark['feed'] = marshal(feeds, Feeds.response_field)
            
            return bookmark, 200, {'Content_type' : 'application/json'}
        else:
            return "Feed sudah dibookmark oleh user", 200, {'Content_type' : 'application/json'}


    # @jwt_required
    # def put(self, id_bookmark):
        
    #     qry = Bookmark.query.get(id_bookmark)
    #     if qry is not None:
    #         if args['id_bookmark'] is not None:
    #             qry.id_bookmark = args['id_bookmark']

    #         qry.updated_at = datetime.datetime.now()
    #         db.session.commit()
    #         return marshal(qry, Bookmark.response_field), 200, {'Content_type' : 'application/json'}

    #     else:
    #         return {'status' : 'NOT_FOUND', 'message' : 'Comment Like not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def delete(self, id_bookmark):
        jwtClaims = get_jwt_claims()

        qry = Bookmark.query.filter_by(id_feed = id_bookmark).filter(Bookmark.id_user == jwtClaims['id']).first()
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return 'Deleted', 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Comment Like not found'}, 404, {'Content_type' : 'application/json'}

    def options(self, id_bookmark = None):
        return {}, 200

api.add_resource(BookmarkResources, '', '/<int:id_bookmark>')