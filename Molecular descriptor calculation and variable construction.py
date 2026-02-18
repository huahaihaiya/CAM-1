import math
import pandas as pd

def _rdkit_available():
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
        return True
    except Exception:
        return False

def _compute_basic_descriptors(smiles):
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return _fallback_descriptors(smiles)
        return [
            Descriptors.MolWt(mol),
            Descriptors.HeavyAtomCount(mol),
            Descriptors.NumHAcceptors(mol),
            Descriptors.NumHDonors(mol),
            Descriptors.TPSA(mol),
            Crippen.MolLogP(mol),
            Crippen.MolMR(mol),
            Descriptors.NumRotatableBonds(mol),
            rdMolDescriptors.CalcNumAromaticRings(mol),
            rdMolDescriptors.CalcNumAliphaticRings(mol),
            rdMolDescriptors.CalcFractionCSP3(mol),
            rdMolDescriptors.CalcNumHeteroatoms(mol),
            rdMolDescriptors.CalcNumRings(mol),
            Descriptors.NHOHCount(mol),
            Descriptors.NOCount(mol),
        ]
    except Exception:
        return _fallback_descriptors(smiles)

def _fallback_descriptors(smiles):
    s = smiles or ""
    counts = {ch: s.count(ch) for ch in ["C","c","N","O","F","Cl","Br","S","P","=","(",")","[","]","#"]}
    length = len(s)
    digits = sum(ch.isdigit() for ch in s)
    vowels = sum(ch in "aeiou" for ch in s.lower())
    return [
        float(length),
        float(digits),
        float(vowels),
        float(counts.get("C",0)+counts.get("c",0)),
        float(counts.get("N",0)),
        float(counts.get("O",0)),
        float(counts.get("F",0)+counts.get("Cl",0)+counts.get("Br",0)),
        float(counts.get("S",0)),
        float(counts.get("P",0)),
        float(counts.get("=",0)),
        float(counts.get("(",0)+counts.get(")",0)),
        float(counts.get("[",0)+counts.get("]",0)),
        float(counts.get("#",0)),
        float(length % 10),
        float((counts.get("C",0)+counts.get("c",0)) - counts.get("O",0)),
    ]

def _pair_features(v1, v2):
    feats = []
    for a, b in zip(v1, v2):
        feats.extend([
            a + b,
            abs(a - b),
            (a * b),
            (a / (b + 1e-6)),
        ])
    return feats

def main(smiles1: str, smiles2: str, ratio: float, method: int) -> pd.DataFrame:
    d1 = _compute_basic_descriptors(smiles1)
    d2 = _compute_basic_descriptors(smiles2)
    pair = _pair_features(d1, d2)
    extra = [
        float(ratio),
        float(1.0 / (ratio + 1e-6)),
        float(method),
        float(1 if method == 1 else 0),
        float(1 if method == 2 else 0),
    ]
    vec = d1 + d2 + pair + extra
    if len(vec) < 65:
        vec.extend([0.0] * (65 - len(vec)))
    else:
        vec = vec[:65]
    cols = [f"f{i}" for i in range(65)]
    df = pd.DataFrame([vec], columns=cols)
    return df