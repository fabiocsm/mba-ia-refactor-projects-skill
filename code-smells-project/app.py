from flask import Flask
from flask_cors import CORS

import database
from config.settings import Settings
from middlewares.error_handler import register_error_handlers
from utils.logger import configure_logging, get_logger
from views import (
    admin_routes,
    health_routes,
    index_routes,
    pedido_routes,
    produto_routes,
    relatorio_routes,
    usuario_routes,
)


def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)

    configure_logging()
    CORS(app)

    database.init_app(app)
    register_error_handlers(app)

    app.register_blueprint(index_routes.bp)
    app.register_blueprint(produto_routes.bp)
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(pedido_routes.bp)
    app.register_blueprint(relatorio_routes.bp)
    app.register_blueprint(health_routes.bp)
    app.register_blueprint(admin_routes.bp)

    return app


app = create_app()

if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Servidor iniciado em http://%s:%s", app.config["HOST"], app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
