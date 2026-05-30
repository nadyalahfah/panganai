from pydantic import BaseModel


class PredictionPoint(BaseModel):
    tanggal: str
    prediksi: float | None = None
    batas_bawah: float | None = None
    batas_atas: float | None = None


class PredictionResponse(BaseModel):
    ringkasan: dict
    harian: list[PredictionPoint]
