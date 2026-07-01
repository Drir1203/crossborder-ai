"""VeyaShip - 系统配置模型

存储系统级别的配置项（如 API Key），
管理员在网页设置页面填写，存入数据库，无需改配置文件。
"""

from sqlalchemy import Column, DateTime, String, Text, func

from app.core.database import Base


class SystemConfig(Base):
    """系统配置表 —— 简单的 key-value 存储

    为什么用数据库存配置而不是 .env 文件？
    .env 文件适合开发者配的静态配置（数据库地址、密钥等），
    但 Onebound API Key 这类配置，管理员希望在网页上直接修改，
    不需要登录服务器、编辑文件、重启服务。

    这个表就是干这个用的：key 是配置名，value 是配置值。
    """

    __tablename__ = "system_config"

    # 主键就是 key，每个配置项一行
    # 比如: key="onebound_api_key", value="sk-xxx"
    key = Column(String(100), primary_key=True)
    # 配置值，Text 类型可以存较长内容
    value = Column(Text, nullable=True)
    # 记录最后修改时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
