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
    luas_tanah = db.Column(db.Integer)
    avg_panen = db.Column(db.Integer)
    jumlah_tanaman = db.Column(db.Integer)
    planted_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)

    response_field = {
        "id" : fields.Integer,
        "jenis_tanaman": fields.String,
        "luas_tanah" : fields.String,
        "avg_panen" : fields.String,
        "jumlah_tanaman" : fields.String,
        'planted_at' : fields.DateTime,
        'ready_at' : fields.DateTime
    }

    def __init__(self, id, jenis_tanaman, luas_tanah, avg_panen, jumlah_tanaman, planted_at, ready_at):
        self.id = id
        self.jenis_tanaman = jenis_tanaman
        self.luas_tanah = luas_tanah
        self.avg_panen = avg_panen
        self.jumlah_tanaman = jumlah_tanaman
        self.planted_at = planted_at
        self.ready_at = ready_at

    def __repr__(self):
        return f'<Analyze {self.id}>'

class AnalyzeResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('jenis_tanaman', location='args')
        args = parser.parse_args()

        analyze_qry = Analyze.query

        if args['jenis_tanaman'] is not None:
            dates = [29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18 ,17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
            output = []
            past_output_dates = []
            future_output_dates = []
            output_luas_tanah = []
            output_avg_panen = []
            counter = 0
            for date in dates:
                analyze_qry = Analyze.query
                yesterday = datetime.now().date() + timedelta(days=-date)
                tomorrow = datetime.now().date() + timedelta(days=counter)
                counter += 1
                past_output_dates.append(str(yesterday))
                future_output_dates.append(str(tomorrow))

                analyze_qry_first = analyze_qry.filter(Analyze.jenis_tanaman == args['jenis_tanaman']).filter(Analyze.planted_at.like("%"+str(yesterday)+"%")).order_by(Analyze.id.desc()).first()
                analyze_qry_all = analyze_qry.filter(Analyze.jenis_tanaman == args['jenis_tanaman']).filter(Analyze.ready_at.like("%"+str(tomorrow)+"%")).order_by(Analyze.id.desc()).all()

                # counter2 = 0
                # for element in range(0, 30):
                #     yesterday_min1 = datetime.now().date() + timedelta(days=-(element+counter2))
                #     before_analyze_qry_first = analyze_qry.filter(Analyze.jenis_tanaman == args['jenis_tanaman']).filter(Analyze.planted_at.like("%"+str(yesterday_min1)+"%")).order_by(Analyze.id.desc()).first()
                #     if before_analyze_qry_first is not None:
                #         break
                #     else:
                #         counter2 += 1
                
                # return {"test": marshal(before_analyze_qry_first, Analyze.response_field)}

                total = 0
                for element in analyze_qry_all:
                    total += element.avg_panen

                output_avg_panen.append(total)

                output.append(analyze_qry_first)

                if analyze_qry_first is not None:
                    output_luas_tanah.append(analyze_qry_first.luas_tanah)
                else:
                    # if before_analyze_qry_first is not None:
                    #     output_luas_tanah.append(before_analyze_qry_first.luas_tanah)
                    # else:
                    #     counter2 += 1
                    #     yesterday_min1 = datetime.now().date() + timedelta(days=-(element+counter2))
                    #     before_analyze_qry_first = analyze_qry.filter(Analyze.jenis_tanaman == args['jenis_tanaman']).filter(Analyze.planted_at.like("%"+str(yesterday_min1)+"%")).order_by(Analyze.id.desc()).first()


                    output_luas_tanah.append(0)

        return {'past_output_dates': past_output_dates, 'future_output_dates': future_output_dates, 'luas_tanah': output_luas_tanah, 'avg_panen': output_avg_panen, 'data': marshal(output, Analyze.response_field)}, 200, {'Content_type' : 'application/json'}

    def options(self):
        return {}, 200

api.add_resource(AnalyzeResource, '')