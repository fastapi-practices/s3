from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.plugin.s3.crud.crud_storage import s3_storage_dao
from backend.plugin.s3.model import S3Storage
from backend.plugin.s3.utils.file_ops import delete_object, get_bytes, normalize_object_key, put_bytes, remove_prefix


async def require_storage(*, db: AsyncSession, storage_id: int | None = None) -> S3Storage:
    """
    获取指定 S3 存储，未指定时使用默认存储

    :param db: 数据库会话
    :param storage_id: S3 存储 ID
    :return:
    """
    if storage_id is None:
        storage = await s3_storage_dao.get_default(db)
        if not storage:
            raise errors.RequestError(msg='未配置默认 S3 存储')
        return storage
    storage = await s3_storage_dao.get(db, storage_id)
    if not storage:
        raise errors.NotFoundError(msg='S3 存储不存在')
    return storage


async def write_bytes(*, db: AsyncSession, key: str, data: bytes, storage_id: int | None = None) -> str:
    """
    写入二进制对象

    :param db: 数据库会话
    :param key: 对象键
    :param data: 对象内容
    :param storage_id: S3 存储 ID
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await require_storage(db=db, storage_id=storage_id)
    return await put_bytes(storage, object_key, data)


async def write_text(*, db: AsyncSession, key: str, content: str, storage_id: int | None = None) -> str:
    """
    写入文本对象

    :param db: 数据库会话
    :param key: 对象键
    :param content: 文本内容
    :param storage_id: S3 存储 ID
    :return:
    """
    return await write_bytes(db=db, key=key, data=content.encode(), storage_id=storage_id)


async def read_text(*, db: AsyncSession, key: str, storage_id: int | None = None) -> str:
    """
    读取文本对象

    :param db: 数据库会话
    :param key: 对象键
    :param storage_id: S3 存储 ID
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await require_storage(db=db, storage_id=storage_id)
    try:
        return (await get_bytes(storage, object_key)).decode()
    except Exception as exc:
        raise errors.NotFoundError(msg='对象不存在') from exc


async def delete_text(*, db: AsyncSession, key: str, storage_id: int | None = None) -> None:
    """
    删除文本对象

    :param db: 数据库会话
    :param key: 对象键
    :param storage_id: S3 存储 ID
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await require_storage(db=db, storage_id=storage_id)
    await delete_object(storage, object_key)


async def delete_prefix(*, db: AsyncSession, prefix: str, storage_id: int | None = None) -> None:
    """
    递归删除前缀下的全部对象

    :param db: 数据库会话
    :param prefix: 对象前缀
    :param storage_id: S3 存储 ID
    :return:
    """
    object_prefix = normalize_object_key(prefix)
    storage = await require_storage(db=db, storage_id=storage_id)
    await remove_prefix(storage, object_prefix)


async def load_text(
    *, db: AsyncSession, object_key: str | None, fallback: str = '', storage_id: int | None = None
) -> str:
    """
    按对象键读取正文，没有对象键或对象不存在时返回回退内容

    :param db: 数据库会话
    :param object_key: 对象键
    :param fallback: 回退内容
    :param storage_id: S3 存储 ID
    :return:
    """
    if not object_key:
        return fallback
    try:
        return await read_text(db=db, key=object_key, storage_id=storage_id)
    except errors.NotFoundError:
        return fallback
