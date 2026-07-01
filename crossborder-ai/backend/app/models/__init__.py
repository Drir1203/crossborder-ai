"""VeyaShip - 数据模型入口

所有模型集中导出，方便 Alembic 迁移检测和外部导入。
每新增一个模型，都要在这里注册。

Alembic 通过 from app.models import * 自动发现所有表结构变更。
"""

from app.models.user import User
from app.models.product import Product
from app.models.system_config import SystemConfig

# __all__ 控制 from app.models import * 时暴露哪些类
__all__ = ["User", "Product", "SystemConfig"]
