import os
from flask import Flask

def make_application(environment):
    import footy.views
    if environment == "production":
        config_path = 'footy.config.ProdConfig'
    else:
        config_path = 'footy.config.DevConfig'
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_path)
    flask_app.register_blueprint(footy.views.footy_http)
    return flask_app

def make_production_application():
    env = os.getenv('FOOTY_ENV','production')
    return make_application(env)
