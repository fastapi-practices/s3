from pydantic import Field

from backend.common.schema import SchemaBase


class S3FileUploadQueryParam(SchemaBase):
    """S3 文件上传查询参数"""

    storage: int = Field(description='S3 存储 ID')


class GetS3ObjectDetail(SchemaBase):
    """S3 对象详情"""

    storage_id: int = Field(description='S3 存储 ID')
    key: str = Field(description='对象键')
