from flask import Blueprint, request, jsonify
from services.glm_service import chat_with_glm

chat_bp = Blueprint("chat", __name__)

@chat_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "查询不能为空"}), 400
    result = chat_with_glm(query)
    if result.get("error"):
        return jsonify({"error": result["error"]}), 500
    return jsonify({"answer": result.get("answer", "")}), 200