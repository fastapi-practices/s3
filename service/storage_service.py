from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.enums import StatusType
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.s3.crud.crud_storage import s3_storage_dao
from backend.plugin.s3.model import S3Storage
from backend.plugin.s3.schema.storage import CreateS3StorageParam, DeleteS3StorageParam, UpdateS3StorageParam
from backend.plugin.s3.utils.file_ops import check_storage, is_masked_secret


class S3StorageService:
    """S3 存储服务类"""

    async def get_all(self, *, db: AsyncSession, status: int | None = None) -> Sequence[S3Storage]:
        """
        获取所有 S3 存储

        :param db: 数据库会话
        :param status: 状态
        :return:
        """
        return await s3_storage_dao.get_all(db, status=status)

    async def get(self, *, db: AsyncSession, pk: int) -> S3Storage:
        """
        获取 S3 存储

        :param db: 数据库会话
        :param pk: S3 存储 ID
        :return:
        """
        s3_storage = await s3_storage_dao.get(db, pk)
        if not s3_storage:
            raise errors.NotFoundError(msg='S3 存储不存在')
        return s3_storage

    async def get_default(self, *, db: AsyncSession) -> S3Storage:
        """
        获取默认 S3 存储

        :param db: 数据库会话
        :return:
        """
        s3_storage = await s3_storage_dao.get_default(db)
        if not s3_storage:
            raise errors.NotFoundError(msg='未配置默认 S3 存储')
        return s3_storage

    async def get_list(
        self,
        *,
        db: AsyncSession,
        name: str | None,
        region: str | None,
        status: int | None,
    ) -> dict[str, Any]:
        """
        获取 S3 存储列表

        :param db: 数据库会话
        :param name: 存储名称
        :param region: 区域
        :param status: 状态
        :return:
        """
        s3_storage_select = await s3_storage_dao.get_select(name, region, status)
        return await paging_data(db, s3_storage_select)

    async def create(self, *, db: AsyncSession, obj: CreateS3StorageParam) -> None:
        """
        创建 S3 存储

        :param db: 数据库会话
        :param obj: 创建 S3 存储参数
        :return:
        """
        name = obj.name.strip()
        endpoint = obj.endpoint.strip()
        access_key = obj.access_key.strip()
        secret_key = obj.secret_key.strip()
        bucket = obj.bucket.strip()
        if not name:
            raise errors.RequestError(msg='存储名称不能为空')
        if not endpoint:
            raise errors.RequestError(msg='终端节点不能为空')
        if not access_key:
            raise errors.RequestError(msg='访问密钥不能为空')
        if not secret_key:
            raise errors.RequestError(msg='密钥不能为空')
        if not bucket:
            raise errors.RequestError(msg='存储桶不能为空')
        if await s3_storage_dao.get_by_name(db, name):
            raise errors.ConflictError(msg='存储名称已存在')

        prefix = obj.prefix.strip() if obj.prefix else None
        region = obj.region.strip() if obj.region else None
        if obj.is_default:
            await s3_storage_dao.clear_default(db)
        await s3_storage_dao.create(
            db,
            obj.model_copy(
                update={
                    'name': name,
                    'endpoint': endpoint,
                    'access_key': access_key,
                    'secret_key': secret_key,
                    'bucket': bucket,
                    'prefix': prefix,
                    'region': region,
                }
            ),
        )

    async def update(self, *, db: AsyncSession, pk: int, obj: UpdateS3StorageParam) -> int:
        """
        更新 S3 存储

        :param db: 数据库会话
        :param pk: S3 存储 ID
        :param obj: 更新 S3 存储参数
        :return:
        """
        await self.get(db=db, pk=pk)
        name = obj.name.strip()
        endpoint = obj.endpoint.strip()
        bucket = obj.bucket.strip()
        if not name:
            raise errors.RequestError(msg='存储名称不能为空')
        if not endpoint:
            raise errors.RequestError(msg='终端节点不能为空')
        if not bucket:
            raise errors.RequestError(msg='存储桶不能为空')
        existed = await s3_storage_dao.get_by_name(db, name)
        if existed and existed.id != pk:
            raise errors.ConflictError(msg='存储名称已存在')

        payload = obj.model_dump()
        payload['name'] = name
        payload['endpoint'] = endpoint
        payload['bucket'] = bucket
        payload['prefix'] = obj.prefix.strip() if obj.prefix else None
        payload['region'] = obj.region.strip() if obj.region else None
        if is_masked_secret(obj.access_key):
            payload.pop('access_key', None)
        else:
            payload['access_key'] = obj.access_key.strip()
        if is_masked_secret(obj.secret_key):
            payload.pop('secret_key', None)
        else:
            payload['secret_key'] = obj.secret_key.strip()
        if obj.is_default:
            await s3_storage_dao.clear_default(db)
        return await s3_storage_dao.update(db, pk, payload)

    async def delete(self, *, db: AsyncSession, obj: DeleteS3StorageParam) -> int:
        """
        删除 S3 存储

        :param db: 数据库会话
        :param obj: S3 存储 ID 列表
        :return:
        """
        return await s3_storage_dao.delete(db, obj.pks)

    async def check(self, *, db: AsyncSession, pk: int) -> None:
        """
        检查 S3 存储是否可用

        :param db: 数据库会话
        :param pk: S3 存储 ID
        :return:
        """
        s3_storage = await self.get(db=db, pk=pk)
        if s3_storage.status != StatusType.enable.value:
            raise errors.RequestError(msg='S3 存储已停用')

        try:
            await check_storage(s3_storage)
        except Exception:
            raise errors.RequestError(msg='S3 存储连接失败')


s3_storage_service: S3StorageService = S3StorageService()
