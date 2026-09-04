from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.plugin.s3.crud.crud_storage import s3_storage_dao
from backend.plugin.s3.model import S3Storage
from backend.plugin.s3.utils.file_ops import delete_object, get_bytes, normalize_object_key, put_bytes


async def _require_default_storage(*, db: AsyncSession) -> S3Storage:
    """
    获取默认 S3 存储

    :param db: 数据库会话
    :return:
    """
    storage = await s3_storage_dao.get_default(db)
    if not storage:
        raise errors.RequestError(msg='未配置默认 S3 存储')
    return storage


async def write_text(*, db: AsyncSession, key: str, content: str) -> str:
    """
    写入文本对象

    :param db: 数据库会话
    :param key: 对象键
    :param content: 文本内容
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await _require_default_storage(db=db)
    return await put_bytes(storage, object_key, content.encode())


async def read_text(*, db: AsyncSession, key: str) -> str:
    """
    读取文本对象

    :param db: 数据库会话
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await _require_default_storage(db=db)
    try:
        return (await get_bytes(storage, object_key)).decode()
    except Exception:
        raise errors.NotFoundError(msg='对象不存在')


async def delete_text(*, db: AsyncSession, key: str) -> None:
    """
    删除文本对象

    :param db: 数据库会话
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await _require_default_storage(db=db)
    await delete_object(storage, object_key)


async def load_text(*, db: AsyncSession, object_key: str | None, fallback: str = '') -> str:
    """
    按对象键读取正文，没有对象键或对象不存在时返回回退内容

    :param db: 数据库会话
    :param object_key: 对象键
    :param fallback: 回退内容
    :return:
    """
    if not object_key:
        return fallback
    try:
        return await read_text(db=db, key=object_key)
    except errors.NotFoundError:
        return fallback
