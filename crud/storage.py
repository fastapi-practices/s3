from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.s3.model import S3Storage
from backend.plugin.s3.schema.storage import CreateS3StorageParam, UpdateS3StorageParam
from backend.utils.timezone import timezone


class CRUDS3Storage(CRUDPlus[S3Storage]):
    async def get(self, db: AsyncSession, pk: int) -> S3Storage | None:
        """
        获取 S3 存储

        :param db: 数据库会话
        :param pk: S3 存储 ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_select(self, name: str | None, region: str | None) -> Select:
        """
        获取 S3 存储列表查询表达式

        :param name: 存储名称
        :param region: 区域
        :return:
        """
        filters = {'deleted': 0}

        if name is not None:
            filters['name__like'] = f'%{name}%'
        if region is not None:
            filters['region'] = region

        return await self.select_order('id', 'desc', **filters)

    async def get_all(self, db: AsyncSession) -> Sequence[S3Storage]:
        """
        获取所有 S3 存储

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db, deleted=0)

    async def create(self, db: AsyncSession, obj: CreateS3StorageParam) -> None:
        """
        创建 S3 存储

        :param db: 数据库会话
        :param obj: 创建S3 存储参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateS3StorageParam) -> int:
        """
        更新 S3 存储

        :param db: 数据库会话
        :param pk: S3 存储 ID
        :param obj: 更新 S3 存储参数
        :return:
        """
        return await self.update_model_by_column(db, obj, id=pk, deleted=0)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除 S3 存储

        :param db: 数据库会话
        :param pks: S3 存储 ID 列表
        :return:
        """
        return await self.delete_model_by_column(
            db,
            allow_multiple=True,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id__in=pks,
            deleted=0,
        )


s3_storage_dao: CRUDS3Storage = CRUDS3Storage(S3Storage)
