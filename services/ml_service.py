import json
import os
import joblib
import numpy as np
import pandas as pd

def _load_feature_selector():
    path = os.path.join(os.getcwd(), "feature_selector.joblib")
    if not os.path.exists(path):
        raise FileNotFoundError("feature selector missing")
    return joblib.load(path)

def _load_model():
    path = os.path.join(os.getcwd(), "XGB_clean_best.joblib")
    if not os.path.exists(path):
        raise FileNotFoundError("model missing")
    return joblib.load(path)

def _load_threshold():
    path = os.path.join(os.getcwd(), "optimal_thresholds.json")
    if not os.path.exists(path):
        return 0.5
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return float(data.get("optimal_threshold_f1", 0.5))

def predict_label(features_df):
    selector = _load_feature_selector()
    model = _load_model()
    X = selector.transform(features_df)

    exp_names = None
    try:
        # model could be a pipeline
        xgb = model.named_steps.get('xgb') if hasattr(model, 'named_steps') else model
        booster = xgb.get_booster()
        exp_names = booster.feature_names
    except Exception:
        exp_names = None

    if exp_names and len(exp_names) == X.shape[1]:
        X_input = pd.DataFrame(X, columns=exp_names)
    else:
        X_input = X
    try:
        proba = model.predict_proba(X_input)[:, 1][0]
    except Exception:
        try:
            import xgboost as xgb
            xgb_est = model.named_steps.get('xgb') if hasattr(model, 'named_steps') else None
            booster = xgb_est.get_booster() if xgb_est is not None else None
            dmat = xgb.DMatrix(X_input)
            proba = float(booster.predict(dmat)[0])
        except Exception as e:
            raise e
    thr = _load_threshold()
    label = 1 if proba >= thr else 0
    return label, float(proba)