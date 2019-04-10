from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from time import strftime
import json, logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


### Konfigurasi database

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:alphatech123@localhost:3306/final_project'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ok:ok@localhost:3306/tanahair'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ok:ok@localhost:3306/tanahair_demo'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:bismillah@127.0.0.1:3306/final_project_edit_2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@0.0.0.0:3306/tanahair'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'SFsieaaBsLEpecP675r243faM8oSB2hV'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days = 1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# db.create_all()

### Catch 404 errors with catch_all_404s = True

api = Api(app, catch_all_404s = True)

### Middleware

@app.after_request
def after_request(response):
    if request.method == 'GET':
        app.logger.warning("REQUEST LOG\t%s%s", json.dumps({'request' : request.args.to_dict(), 'response' : json.loads(response.data.decode('utf-8'))}), request.method)
    else:    
        app.logger.warning("REQUEST LOG\t%s%s", json.dumps({'request' : request.get_json(), 'response' : json.loads(response.data.decode('utf-8'))}), request.method)
    return response

jwt = JWTManager(app)
@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity

from blueprints.auth import bp_auth
from blueprints.users.resources import bp_users
from blueprints.PostFeed.resources import bp_feed
from blueprints.feedLike.resources import bp_feedLike
from blueprints.comments.resources import bp_comments
from blueprints.commentLike.resources import bp_commentsLike
from blueprints.farm.resources import bp_farm
from blueprints.analyze import bp_analyze
from blueprints.bookmark.resources import bp_bookmark
from blueprints.analyzeKota import bp_analyzeKota

app.register_blueprint(bp_auth, url_prefix='/login')
app.register_blueprint(bp_users, url_prefix='/users')
app.register_blueprint(bp_feed, url_prefix='/feeds')
app.register_blueprint(bp_feedLike, url_prefix='/feedlikes')
app.register_blueprint(bp_comments, url_prefix='/comments')
app.register_blueprint(bp_commentsLike, url_prefix='/commentlikes')
app.register_blueprint(bp_farm, url_prefix='/farms')
app.register_blueprint(bp_analyze, url_prefix='/analyze')
app.register_blueprint(bp_bookmark, url_prefix='/bookmarks')
app.register_blueprint(bp_analyzeKota, url_prefix='/analyzekota')

db.create_all()
