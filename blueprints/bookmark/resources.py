import json, logging
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
import datetime
from sqlalchemy import desc

from . import *
from blueprints.users import *
from blueprints.PostFeed import *

from blueprints.comments import *
from blueprints.feedLike import *
from blueprints.commentLike import *

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
            parser.add_argument('rp', type = int, location = 'args', default = 100)
            parser.add_argument('search', location = 'args')
            parser.add_argument('sort', location='args', choices=('desc','asc'))
            args = parser.parse_args()

            offsets = (args['p'] * args['rp']) - args['rp']
            
            # qry = Bookmark.query

            # rows = []
            # for row in qry.limit(args['rp']).offset(offsets).all():
            #     bookmarks = marshal(row, Bookmark.response_field)
            #     feeds = Feeds.query.get(row.id_feed)
            #     bookmarks['feed'] = marshal(feeds, Feeds.response_field)
            #     feedLike = FeedLike.query.filter(FeedLike.id_feed == row.id_feed)
            #     # rowFeedLike = []
            #     # for row in feedLike:
            #     #     feedlike = marshal(row, FeedLike.response_field)
            #     #     rowFeedLike.append(feedlike)
            #     bookmarks['feed_like'] = marshal(feedLike, FeedLike.response_field)
            #     users = Users.query.get(row.id_user)
            #     bookmarks['user'] = marshal(users, Users.response_field)
            #     rows.append(bookmarks)
            # return rows, 200, {'Content_type' : 'application/json'}
            qry = Bookmark.query.filter(Bookmark.id_user == jwtClaims['id'])

            rows = []
            for row in qry.limit(args['rp']).offset(offsets).all():
                bookmarks = marshal(row, Bookmark.response_field)
                # feeds = Feeds.query.get(row.id_feed)
                # bookmarks['feed'] = marshal(feeds, Feeds.response_field)
                # bookmarks['feed_like'] = marshal(feedLike, FeedLike.response_field)
                # users = Users.query.get(row.id_user)
                # bookmarks['user'] = marshal(users, Users.response_field)

                qry = Feeds.query.get(row.id_feed)
            
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
                    comment = marshal(row, Comments.response_field)
                    # TEST
                    # commentLike = CommentsLike.query.filter(CommentsLike.id_comment == row.id)
                    # rowCommentLike = []
                    # for row in commentLike:
                    #     likeOfComment = marshal(row, CommentsLike.response_field)
                    #     rowCommentLike.append(likeOfComment)
                    # feedComment = Comments.query.filter(Comments.id_feed==qry.id_feed)
                    # TEST
                    # # commentLike = CommentsLike.query
                    # commentLike = CommentsLike.query.filter_by(id_comment = row.id).all()
                    # # commentLike = marshal(CommentsLike.query.filter(CommentsLike.id_comment==row.id), CommentsLike.response_field)
                    # # commentBy = Users.query.get(row.id_user)
                    # totalLike = []
                    # for rows in commentLike:
                    #     temp = marshal(rows, CommentsLike.response_field)
                    #     totalLike.append(temp)
                    # comment['like'] = rowCommentLike
                    comment['comment_by'] = marshal(Users.query.get(row.id_user), Users.response_field)
                    rowComment.append(comment)

                feeds['user'] = marshal(users, Users.response_field)
                feeds['like'] = rowFeedLike
                feeds['total_likes'] = len(rowFeedLike)
                feeds['comment'] = rowComment
                feeds['total_comment'] = len(rowComment)
                # return feeds, 200, {'Content_type' : 'application/json'}

                bookmarks['feed_content'] = feeds
                rows.append(bookmarks)
            return rows, 200, {'Content_type' : 'application/json'}

        else:
            qry = Bookmark.query.get(id_bookmark)
            if qry is not None:
                bookmarks = marshal(qry, Bookmark.response_field)
                # feeds = Feeds.query.get(qry.id_feed)
                # bookmarks['feed'] = marshal(feeds, Feeds.response_field)
                feedQry = Feeds.query.get(qry.id_feed)
            
                feeds = marshal(feedQry, Feeds.response_field)
                users = Users.query.get(feedQry.id_user)
                feedLike = FeedLike.query.filter(FeedLike.id_feed == feedQry.id_feed)
                rowFeedLike = []
                for row in feedLike:
                    feedlike = marshal(row, FeedLike.response_field)
                    rowFeedLike.append(feedlike)
                feedComment = Comments.query.filter(Comments.id_feed==feedQry.id_feed)
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
                feeds['total_likes'] = len(rowFeedLike)
                feeds['comment'] = rowComment
                feeds['total_comment'] = len(rowComment)
                bookmarks['feed_content'] = feeds

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
        # return id_bookmark

        # qry = Bookmark.query.filter_by(id_feed = id_bookmark).filter(Bookmark.id_user == jwtClaims['id']).first()
        # qry = Bookmark.query.filter_by(id_feed = id_bookmark).filter(Bookmark.id_user == jwtClaims['id']).first()
        qry = Bookmark.query.get(id_bookmark)
        # return qry
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return 'Deleted', 200, {'Content_type' : 'application/json'}
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'Comment Like not found'}, 404, {'Content_type' : 'application/json'}

    def options(self, id_bookmark = None):
        return {}, 200

api.add_resource(BookmarkResources, '', '/<int:id_bookmark>')