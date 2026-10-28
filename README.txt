# CAM-1 — Intelligent Screening Platform for Co-Amorphous Materials

CAM-1 is a lightweight web application (Flask + HTML/CSS/JS) for predicting the possibility of forming a co-amorphous material from two compounds, and generating a structured molecular interaction analysis powered by GLM.

## Features

- **Co-amorphous formation prediction** from two SMILES inputs, a preparation method, and a weight ratio
- **Deep molecular analysis** across six dimensions (electrostatic, π-π, hydrogen bonding, hydrophobic, thermodynamics/phase behavior, kinetics) using GLM
- **Simple web UI** served by Flask (no separate frontend build step)
- **API endpoints** for prediction, analysis, and chat

## Tech Stack

- Backend: Python, Flask
- ML inference: joblib, scikit-learn (feature selector), XGBoost model artifact (loaded via joblib)
- Chemistry: RDKit (optional but recommended; regex fallback exists for SMILES validation)
- LLM: GLM API (`glm-4-flash`)
- Frontend: HTML + CSS + vanilla JavaScript (`fetch`)

## Project Structure

```
.
├─ app.py
├─ controllers/
│  ├─ predict_controller.py
│  ├─ analyze_controller.py
│  └─ chat_controller.py
├─ services/
│  ├─ preprocess_service.py
│  ├─ ml_service.py
│  └─ glm_service.py
├─ templates/
│  └─ index.html
├─ static/
│  └─ style.css
├─ tests/
│  ├─ test_api.py
│  └─ test_preprocess.py
├─ requirements.txt
├─ feature_selector.joblib
├─ XGB_clean_best.joblib
├─ optimal_thresholds.json
├─ Knowledge base.docx
└─ Molecular descriptor calculation and variable construction.py
```

## Requirements

- Python 3.9+ recommended
- Network access to the GLM API (for `/analyze` and `/chat`)
- OS that supports **UTF-8 filenames** (this repo includes Chinese filenames used at runtime)

## Quick Start (Local)

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

Create a `.env` file in the project root:

```env
GLM_API_KEY=your_glm_api_key_here
```

Notes:
- `.env` is intentionally ignored by git. Do not commit secrets.
- If `GLM_API_KEY` is missing, `/analyze` and `/chat` will return an error.

5. Start the server:

```bash
python app.py
```

Then open:

- http://127.0.0.1:5000/

## Using the Web UI

1. Enter **Compound 1 SMILES** and **Compound 2 SMILES**
2. Choose a **Preparation Method**:
   - Solvent Method
   - Melt Method
3. Enter **Weight Ratio** (> 0)
4. Click **Start Prediction & Analysis**

The right panel will show:
- Prediction (can/cannot form co-amorphous material) with probability
- A structured GLM analysis (six dimensions)

## API Reference

Base URL (local): `http://127.0.0.1:5000`

### `POST /predict`

Request body:

```json
{
  "smiles1": "CC(=O)OC1=CC=CC=C1C(=O)O",
  "smiles2": "C1=CC=C(C=C1)C(=O)O",
  "method": 1,
  "ratio": 1.0
}
```

Response:

```json
{
  "prediction": 1,
  "probability": 0.873,
  "message": "..."
}
```

### `POST /analyze`

Request body:

```json
{
  "smiles1": "CC(=O)OC1=CC=CC=C1C(=O)O",
  "smiles2": "C1=CC=C(C=C1)C(=O)O",
  "prediction": 1
}
```

Response:

```json
{
  "analysis": {
    "electrostatic": "...",
    "pi_pi_interaction": "...",
    "hydrogen_bond": "...",
    "hydrophobic_interaction": "...",
    "thermodynamics": "...",
    "kinetics": "..."
  }
}
```

### `POST /chat`

Request body:

```json
{
  "query": "What is a co-amorphous material?"
}
```

Response:

```json
{
  "answer": "..."
}
```

## Model and Data Files

The backend expects these files in the project root:

- `feature_selector.joblib` — feature selection/transformer
- `XGB_clean_best.joblib` — trained model artifact
- `optimal_thresholds.json` — optional; falls back to 0.5 if missing
- `Molecular descriptor calculation and variable construction.py` — preprocessing module used to generate model features
- `Knowledge base.docx` — domain knowledge base used for GLM analysis

If any required artifact is missing, the API will return an error message (for example, “model missing”).

## Running Tests

```bash
python -m pytest -q
```



