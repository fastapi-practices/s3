import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enums import StatusType
from backend.common.model import Base, UniversalText, id_key


class S3Storage(Base):
    """S3 存储"""

    __tablename__ = 's3_storage'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), index=True, comment='存储名称')
    endpoint: Mapped[str] = mapped_column(sa.String(512), comment='终端节点')
    access_key: Mapped[str] = mapped_column(sa.String(512), comment='访问密钥')
    secret_key: Mapped[str] = mapped_column(sa.String(512), comment='密钥')
    bucket: Mapped[str] = mapped_column(sa.String(64), comment='存储桶')
    prefix: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='前缀')
    region: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='区域')
    status: Mapped[int] = mapped_column(default=StatusType.enable.value, comment='状态')
    is_default: Mapped[bool] = mapped_column(default=False, index=True, comment='是否默认')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='备注')
