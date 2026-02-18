from services.preprocess_service import validate_smiles, build_features

def test_validate_smiles_basic():
    assert validate_smiles('CCO')
    assert validate_smiles('c1ccccc1')
    assert not validate_smiles('???')

def test_build_features_shape():
    df = build_features('CCO', 'CCN', 1.5, 1)
    assert df.shape == (1, 65)