from pydantic import Field

from backend.common.schema import SchemaBase


class GetS3ObjectDetail(SchemaBase):
    """S3 对象详情"""

    storage_id: int = Field(description='S3 存储 ID')
    key: str = Field(description='对象键')
