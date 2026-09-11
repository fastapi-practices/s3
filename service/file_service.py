from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.enums import StatusType
from backend.common.exception import errors
from backend.core.conf import settings
from backend.plugin.s3.model import S3Storage
from backend.plugin.s3.schema.file import GetS3ObjectDetail
from backend.plugin.s3.service.storage_service import s3_storage_service
from backend.plugin.s3.utils.file_ops import delete_object, get_bytes, put_bytes
from backend.utils.file_ops import build_filename


class S3FileService:
    """S3 文件服务类"""

    @staticmethod
    async def _resolve_storage(*, db: AsyncSession, storage_id: int | None) -> S3Storage:
        """
        解析可用的 S3 存储，未指定时使用默认存储

        :param db: 数据库会话
        :param storage_id: S3 存储 ID
        :return:
        """
        if storage_id is None:
            return await s3_storage_service.get_default(db=db)
        s3_storage = await s3_storage_service.get(db=db, pk=storage_id)
        if s3_storage.status != StatusType.enable.value:
            raise errors.RequestError(msg='S3 存储已停用')
        return s3_storage

    async def upload(self, *, db: AsyncSession, storage_id: int, file: UploadFile) -> GetS3ObjectDetail:
        """
        上传文件到指定 S3 存储

        :param db: 数据库会话
        :param storage_id: S3 存储 ID
        :param file: 上传文件
        :return:
        """
        if not file.filename or not file.filename.strip():
            raise errors.RequestError(msg='文件名不能为空')
        if file.size is not None and file.size > settings.S3_UPLOAD_SIZE_MAX:
            raise errors.RequestError(msg='文件超出最大限制')
        contents = await file.read()
        if not contents:
            raise errors.RequestError(msg='文件内容不能为空')

        s3_storage = await self._resolve_storage(db=db, storage_id=storage_id)
        key = await put_bytes(s3_storage, f'uploads/{build_filename(file)}', contents)
        return GetS3ObjectDetail(storage_id=s3_storage.id, key=key)

    async def put_bytes(
        self,
        *,
        db: AsyncSession,
        key: str,
        data: bytes,
        storage_id: int | None = None,
    ) -> GetS3ObjectDetail:
        """
        写入对象，未指定存储时使用默认存储

        :param db: 数据库会话
        :param key: 对象键
        :param data: 对象内容
        :param storage_id: S3 存储 ID
        :return:
        """
        s3_storage = await self._resolve_storage(db=db, storage_id=storage_id)
        object_key = await put_bytes(s3_storage, key, data)
        return GetS3ObjectDetail(storage_id=s3_storage.id, key=object_key)

    async def get_bytes(self, *, db: AsyncSession, key: str, storage_id: int | None = None) -> bytes:
        """
        读取对象，未指定存储时使用默认存储

        :param db: 数据库会话
        :param key: 对象键
        :param storage_id: S3 存储 ID
        :return:
        """
        s3_storage = await self._resolve_storage(db=db, storage_id=storage_id)
        try:
            return await get_bytes(s3_storage, key)
        except Exception:
            raise errors.NotFoundError(msg='对象不存在')

    async def delete(self, *, db: AsyncSession, key: str, storage_id: int | None = None) -> None:
        """
        删除对象，未指定存储时使用默认存储

        :param db: 数据库会话
        :param key: 对象键
        :param storage_id: S3 存储 ID
        :return:
        """
        s3_storage = await self._resolve_storage(db=db, storage_id=storage_id)
        await delete_object(s3_storage, key)


s3_file_service: S3FileService = S3FileService()
