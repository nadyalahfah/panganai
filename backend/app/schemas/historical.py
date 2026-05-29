from pydantic import BaseModel


class HistoricalPoint(BaseModel):
    tanggal: str
    harga: float | None = None
    harga_nasional: float | None = None
    status_pasokan: str | None = None
