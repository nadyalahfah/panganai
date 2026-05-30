from fastapi import APIRouter, Request

from app.services.dataset_service import (
    get_komoditas_objects,
    get_provinsi_objects,
)

router = APIRouter()


@router.get("/komoditas")
def get_komoditas_endpoint(request: Request):
    if hasattr(request.app.state, "cached_komoditas") and request.app.state.cached_komoditas:
        return request.app.state.cached_komoditas
        
    source_df = request.app.state.latest_feature_df if hasattr(request.app.state, "latest_feature_df") and request.app.state.latest_feature_df is not None else (request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua)
    return get_komoditas_objects(source_df)


@router.get("/provinsi")
def get_provinsi_endpoint(request: Request):
    if hasattr(request.app.state, "cached_provinsi") and request.app.state.cached_provinsi:
        return request.app.state.cached_provinsi
        
    source_df = request.app.state.latest_feature_df if hasattr(request.app.state, "latest_feature_df") and request.app.state.latest_feature_df is not None else (request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua)
    return get_provinsi_objects(source_df)
