"""
/api/history  endpoints
"""

from flask import Blueprint, jsonify
from extensions import db
from models import Conversion

history_bp = Blueprint("history", __name__)


@history_bp.route("/api/history", methods=["GET"])
def get_history():
    records = Conversion.query.order_by(Conversion.created_at.desc()).limit(100).all()
    return jsonify([r.to_dict() for r in records])


@history_bp.route("/api/history/<int:conv_id>", methods=["DELETE"])
def delete_history(conv_id):
    record = Conversion.query.get_or_404(conv_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Deleted successfully", "id": conv_id})
