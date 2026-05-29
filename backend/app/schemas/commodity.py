from pydantic import BaseModel


class CommodityPrediction(BaseModel):
    provinsi: str
    harga_sekarang: float | None = None
    prediksi_7h: float | None = None
    prediksi_30h: float | None = None
    tren_7h: str | None = None
    tren_30h: str | None = None
    ubah_7_pct: float | None = None
    ubah_30_pct: float | None = None
