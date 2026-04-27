from flask import Flask
from config import configs
from web.dependencies.error_handler import register_error_handlers

def create_app(config_key):
    web = Flask(__name__)
    web.config.from_object(configs[config_key])

    register_error_handlers(web)

    from web.blueprints import main
    from web.blueprints import auth
    from web.blueprints import user

    web.register_blueprint(main)
    web.register_blueprint(auth)
    web.register_blueprint(user)

    return web