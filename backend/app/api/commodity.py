from fastapi import APIRouter, Request

from app.services.dataset_service import (
    get_komoditas_objects,
    get_provinsi_objects,
)

router = APIRouter()


@router.get("/komoditas")
def get_komoditas_endpoint(request: Request):
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    return get_komoditas_objects(source_df)


@router.get("/provinsi")
def get_provinsi_endpoint(request: Request):
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    return get_provinsi_objects(source_df)
