
import logging
logging.basicConfig(level=logging.INFO)
from app.core.config import settings
from app.services.model_service import ModelService
from app.services.feature_service import load_feature_dataset

feature_cols = ModelService.load_feature_columns(settings.FEATURE_COLUMNS_PATH)
df = load_feature_dataset(feature_cols)
print('success', df.shape)

