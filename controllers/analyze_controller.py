from flask import Blueprint, request, jsonify
from services.glm_service import get_knowledge_text, chat_with_glm, build_analysis_prompt

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.post("/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    smiles1 = data.get("smiles1", "").strip()
    smiles2 = data.get("smiles2", "").strip()
    prediction = data.get("prediction")

    if not smiles1 or not smiles2:
        return jsonify({"error": "SMILES cannot be empty"}), 400
    if prediction not in [0, 1]:
        return jsonify({"error": "Invalid prediction result"}), 400

    warning = None
    try:
        kb_text = get_knowledge_text()
    except Exception as e:
        kb_text = ""
        warning = "Knowledge base not accessible"

    # Build comprehensive analysis prompt
    prompt = build_analysis_prompt(kb_text, smiles1, smiles2, prediction)
    
    # Get detailed analysis from GLM
    result = chat_with_glm(prompt)

    if result.get("error"):
        return jsonify({"error": result["error"]}), 500

    # Extract analysis results
    analysis = result.get("analysis") or {}
    
    # Ensure all six dimensions have content
    default_analysis = {
        "electrostatic": "Analyzing charge distribution and electrostatic interactions between compounds...",
        "pi_pi_interaction": "Examining aromatic ring interactions and π-electron systems...",
        "hydrogen_bond": "Identifying hydrogen bond donors and acceptors...",
        "hydrophobic_interaction": "Assessing non-polar interactions and hydrophobic effects...",
        "thermodynamics": "Evaluating thermodynamic stability and phase behavior...",
        "kinetics": "Considering molecular mobility and kinetic factors..."
    }
    
    # Merge with actual analysis, replacing defaults where we have real content
    final_analysis = {}
    for key in default_analysis.keys():
        if key in analysis and analysis[key] and analysis[key] != "No detailed analysis available":
            final_analysis[key] = analysis[key]
        else:
            final_analysis[key] = default_analysis[key]

    resp = {"analysis": final_analysis, "full_response": result.get("full_response", "")}
    if warning:
        resp["warning"] = warning
    
    return jsonify(resp), 200