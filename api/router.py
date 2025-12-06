from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.s3.api.v1.storage import router as business_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH, tags=['S3'])

v1.include_router(business_router, prefix='/s3')
