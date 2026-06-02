from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alert, commodity, dashboard, health, historical, prediction, statistics, insight, optimizer
from app.core.config import settings
from app.core.lifespan import lifespan

app = FastAPI(
    title="Pangan AI API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(commodity.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(historical.router, prefix="/api")
app.include_router(prediction.router, prefix="/api")
app.include_router(alert.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(insight.router, prefix="/api/ai")
app.include_router(optimizer.router, prefix="/api/optimizer")
