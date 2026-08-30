from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from api.incident_routes import incident_bp
from api.webhook_routes import webhook_bp
from api.health_routes import health_bp
from api.repo_routes import repo_bp

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"]
            }
        },
    )

    app.register_blueprint(incident_bp, url_prefix="/api/incidents")
    app.register_blueprint(webhook_bp, url_prefix="/api/webhooks")
    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(repo_bp, url_prefix="/api/repos")

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "bad_request",
            "message": str(error)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "not_found",
            "message": "Resource not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Unhandled application error")
        return jsonify({
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )