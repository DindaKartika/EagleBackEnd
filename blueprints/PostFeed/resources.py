import json, logging
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
import datetime
from blueprints.users import *
from blueprints.farm import *
from blueprints.comments import *
from blueprints.feedLike import *
from blueprints.commentLike import *
from sqlalchemy import desc
from . import *

bp_feed = Blueprint('feed', __name__)
api = Api(bp_feed)

class FeedResource(Resource):

    def __init__(self):
        pass

    def get(self, id_feed = None):
        if id_feed == None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type = int, location = 'args', default = 1)
            parser.add_argument('rp', type = int, location = 'args', default = 5)
            parser.add_argument('search', location = 'args')
            parser.add_argument('id_user', location = 'args')
            parser.add_argument('tag', location = 'args')
            parser.add_argument('plant_type', location = 'args')
            parser.add_argument('location', location = 'args')
            parser.add_argument('sort', location='args', choices=('desc','asc'))
            args = parser.parse_args()

            offsets = (args['p'] * args['rp']) - args['rp']
            qry = Feeds.query

            if args['search'] is not None:
                qry = qry.filter(Feeds.content.like("%"+args['search']+"%"))
                if qry.first() is None:
                    qry = Feeds.query.filter(Feeds.tag.like("%"+args['search']+"%"))
                    if qry.first() is None:
                        qry = Feeds.query
                        qry1 = Farms.query.filter(Farms.plant_type.like("%"+args['search']+"%")).all()
                        temp_list = []
                        for element in qry1:
                            temp = marshal(element, Farms.response_field)
                            temp_list.append(temp['id_user'])
                        qry = qry.filter(Feeds.id_user.in_(temp_list))
                        if qry.first() is None:
                            qry = Feeds.query
                            qry1 = Users.query.filter(Users.address.like("%"+args['search']+"%")).all()
                            temp_list = []
                            for element in qry1:
                                temp = marshal(element, Users.response_field)
                                temp_list.append(temp['id'])
                            qry = qry.filter(Feeds.id_user.in_(temp_list))
                            if qry.first() is None:
                                return {'status': 'Not Found', 'message': 'Feed is not found'}, 404, {'Content-Type': 'application/json'}

            if args['id_user'] is not None:
                qry = qry.filter(Feeds.id_user.like("%"+args['id_user']+"%"))
            if args['tag'] is not None:
                qry = qry.filter(Feeds.tag.like("%"+args['tag']+"%"))
            if args['plant_type'] is not None:
                qry1 = Farms.query.filter(Farms.plant_type.like("%"+args['plant_type']+"%")).all()
                temp_list = []
                for element in qry1:
                    temp = marshal(element, Farms.response_field)
                    temp_list.append(temp['id_user'])
                qry = qry.filter(Feeds.id_user.in_(temp_list))
            if args['location'] is not None:
                qry1 = Users.query.filter(Users.address.like("%"+args['location']+"%")).all()
                temp_list = []
                for element in qry1:
                    temp = marshal(element, Users.response_field)
                    temp_list.append(temp['id'])
                qry = qry.filter(Feeds.id_user.in_(temp_list))

            if args['sort']=='desc':
                qry = qry.order_by(desc(Feeds.created_at))
            else:
                qry = qry.order_by(Feeds.created_at)

            rows = []
            for row in qry.limit(args['rp']).offset(offsets).all():
                feeds = marshal(row, Feeds.response_field)
                users = Users.query.get(row.id_user)
                feedLike = FeedLike.query.filter(FeedLike.id_feed == row.id_feed)
                rowFeedLike = []
                for row in feedLike:
                    feedlike = marshal(row, FeedLike.response_field)
                    rowFeedLike.append(feedlike)
                feedComment = Comments.query.filter(Comments.id_feed==row.id_feed)
                rowComment = []
                for row in feedComment:
                    commentLike = CommentsLike.query.filter(CommentsLike.id_comment==row.id)
                    comment = marshal(row, Comments.response_field)
                    CommentLikes = []
                    commentBy = Users.query.get(row.id_user)
                    commentBy = marshal(commentBy, Users.response_field)
                    for rowed in commentLike:
                        commentLikes = marshal(rowed, CommentsLike.response_field)
                        CommentLikes.append(commentLikes)
                    comment['like'] = CommentLikes
                    comment['total_like_comment'] = len(CommentLikes)
                    comment['comment_by'] = commentBy
                    rowComment.append(comment)
                feeds['user'] = marshal(users, Users.response_field)
                feeds['like'] = rowFeedLike
                feeds['total_like_feed'] = len(rowFeedLike)
                feeds['comment'] = rowComment
                feeds['total_comment'] = len(rowComment)
                rows.append(feeds)
            return rows, 200, {'Content_type' : 'application/json'}
        else:
            qry = Feeds.query.get(id_feed)
            if qry is not None:
                feeds = marshal(qry, Feeds.response_field)
                users = Users.query.get(qry.id_user)
                feedLike = FeedLike.query.filter(FeedLike.id_feed == qry.id_feed)
                rowFeedLike = []
                for row in feedLike:
                    feedlike = marshal(row, FeedLike.response_field)
                    rowFeedLike.append(feedlike)
                feedComment = Comments.query.filter(Comments.id_feed==qry.id_feed)
                rowComment = []
                for row in feedComment:
                    commentLike = CommentsLike.query.filter(CommentsLike.id_comment==row.id)
                    commentBy = Users.query.get(row['id_user'])
                    comment = marshal(row, Comments.response_field)
                    CommentLikes = []
                    for rows in commentLike:
                        commentLikes = marshal(rows, CommentsLike.response_field)
                        CommentLikes.append(commentLikes)
                    comment['like'] = CommentLikes
                    comment['comment_by'] = commentBy
                    rowComment.append(comment)

                feeds['user'] = marshal(users, Users.response_field)
                feeds['like'] = rowFeedLike
                feeds['comment'] = rowComment
                return feeds, 200, {'Content_type' : 'application/json'}
            else:
                return {'status' : 'NOT_FOUND', 'message' : 'Post Feed not found'}, 404, {'Content_type' : 'application/json'}
   
    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims() ##  buat kalo butuh data klaim
        parser = reqparse.RequestParser()
        parser.add_argument('content', location = 'json', required=True)
        parser.add_argument('tag', location = 'json')
        parser.add_argument('image', location = 'json')
        args = parser.parse_args()

        id_user = jwtClaims['id']
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        feeds = Feeds(None, id_user, args['content'], args['tag'], args['image'], created_at, updated_at)
        qry_user = Users.query.get(id_user)
        qry_user.post_count += 1

        db.session.add(feeds)
        db.session.commit()

        feed = marshal(feeds, Feeds.response_field)
        feed['user'] = marshal(qry_user, qry_user.response_field)
        
        return feed, 200, {'Content_type' : 'application/json'}
    
    @jwt_required
    def put(self, id_feed):
        parser = reqparse.RequestParser()
        parser.add_argument('content', location = 'json')
        parser.add_argument('tag', location = 'json')
        parser.add_argument('image', location = 'json')
        args = parser.parse_args()
        
        qry = Feeds.query.get(id_feed)
        if qry is not None:
            if args['content'] is not None:
                qry.content = args['content']
            if args['tag'] is not None:
                qry.tag = args['tag']
            if args['image'] is not None:
                qry.attached_image = args['image']
                
            qry.updated_at = datetime.datetime.now()

            db.session.commit()

            feeds = marshal(qry, Feeds.response_field)
            users = Users.query.get(qry.id_user)
            feeds['user'] = marshal(users, Users.response_field)

            return feeds, 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Post Feed not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def delete(self, id_feed):
        qry = Feeds.query.get(id_feed)
        if qry is not None:
            qry_user = Users.query.get(qry.id_user)
            qry_user.post_count -= 1

            qry_comment = Comments.query.filter(Comments.id_feed == id_feed).delete()

            db.session.delete(qry)
            db.session.commit()
            return 'Deleted', 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Post Feed not found'}, 404, {'Content_type' : 'application/json'}

    def options(self, id_feed = None):
        return {}, 200

api.add_resource(FeedResource, '', '/<int:id_feed>')