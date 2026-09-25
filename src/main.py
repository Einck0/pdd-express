"""
应用入口文件
创建 Flask 应用并启动服务。
"""

from app import create_app
from config import get_settings

settings = get_settings()
app = create_app()

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
