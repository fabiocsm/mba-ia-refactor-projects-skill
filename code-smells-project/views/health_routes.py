from flask import Blueprint, jsonify

from controllers import health_controller

bp = Blueprint("health", __name__)


@bp.route("/health", methods=["GET"])
def health_check():
    body, status_code = health_controller.status()
    return jsonify(body), status_code
