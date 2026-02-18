import os
import time
import json
import requests
from docx import Document
from dotenv import load_dotenv

load_dotenv()

KB_LOCAL_PATH = os.path.join(os.getcwd(), "共无定型物知识库.docx")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def get_knowledge_text():
    if not os.path.exists(KB_LOCAL_PATH):
        raise FileNotFoundError("knowledge not found")
    doc = Document(KB_LOCAL_PATH)
    parts = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            parts.append(t)
    return "\n".join(parts)

def _glm_key():
    return os.environ.get("GLM_API_KEY", "")

def _post_glm(messages):
    key = _glm_key()
    if not key:
        return {"error": "GLM API key not configured"}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": "glm-4-flash", "messages": messages}
    for i in range(3):
        try:
            r = requests.post(GLM_API_URL, headers=headers, data=json.dumps(payload), timeout=30)
            if r.status_code == 200:
                data = r.json()
                txt = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"text": txt}
            time.sleep(2)
        except Exception as e:
            time.sleep(2)
    return {"error": "GLM API call failed"}

def build_analysis_prompt(kb_text, s1, s2, pred):
    label = "can form co-amorphous" if pred == 1 else "cannot form co-amorphous"
    prompt = (
        f"As a pharmaceutical chemistry expert, based on the following domain knowledge and the fact that compound {s1} and compound {s2} {label}, "
        "provide a comprehensive analysis from six key dimensions: electrostatic interaction, π-π interaction, hydrogen bonding, hydrophobic interaction, thermodynamics & phase behavior, and kinetic control. "
        "For each dimension, explain the specific molecular mechanisms and provide detailed insights about why this interaction favors or prevents co-amorphous formation. "
        "Use scientific terminology and be specific about molecular features, functional groups, and physicochemical properties.\n\n"
        "Structure your response clearly with each dimension labeled:\n"
        "1. ELECTROSTATIC INTERACTION: [detailed analysis of charge distribution, dipole moments, ionic interactions]\n"
        "2. π-π INTERACTION: [analysis of aromatic rings, conjugated systems, stacking effects]\n"
        "3. HYDROGEN BOND: [specific H-bond donors/acceptors, bond strength, network formation]\n"
        "4. HYDROPHOBIC INTERACTION: [non-polar groups, water exclusion, entropy effects]\n"
        "5. THERMODYNAMICS & PHASE BEHAVIOR: [free energy, enthalpy/entropy, melting point depression]\n"
        "6. KINETIC CONTROL: [molecular mobility, diffusion rates, nucleation inhibition]\n\n"
        f"Knowledge base: {kb_text[:8000]}"
    )
    return prompt

def parse_comprehensive_analysis(response_text):
    """Parse the comprehensive analysis from GLM response using heading markers only"""
    sections = {
        "electrostatic": "No detailed analysis available",
        "pi_pi_interaction": "No detailed analysis available",
        "hydrogen_bond": "No detailed analysis available",
        "hydrophobic_interaction": "No detailed analysis available",
        "thermodynamics": "No detailed analysis available",
        "kinetics": "No detailed analysis available",
    }

    # Define strict heading markers (avoid generic keywords that cause early cutoffs)
    headings = {
        "electrostatic": ["ELECTROSTATIC INTERACTION:", "Electrostatic Interaction:", "静电相互作用:"],
        "pi_pi_interaction": ["π-π INTERACTION:", "PI-PI INTERACTION:", "Pi-Pi Interaction:", "π-π相互作用:"],
        "hydrogen_bond": ["HYDROGEN BONDING:", "HYDROGEN BOND:", "Hydrogen Bond:", "氢键:"],
        "hydrophobic_interaction": ["HYDROPHOBIC INTERACTION:", "Hydrophobic Interaction:", "疏水相互作用:"],
        "thermodynamics": ["THERMODYNAMICS & PHASE BEHAVIOR:", "Thermodynamics:", "热力学与相行为:"],
        "kinetics": ["KINETIC CONTROL:", "Kinetic Control:", "动力学控制:"],
    }

    # Map each found heading start to its dimension
    found_positions = []
    for dim, variants in headings.items():
        for h in variants:
            idx = response_text.find(h)
            if idx != -1:
                found_positions.append((idx, dim, h))
                break

    # Sort by position to compute boundaries
    found_positions.sort(key=lambda x: x[0])

    for i, (start_idx, dim, heading_text) in enumerate(found_positions):
        end_idx = len(response_text)
        if i + 1 < len(found_positions):
            end_idx = found_positions[i + 1][0]
        section_text = response_text[start_idx + len(heading_text):end_idx].strip()
        if len(section_text) > 10:
            sections[dim] = section_text

    return sections

def chat_with_glm(text):
    messages = [{"role": "user", "content": text}]
    res = _post_glm(messages)
    if res.get("error"):
        return {"error": res["error"]}
    
    response_text = res.get("text", "")
    if not response_text:
        return {"error": "Empty response from GLM"}
    
    # Parse comprehensive analysis
    analysis = parse_comprehensive_analysis(response_text)
    
    return {"analysis": analysis, "full_response": response_text}