from typing import Annotated

from fastapi import APIRouter, Path

from backend.common.response.response_schema import ResponseSchemaModel
from backend.common.security.jwt import DependsJwtAuth
from backend.plugin.s3.schema.storage import GetS3StorageDetail

router = APIRouter()


@router.get('/{pk}', summary='获取 S3 存储详情', dependencies=[DependsJwtAuth])
async def get_s3_storage(
    pk: Annotated[int, Path(description='S3 存储 ID')],
) -> ResponseSchemaModel[GetS3StorageDetail]: ...
