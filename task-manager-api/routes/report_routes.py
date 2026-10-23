from flask import Blueprint, jsonify, request

from controllers import category_controller, report_controller
from utils.validators import validate_category_create_payload, validate_category_update_payload

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(report_controller.summary_report()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return jsonify(report_controller.user_report(user_id)), 200


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(category_controller.list_categories()), 200


@report_bp.route('/categories', methods=['POST'])
def create_category():
    payload = validate_category_create_payload(request.get_json(silent=True))
    return jsonify(category_controller.create_category(payload)), 201


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    updates = validate_category_update_payload(request.get_json(silent=True))
    return jsonify(category_controller.update_category(cat_id, updates)), 200


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    category_controller.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
