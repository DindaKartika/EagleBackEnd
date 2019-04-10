from flask import Blueprint, Flask
import json
from flask_restful import Resource, Api, reqparse, marshal
from . import *
from blueprints import db
from blueprints.users import *
from blueprints.farm import *
from datetime import datetime, timedelta

bp_analyzeKota = Blueprint('analyzeKota', __name__)
api = Api(bp_analyzeKota)

class AnalyzeKota(db.Model):
    __tablename__ = 'analyzeKota'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jenis_tanaman = db.Column(db.String(255))
    kota = db.Column(db.String(255))
    luas_tanah = db.Column(db.Integer)
    avg_panen = db.Column(db.Integer)
    planted_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)

    response_field = {
        "id" : fields.Integer,
        "jenis_tanaman": fields.String,
        "kota": fields.String,
        "luas_tanah" : fields.String,
        "avg_panen" : fields.String,
        'planted_at' : fields.DateTime,
        'ready_at' : fields.DateTime
    }

    def __init__(self, id, jenis_tanaman, kota, luas_tanah, avg_panen, planted_at, ready_at):
        self.id = id
        self.jenis_tanaman = jenis_tanaman
        self.kota = kota
        self.luas_tanah = luas_tanah
        self.avg_panen = avg_panen
        self.planted_at = planted_at
        self.ready_at = ready_at

    def __repr__(self):
        return f'<AnalyzeKota {self.id}>'

class AnalyzeKotaResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('jenis_tanaman', location='args')
        parser.add_argument('kota', location='args')
        args = parser.parse_args()

        analyze_kota_qry = AnalyzeKota.query

        users_qry = Users.query.all()
        total_user = 0
        for element in users_qry:  
            total_user += 1

        if args['jenis_tanaman'] is not None:
            dates = [29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18 ,17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
            output = []
            past_output_dates = []
            future_output_dates = []
            output_luas_tanah = []
            output_avg_panen = []
            counter = 0
            total_lahan = 0
            for date in dates:
                analyze_kota_qry = AnalyzeKota.query
                yesterday = datetime.now().date() + timedelta(days=-date)
                tomorrow = datetime.now().date() + timedelta(days=counter)
                counter += 1
                past_output_dates.append(str(yesterday))
                future_output_dates.append(str(tomorrow))

                analyze_kota_qry_first = analyze_kota_qry.filter(AnalyzeKota.jenis_tanaman == args['jenis_tanaman']).filter(AnalyzeKota.kota == args['kota']).filter(AnalyzeKota.planted_at.like("%"+str(yesterday)+"%")).order_by(AnalyzeKota.id.desc()).first()
                analyze_kota_qry_all = analyze_kota_qry.filter(AnalyzeKota.jenis_tanaman == args['jenis_tanaman']).filter(AnalyzeKota.kota == args['kota']).filter(AnalyzeKota.ready_at.like("%"+str(tomorrow)+"%")).order_by(AnalyzeKota.id.desc()).all()

                total = 0
                for element in analyze_kota_qry_all:
                    total += element.avg_panen

                output_avg_panen.append(total)

                output.append(analyze_kota_qry_first)

                if analyze_kota_qry_first is not None:
                    output_luas_tanah.append(analyze_kota_qry_first.luas_tanah)
                    total_lahan = analyze_kota_qry_first.luas_tanah
                else:
                    output_luas_tanah.append(0)
                    # total_lahan = 0

            total_panen = 0
            for element in output_avg_panen:
                total_panen += element

        return {'past_output_dates': past_output_dates, 'future_output_dates': future_output_dates, 'luas_tanah': output_luas_tanah, 'avg_panen': output_avg_panen, 'total_user': total_user, 'total_panen': total_panen, 'total_lahan': total_lahan, 'data': marshal(output, AnalyzeKota.response_field)}, 200, {'Content_type' : 'application/json'}

    def options(self):
        return {}, 200

api.add_resource(AnalyzeKotaResource, '')