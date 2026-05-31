import urllib.request
import json
import traceback

def run():
    try:
        url = 'http://localhost:8000/api/dashboard/detail?komoditas=bawang-merah-ukuran-sedang&provinsi=aceh'
        res = urllib.request.urlopen(url)
        data = json.loads(res.read())
        
        historis = data.get('historis', [])
        prediksi = data.get('prediksi', {}).get('harian', [])
        
        if not historis or not prediksi:
            print("Missing data")
            return
            
        last_hist = historis[-1]
        first_pred = prediksi[0]
        
        print(f"Historical: {last_hist['tanggal']} - Rp {last_hist['harga']}")
        print(f"Forecast:   {first_pred['tanggal']} - Rp {first_pred['prediksi']}")
        
    except Exception as e:
        traceback.print_exc()

run()
