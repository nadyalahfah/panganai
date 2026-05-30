from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException, Request

from app.services.dataset_service import (
    get_harga_historis_indexed,
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
    return get_harga_historis_indexed(request.app.state, komoditas_resolved, provinsi_resolved)


@router.post("/harga-historis/batch")
def get_harga_historis_batch(
    request: Request,
    payload: Dict[str, Any] = Body(
        ...,
        example={
            "items": [
                {"komoditas": "bawang-merah-ukuran-sedang", "provinsi": "aceh"},
                {"komoditas": "cabai-merah-keriting", "provinsi": "bali"},
            ],
            "limit_days": 90,
        },
    ),
):
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    items = payload.get("items", [])
    limit_days = payload.get("limit_days")
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="Body harus berisi items[]")

    results = {}

    for pair in items:
        komoditas_input = pair.get("komoditas")
        provinsi_input = pair.get("provinsi")
        komoditas_resolved = resolve_komoditas_value(source_df, komoditas_input)
        provinsi_resolved = resolve_provinsi_value(source_df, provinsi_input)
        key = f"{provinsi_input}::{komoditas_input}"

        if not komoditas_resolved or not provinsi_resolved:
            results[key] = []
            continue

        historis = get_harga_historis_indexed(
            request.app.state,
            komoditas_resolved,
            provinsi_resolved,
        )
        if isinstance(limit_days, int) and limit_days > 0:
            historis = historis[-limit_days:]
        results[key] = historis

    return {"results": results}
