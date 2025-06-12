import pandas as pd
from scripts.data_loader import load_data

def test_load_data_csv(tmp_path):
    X = pd.DataFrame({'a': [1,2,3], 'b':[4,5,6]})
    y = pd.Series([1,0,1])
    X_path = tmp_path/'X.csv'
    y_path = tmp_path/'y.csv'
    X.to_csv(X_path, index=False)
    y.to_csv(y_path, index=False)

    X_loaded, y_loaded = load_data(X_path, y_path)
    pd.testing.assert_frame_equal(X_loaded, X)
    pd.testing.assert_series_equal(y_loaded, y, check_names=False)
