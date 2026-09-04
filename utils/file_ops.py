from opendal import AsyncOperator

from backend.common.exception import errors
from backend.plugin.s3.model import S3Storage

_SECRET_MASK = '****'


def is_masked_secret(value: str | None) -> bool:
    """
    判断密钥是否为脱敏值

    :param value: 密钥
    :return:
    """
    if value is None:
        return True
    text = value.strip()
    return not text or _SECRET_MASK in text


def normalize_object_key(key: str) -> str:
    """
    规范化对象键

    :param key: 对象键
    :return:
    """
    text = key.strip().lstrip('/')
    if not text or '..' in text.split('/'):
        raise errors.RequestError(msg='对象键非法')
    return text


def get_operator(s3_storage: S3Storage) -> AsyncOperator:
    """
    获取 S3 操作器

    :param s3_storage: S3 存储
    :return:
    """
    return AsyncOperator(
        's3',
        endpoint=s3_storage.endpoint,
        access_key_id=s3_storage.access_key,
        secret_access_key=s3_storage.secret_key,
        bucket=s3_storage.bucket,
        root=s3_storage.prefix or '/',
        region=s3_storage.region or 'us-east-1',
    )


async def put_bytes(s3_storage: S3Storage, key: str, data: bytes) -> str:
    """
    写入对象

    :param s3_storage: S3 存储
    :param key: 对象键
    :param data: 对象内容
    :return:
    """
    object_key = normalize_object_key(key)
    await get_operator(s3_storage).write(object_key, data)
    return object_key


async def get_bytes(s3_storage: S3Storage, key: str) -> bytes:
    """
    读取对象

    :param s3_storage: S3 存储
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    return bytes(await get_operator(s3_storage).read(object_key))


async def delete_object(s3_storage: S3Storage, key: str) -> None:
    """
    删除对象

    :param s3_storage: S3 存储
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    await get_operator(s3_storage).delete(object_key)


async def object_exists(s3_storage: S3Storage, key: str) -> bool:
    """
    判断对象是否存在

    :param s3_storage: S3 存储
    :param key: 对象键
    :return:
    """
    object_key = normalize_object_key(key)
    return bool(await get_operator(s3_storage).exists(object_key))


async def check_storage(s3_storage: S3Storage) -> None:
    """
    检查 S3 存储是否可用

    :param s3_storage: S3 存储
    :return:
    """
    await get_operator(s3_storage).check()
