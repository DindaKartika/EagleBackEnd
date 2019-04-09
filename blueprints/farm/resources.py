import json, logging
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
from datetime import datetime, timedelta
from blueprints.users import *
from sqlalchemy import and_
import dateutil.parser

from . import *
from blueprints.users import *
from blueprints.analyze import *
from ast import literal_eval

from ast import literal_eval

bp_farm = Blueprint('farm', __name__)
api = Api(bp_farm)

class FarmResource(Resource):

    def __init__(self):
        pass

    def get(self, id_farm = None):
        if id_farm == None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type = int, location = 'args', default = 1)
            parser.add_argument('rp', type = int, location = 'args', default = 20)
            parser.add_argument('search', location = 'args')
            parser.add_argument('id_user', location = 'args')
            parser.add_argument('planted_at', location = 'args')
            parser.add_argument('ready_at', location = 'args')
            parser.add_argument('plant_type', location = 'args')
            parser.add_argument('address', location = 'args')
            parser.add_argument('city', location = 'args')
            parser.add_argument('category', location = 'args')
            parser.add_argument('status_lahan', location = 'args')
            parser.add_argument('status_tanaman', location = 'args')
            args = parser.parse_args()

            offsets = (args['p'] * args['rp']) - args['rp']
            qry = Farms.query

            if args['search'] is not None:
                qry = qry.filter(Farms.plant_type.like("%"+args['search']+"%"))
                if qry.first() is None:
                    qry = Farms.query.filter(Farms.deskripsi.like("%"+args['search']+"%"))
                    if qry.first() is None:
                        qry = Farms.query.filter(Farms.city.like("%"+args['search']+"%"))
                        if qry.first() is None:
                            return {'status': 'Not Found', 'message': 'Farm is not found'}, 404, {'Content-Type': 'application/json'}

            if args['id_user'] is not None:
                qry = qry.filter(Farms.id_user == args['id_user'])

            if args['plant_type'] is not None:
                qry = qry.filter(Farms.plant_type.like("%"+args['plant_type']+"%"))

            if args['planted_at'] is not None:
                datetime_object = dateutil.parser.parse(args['planted_at'])
                qry = qry.filter(and_(Farms.planted_at >= datetime_object, Farms.planted_at < datetime_object + timedelta(days=1)))
            
            if args['ready_at'] is not None:
                datetime_object = dateutil.parser.parse(args['ready_at'])
                qry = qry.filter(and_(Farms.ready_at >= datetime_object, Farms.ready_at < datetime_object + timedelta(days=1)))

            if args['address'] is not None:
                qry = qry.filter(Farms.address.like("%"+args['address']+"%"))
            
            if args['city'] is not None:
                qry = qry.filter(Farms.city.like("%"+args['city']+"%"))

            if args['category'] is not None:
                qry = qry.filter(Farms.category.like("%"+args['category']+"%"))

            if args['status_lahan'] is not None:
                qry = qry.filter(Farms.status_lahan.like("%"+args['status_lahan']+"%"))

            if args['status_tanaman'] is not None:
                qry = qry.filter(Farms.status_tanaman.like("%"+args['status_tanaman']+"%"))

            rows = []
            for row in qry.limit(args['rp']).offset(offsets).all():
                farms = marshal(row, Farms.response_field)
                users = Users.query.get(row.id_user)
                farms['user'] = marshal(users, Users.response_field)
                rows.append(farms)
            return rows, 200, {'Content_type' : 'application/json'}

        else:
            qry = Farms.query.get(id_farm)
            if qry is not None:
                farms = marshal(qry, Farms.response_field)
                users = Users.query.get(qry.id_user)
                farms['user'] = marshal(users, Users.response_field)
                return farms, 200, {'Content_type' : 'application/json'}
            else:
                return {'status' : 'NOT_FOUND'}, 404, {'Content_type' : 'application/json'}
   
    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims() ##  buat kalo butuh data klaim
        parser = reqparse.RequestParser()
        parser.add_argument('farm_size', type=int, location = 'json', required=True)
        parser.add_argument('coordinates', location = 'json', required=True)
        parser.add_argument('center', location = 'json', required=True)
        parser.add_argument('ketinggian', type=int, location = 'json', required=True)
        args = parser.parse_args()

        deskripsi = ""
        plant_type = ""
        planted_at = datetime.now()
        ready_at = datetime.now()
        address = ""
        city = ""
        photos = ""
        status_lahan = "tidak"
        status_tanaman = "dijual"
        perkiraan_panen = 0

        if args['farm_size'] > 0 and args['farm_size'] <= 100:
            category = "kecil"
        elif args['farm_size'] > 100 and args['farm_size'] <= 500:
            category = "sedang"
        elif args['farm_size'] > 500 and args['farm_size'] <= 1000:
            category = "besar"
        elif args['farm_size'] > 1000:
            category = "sangat besar"

        if args['ketinggian'] > 0 and args['ketinggian'] <= 700:
            zona = "zona iklim panas"
        elif args['ketinggian'] > 700 and args['ketinggian'] <= 1500:
            zona = "zona iklim sedang"
        elif args['ketinggian'] > 1500 and args['ketinggian'] <= 2500:
            zona = "zona iklim sejuk"
        elif args['ketinggian'] > 2500:
            zona = "zona iklim dingin"

        id_user = jwtClaims['id']
        created_at = datetime.now()
        updated_at = datetime.now()

        farms = Farms(None, id_user, deskripsi, plant_type, planted_at, ready_at, address, city, photos, args['farm_size'], category, args['coordinates'], args['center'], args['ketinggian'], perkiraan_panen, zona, status_lahan, status_tanaman, created_at, updated_at)
        db.session.add(farms)
        db.session.commit()

        farm = marshal(farms, Farms.response_field)
        users = Users.query.get(id_user)
        farm['user'] = marshal(users, Users.response_field)
        
        return farm, 200, {'Content_type' : 'application/json'}
    
    @jwt_required
    def put(self, id_farm):
        parser = reqparse.RequestParser()
        parser.add_argument('description', location = 'json')
        parser.add_argument('plant_type', location = 'json')
        parser.add_argument('planted_at', location = 'json')
        parser.add_argument('ready_at', location='json')
        parser.add_argument('address', location = 'json')
        parser.add_argument('city', location = 'json')
        parser.add_argument('photos', location = 'json')
        parser.add_argument('farm_size', location = 'json')
        parser.add_argument('category', location = 'json')
        parser.add_argument('coordinates', location = 'json')
        parser.add_argument('center', location = 'json')
        parser.add_argument('ketinggian', location = 'json')
        parser.add_argument('perkiraan_panen', location = 'json')
        parser.add_argument('zona', location = 'json')
        parser.add_argument('status_lahan', location = 'json')
        parser.add_argument('status_tanaman', location = 'json')
        args = parser.parse_args()

        qry = Farms.query.get(id_farm)
        if qry is not None:
            if args['description'] is not None:
                qry.deskripsi = args['description']

            if args['plant_type'] is not None:

                if args['plant_type'] == 'Jagung':
                    kilogram_per_hektar = 2655
                if args['plant_type'] == 'Kacang Hijau':
                    kilogram_per_hektar = 594
                if args['plant_type'] == 'Kacang Tanah':
                    kilogram_per_hektar = 572
                if args['plant_type'] == 'Kedelai':
                    kilogram_per_hektar = 625
                if args['plant_type'] == 'Padi':
                    kilogram_per_hektar = 2494
                if args['plant_type'] == 'Ubi':
                    kilogram_per_hektar = 6884
                if args['plant_type'] == 'Bawang Merah':
                    kilogram_per_hektar = 4723
                if args['plant_type'] == 'Bawang Putih':
                    kilogram_per_hektar = 4619
                if args['plant_type'] == 'Cabai':
                    kilogram_per_hektar = 3496
                if args['plant_type'] == 'Kacang Panjang':
                    kilogram_per_hektar = 3452
                if args['plant_type'] == 'Kangkung':
                    kilogram_per_hektar = 2944
                if args['plant_type'] == 'Kentang':
                    kilogram_per_hektar = 7826
                if args['plant_type'] == 'Mentimun':
                    kilogram_per_hektar = 5423
                if args['plant_type'] == 'Kubis':
                    kilogram_per_hektar = 8068
                if args['plant_type'] == 'Lobak':
                    kilogram_per_hektar = 3732
                if args['plant_type'] == 'Sawi':
                    kilogram_per_hektar = 5216
                if args['plant_type'] == 'Terung':
                    kilogram_per_hektar = 6196
                if args['plant_type'] == 'Tomat':
                    kilogram_per_hektar = 8794
                if args['plant_type'] == 'Wortel':
                    kilogram_per_hektar = 8906
                
                if qry.plant_type != "":
                    created_at = datetime.now()
                    updated_at = datetime.now()

                    before_analyze_qry = Analyze.query.filter(Analyze.jenis_tanaman == args['plant_type']).order_by(Analyze.id.desc()).first()
                    if before_analyze_qry is not None:
                        subs_analyze_qry = Analyze.query.filter(Analyze.jenis_tanaman == qry.plant_type).order_by(Analyze.id.desc()).first()
                        subs_analyze_qry.luas_tanah -= qry.farm_size
                        new_size = before_analyze_qry.luas_tanah + qry.farm_size
                        
                        total_berat_kg = (qry.farm_size * kilogram_per_hektar / 10000)
                        new_production = before_analyze_qry.avg_panen + total_berat_kg
                        analyze = Analyze(None, args['plant_type'], new_size, new_production, 0, created_at, updated_at)
                        
                        db.session.add(analyze)
                        db.session.commit()


                    else:
                        subs_analyze_qry = Analyze.query.filter(Analyze.jenis_tanaman == qry.plant_type).order_by(Analyze.id.desc()).first()
                        subs_analyze_qry.luas_tanah -= qry.farm_size
                        total_berat_kg = (qry.farm_size * kilogram_per_hektar / 10000)
                        analyze = Analyze(None, args['plant_type'], qry.farm_size, total_berat_kg, 0, created_at, updated_at)
                        db.session.add(analyze)
                        db.session.commit()

                elif qry.plant_type == "":
                    created_at = datetime.now()
                    updated_at = datetime.now()

                    before_analyze_qry = Analyze.query.filter(Analyze.jenis_tanaman == args['plant_type']).order_by(Analyze.id.desc()).first()
                    if before_analyze_qry is not None:
                        new_size = before_analyze_qry.luas_tanah + qry.farm_size
                        total_berat_kg = (qry.farm_size * kilogram_per_hektar / 10000)
                        new_production = before_analyze_qry.avg_panen + total_berat_kg
                        analyze = Analyze(None, args['plant_type'], new_size, new_production, 0, created_at, updated_at)
                        db.session.add(analyze)
                        db.session.commit()

                    else:
                        total_berat_kg = (qry.farm_size * kilogram_per_hektar / 10000)
                        analyze = Analyze(None, args['plant_type'], qry.farm_size, total_berat_kg, 0, created_at, updated_at)
                        db.session.add(analyze)
                        db.session.commit()

                qry.plant_type = args['plant_type']
            
                
            if args['planted_at'] is not None:
                datetime_object = dateutil.parser.parse(args['planted_at'])
                qry.planted_at = datetime_object
            if args['ready_at'] is not None:
                datetimes_object = dateutil.parser.parse(args['ready_at'])
                qry.ready_at = datetimes_object
            if args['address'] is not None:
                qry.address = args['address']
            if args['city'] is not None:
                qry.city = args['city']
            if args['photos'] is not None:
                qry.photos = args['photos']
            if args['farm_size'] is not None:
                qry.farm_size = args['farm_size']
            if args['category'] is not None:
                qry.category = args['category']
            if args['coordinates'] is not None:
                qry.attached_coordinates = args['coordinates']
            if args['center'] is not None:
                qry.attached_center = args['center']
            if args['ketinggian'] is not None:
                qry.attached_ketinggian = args['ketinggian']
            if args['perkiraan_panen'] is not None:
                qry.perkiraan_panen = args['perkiraan_panen']
            if args['zona'] is not None:
                qry.attached_zona = args['zona']
            if args['status_lahan'] is not None:
                if args['status_lahan'] == 'true':
                    qry.status_lahan = 'dijual'
                elif args['status_lahan'] == 'false':
                    qry.status_lahan = 'tidak'
            if args['status_tanaman'] is not None:
                qry.attached_status_tanaman = args['status_tanaman']

            qry.updated_at = datetime.now()

            db.session.commit()

            farms = marshal(qry, Farms.response_field)
            users = Users.query.get(qry.id_user)
            farms['user'] = marshal(users, Users.response_field)

            return farms, 200, {'Content_type' : 'application/json'}

        else:
            return {'status' : 'NOT_FOUND', 'message' : 'ID not found'}, 404, {'Content_type' : 'application/json'}

    @jwt_required
    def delete(self, id_farm):
        qry = Farms.query.get(id_farm)
        if qry is not None:
            before_analyze_qry = Analyze.query.filter(Analyze.jenis_tanaman == qry.plant_type).first()
            before_analyze_qry.luas_tanah -= qry.farm_size

            db.session.delete(qry)
            db.session.commit()

            return 'Deleted', 200, {'Content_type' : 'application/json'}
            
        else:
            return {'status' : 'NOT_FOUND', 'message' : 'ID not found'}, 404, {'Content_type' : 'application/json'}

    def options(self, id_farm = None):
        return {}, 200

api.add_resource(FarmResource, '', '/<int:id_farm>')

class test(Resource):
    def get(self, id_farm = None):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type = int, location = 'args', default = 1)
        parser.add_argument('rp', type = int, location = 'args', default = 20)
        args = parser.parse_args()
        offsets = (args['p'] * args['rp']) - args['rp']
        qry = Farms.query
        
        rows = []
        for row in qry.limit(args['rp']).offset(offsets).all():
            farms = marshal(row, Farms.response_field)
            users = Users.query.get(row.id_user)
            farms['user'] = marshal(users, Users.response_field)
            rowrow = []
            rowrow.append(literal_eval(farms['coordinates']))
            rows.append(rowrow)
        return rows, 200, {'Content_type' : 'application/json'}
    
    def options(self, id_farm = None):
        return {}, 200

api.add_resource(test, '/test')