from fastapi import APIRouter, HTTPException, Request

from app.services.dataset_service import (
    get_harga_historis,
    resolve_komoditas_value,
    resolve_provinsi_value,
)

router = APIRouter()


@router.get("/harga-historis")
def get_harga_historis_endpoint(komoditas: str, provinsi: str, request: Request):
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    provinsi_resolved = resolve_provinsi_value(source_df, provinsi)
    if not komoditas_resolved or not provinsi_resolved:
        raise HTTPException(status_code=404, detail="Slug komoditas/provinsi tidak ditemukan")
    return get_harga_historis(request.app.state.df_semua, komoditas_resolved, provinsi_resolved)
