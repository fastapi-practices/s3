from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.s3.model import S3Storage


class CRUDS3Storage(CRUDPlus):
    """S3 存储数据库操作类"""


s3_storage_dao: CRUDS3Storage = CRUDS3Storage(S3Storage)
