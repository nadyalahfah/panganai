import sys, json
sys.path.append('.')

import app.api.optimizer as opt
import app.services.catboost_prediction_service as cb

# Mock the catboost service so it returns fake predictions for testing
def mock_get_preds(state, slug):
    return [
        {"provinsi": "JAWA TIMUR", "harga_sekarang": 12000, "prediksi_7h": 12100, "ubah_7_pct": 0.8},
        {"provinsi": "PAPUA", "harga_sekarang": 15000, "prediksi_7h": 17000, "ubah_7_pct": 13.3},
        {"provinsi": "DKI JAKARTA", "harga_sekarang": 13000, "prediksi_7h": 14000, "ubah_7_pct": 7.6},
        {"provinsi": "SULAWESI SELATAN", "harga_sekarang": 11000, "prediksi_7h": 11500, "ubah_7_pct": 4.5}
    ]

cb.get_all_province_predictions_legacy_contract = mock_get_preds

# Mock resolve_komoditas_value
opt.resolve_komoditas_value = lambda df, k: "slug-" + k.lower().replace(" ", "-")

class MockState:
    df_semua = None
class MockApp:
    state = MockState()
class MockReq:
    app = MockApp()

req = MockReq()
try:
    res = opt.get_optimizer_routes(req)
    with open('test_out_utf8.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
