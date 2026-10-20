from flask import Flask
from flask_cors import CORS

import database
from config.settings import Settings
from middlewares.error_handler import register_error_handlers
from utils.logger import configure_logging
from views import admin_routes, main_routes, pedido_routes, produto_routes, relatorio_routes, usuario_routes


def create_app(settings=Settings):
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app)

    database.init_app(app)
    register_error_handlers(app)

    app.register_blueprint(main_routes.bp)
    app.register_blueprint(produto_routes.bp)
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(pedido_routes.bp)
    app.register_blueprint(relatorio_routes.bp)
    app.register_blueprint(admin_routes.bp)

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://{Settings.HOST}:{Settings.PORT}")
    print("=" * 50)

    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
