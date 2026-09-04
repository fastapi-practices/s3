from anyio import Path, open_file
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.core.path_conf import UPLOAD_DIR
from backend.plugin.s3.crud.crud_storage import s3_storage_dao
from backend.plugin.s3.utils.file_ops import delete_object, get_bytes, normalize_object_key, put_bytes


def _local_path(key: str) -> Path:
    """
    获取本地回退路径

    :param key: 对象键
    :return:
    """
    return Path(UPLOAD_DIR / normalize_object_key(key))


async def write_text(*, db: AsyncSession, key: str, content: str) -> str:
    """
    写入文本对象，未配置默认存储时回退本地目录

    :param db: 数据库会话
    :param key: 对象键
    :param content: 文本内容
    :return:
    """
    object_key = normalize_object_key(key)
    data = content.encode()
    storage = await s3_storage_dao.get_default(db)
    if storage is None:
        path = _local_path(object_key)
        await path.parent.mkdir(parents=True, exist_ok=True)
        async with await open_file(path, 'wb') as fb:
            await fb.write(data)
        return object_key
    return await put_bytes(storage, object_key, data)


async def read_text(*, db: AsyncSession, key: str) -> str:
    """
    读取文本对象，未配置默认存储时回退本地目录

    :param db: 数据库会话
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await s3_storage_dao.get_default(db)
    if storage is None:
        path = _local_path(object_key)
        if not await path.is_file():
            raise errors.NotFoundError(msg='对象不存在')
        async with await open_file(path, 'rb') as fb:
            return (await fb.read()).decode()
    try:
        return (await get_bytes(storage, object_key)).decode()
    except Exception:
        raise errors.NotFoundError(msg='对象不存在')


async def delete_text(*, db: AsyncSession, key: str) -> None:
    """
    删除文本对象，未配置默认存储时回退本地目录

    :param db: 数据库会话
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    storage = await s3_storage_dao.get_default(db)
    if storage is None:
        path = _local_path(object_key)
        if await path.is_file():
            await path.unlink()
        return
    await delete_object(storage, object_key)


async def load_text(*, db: AsyncSession, object_key: str | None, fallback: str = '') -> str:
    """
    按对象键读取正文，没有对象键时返回回退内容

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
