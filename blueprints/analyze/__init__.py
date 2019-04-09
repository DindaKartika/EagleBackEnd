from flask import Blueprint, Flask
import json
from flask_restful import Resource, Api, reqparse, marshal
from . import *
from blueprints import db
from blueprints.users import *
from blueprints.farm import *
from datetime import datetime, timedelta

bp_analyze = Blueprint('analyze', __name__)
api = Api(bp_analyze)

class Analyze(db.Model):
    __tablename__ = 'analyze'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jenis_tanaman = db.Column(db.String(255))
    # id_lahan = db.Column(db.Integer)
    # jumlah_user = db.Column(db.Integer)
    # jumlah_gender = db.Column(db.Integer)
    # avg_umur_user = db.Column(db.Integer)
    
    luas_tanah = db.Column(db.Integer)
    avg_panen = db.Column(db.Integer)
    jumlah_tanaman = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # cover_photo = db.Column(db.String(255))
    # gender = db.Column(db.String(20))
    # date_of_birth = db.Column(db.String(50))
    # address = db.Column(db.String(50))
    # phone_number = db.Column(db.String(50))
    # facebook_link = db.Column(db.String(50))
    # instagram_link = db.Column(db.String(50))
    # twitter_link = db.Column(db.String(50))
    # other_link = db.Column(db.String(50))
    # created_at = db.Column(db.String(50))
    # updated_at = db.Column(db.String(50))
    # post_count = db.Column(db.Integer)
    # job = db.Column(db.String(50))
    # status = db.Column(db.String(50))

    response_field = {
        "id" : fields.Integer,
        "jenis_tanaman": fields.String,
        # "id_lahan" : fields.Integer,
        # "jumlah_user" : fields.Integer,
        # "jumlah_gender" : fields.Integer,
        # "avg_umur_user" : fields.String,
        "luas_tanah" : fields.String,
        "avg_panen" : fields.String,
        "jumlah_tanaman" : fields.String,
        'created_at' : fields.DateTime,
        'updated_at' : fields.DateTime
        # "cover_photo" : fields.String,
        # "gender" : fields.String,
        # "date_of_birth" : fields.String,
        # "address" : fields.String,
        # "phone_number" : fields.String,
        # "facebook_link" : fields.String,
        # "instagram_link" : fields.String,
        # "twitter_link" : fields.String,
        # "other_link" : fields.String,
        # "created_at" : fields.String,
        # "updated_at": fields.String,
        # "post_count" : fields.Integer,
        # "job" : fields.String,
        # "status" : fields.String
    }

    def __init__(self, id, jenis_tanaman, luas_tanah, avg_panen, jumlah_tanaman, created_at, updated_at):
        self.id = id
        self.jenis_tanaman = jenis_tanaman
        # self.id_lahan = id_lahan
        # self.jumlah_user = jumlah_user
        # self.jumlah_gender = jumlah_gender
        # self.avg_umur_user = avg_umur_user
        self.luas_tanah = luas_tanah
        self.avg_panen = avg_panen
        self.jumlah_tanaman = jumlah_tanaman
        self.created_at = created_at
        # self.cover_photo = cover_photo
        # self.gender = gender
        # self.date_of_birth = date_of_birth
        # self.address = address
        # self.phone_number = phone_number
        # self.facebook_link = facebook_link
        # self.instagram_link = instagram_link
        # self.twitter_link = twitter_link
        # self.other_link = other_link
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.post_count = post_count
        # self.job = job
        # self.status = status

    def __repr__(self):
        return f'<Analyze {self.id}>'

class AnalyzeResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('jenis_tanaman', location='args')
        args = parser.parse_args()

        analyze_qry = Analyze.query

        if args['jenis_tanaman'] is not None:
            dates = [30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18 ,17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
            output = []
            output_dates = []
            output_luas_tanah = []
            output_avg_panen = []
            for date in dates:
                analyze_qry = Analyze.query
                yesterday = datetime.now().date() + timedelta(days=-date)
                output_dates.append(str(yesterday))
                analyze_qry = analyze_qry.filter(Analyze.jenis_tanaman == args['jenis_tanaman']).filter(Analyze.created_at.like("%"+str(yesterday)+"%")).order_by(Analyze.id.desc()).first()
                output.append(analyze_qry)

                if analyze_qry is not None:
                    output_luas_tanah.append(analyze_qry.luas_tanah)
                    output_avg_panen.append(analyze_qry.avg_panen)
                else:
                    output_luas_tanah.append(0)
                    output_avg_panen.append(0)

        

        return {'dates': output_dates, 'luas_tanah': output_luas_tanah, 'avg_panen': output_avg_panen, 'data': marshal(output, Analyze.response_field)}, 200, {'Content_type' : 'application/json'}

    def options(self):
        return {}, 200

api.add_resource(AnalyzeResource, '')