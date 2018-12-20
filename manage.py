import logging

from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models  # 之前迁移是因为模型类和迁移命令在一个py文件中

# 添加测试数据
# 1、进入到mysql中，并且使用需要添加数据的数据库
# 2、source .sql直接导入

# 通过不同的参数创建不同的app ---> 工厂方法
app = create_app("development")   # 已经和配置文件关联了
# 六、集成flask-script  flask-migrate
manager = Manager(app)
Migrate(app, db)  # 而这时候的db已经附有了灵魂
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    print(app.url_map)
    manager.run()