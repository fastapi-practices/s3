from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile

from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession
from backend.plugin.s3.schema.file import GetS3ObjectDetail
from backend.plugin.s3.service.file_service import s3_file_service

router = APIRouter()


@router.post(
    '/upload',
    summary='S3 文件上传',
    dependencies=[
        Depends(RequestPermission('s3:file:upload')),
        DependsRBAC,
    ],
)
async def upload_s3_file(
    db: CurrentSession,
    file: Annotated[UploadFile, File()],
    storage: Annotated[int, Query(description='S3 存储 ID')],
) -> ResponseSchemaModel[GetS3ObjectDetail]:
    data = await s3_file_service.upload(db=db, storage_id=storage, file=file)
    return response_base.success(data=data)
