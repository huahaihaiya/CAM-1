from flask import Blueprint, request, jsonify
from services.preprocess_service import build_features, validate_smiles
from services.ml_service import predict_label

predict_bp = Blueprint("predict", __name__)

@predict_bp.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    smiles1 = data.get("smiles1", "").strip()
    smiles2 = data.get("smiles2", "").strip()
    method = data.get("method")
    ratio = data.get("ratio")

    if not smiles1 or not smiles2:
        return jsonify({"error": "SMILES不能为空"}), 400
    if not validate_smiles(smiles1) or not validate_smiles(smiles2):
        return jsonify({"error": "SMILES格式无效"}), 400
    if method not in [1, 2]:
        return jsonify({"error": "制备技术选择无效"}), 400
    try:
        ratio_val = float(ratio)
        if ratio_val <= 0:
            return jsonify({"error": "重量比必须大于0"}), 400
    except Exception:
        return jsonify({"error": "重量比必须为数值"}), 400

    try:
        features_df = build_features(smiles1, smiles2, ratio_val, method)
    except FileNotFoundError:
        return jsonify({"error": "预处理脚本缺失"}), 500
    except Exception as e:
        return jsonify({"error": f"预处理失败: {str(e)}"}), 500

    try:
        label, proba = predict_label(features_df)
        message = "能够形成共无定型物" if label == 1 else "不能形成共无定型物"
        return jsonify({"prediction": int(label), "probability": float(proba), "message": message}), 200
    except FileNotFoundError:
        return jsonify({"error": "模型文件缺失"}), 500
    except Exception as e:
        return jsonify({"error": f"预测失败: {str(e)}"}), 500