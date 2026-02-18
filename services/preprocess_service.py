import importlib
import os
import re
import pandas as pd

def validate_smiles(s):
    try:
        from rdkit import Chem
        return Chem.MolFromSmiles(s) is not None
    except Exception:
        return bool(re.fullmatch(r"[A-Za-z0-9@+\-\[\]\(\)=#\/\\\.]+", s))

def build_features(smiles1, smiles2, ratio, method):
    module_name = "分子描述符计算及变量构造"
    module_path = os.path.join(os.getcwd(), f"{module_name}.py")
    if not os.path.exists(module_path):
        raise FileNotFoundError("missing preprocessor")
    mod = importlib.import_module(module_name)
    if hasattr(mod, "main"):
        result = mod.main(smiles1, smiles2, ratio, method)
        if isinstance(result, pd.DataFrame):
            train_path = os.path.join(os.getcwd(), "训练集_分层抽样无GNN.xlsx")
            try:
                if os.path.exists(train_path):
                    tdf = pd.read_excel(train_path)
                    expected = list(tdf.columns[3:68])
                    if len(expected) == result.shape[1]:
                        result.columns = expected
            except Exception:
                pass
            return result
        raise ValueError("preprocessor returned invalid format")
    raise ValueError("preprocessor entrypoint not found")