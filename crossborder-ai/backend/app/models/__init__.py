"""VeyaShip - 数据模型入口

所有模型集中导出，方便 Alembic 迁移检测和外部导入。
每新增一个模型，都要在这里注册。

Alembic 通过 from app.models import * 自动发现所有表结构变更。
"""

from app.models.user import User
from app.models.product import Product
from app.models.system_config import SystemConfig
from app.models.persona import Persona
from app.models.shopify_channel import ShopifyChannel
from app.models.batch_job import BatchJob

__all__ = ["User", "Product", "SystemConfig", "Persona", "ShopifyChannel", "BatchJob"]
