# 开发记录

## 环境搭建

创建一个新的虚拟环境

```Shell
conda create --name ai-fitness-service-env python=3.9
```

激活虚拟环境

```Shell
conda activate ai-fitness-service-env
```

查看当前终端使用的 Python 路径

```Shell
> which python3
/Users/kevin/miniconda3/envs/ai-fitness-service-env/bin/python3
```

设置 Vscode Python 解释器路径为`/Users/kevin/miniconda3/envs/ai-fitness-service-env/bin/python3`。

## 项目搭建

安装 pip 依赖

```Shell
pip install flask flask_sqlalchemy
```

> 提示：如果 pip 下载很慢，可以替换国内镜像源

```Shell
sudo vim ~/.pip/pip.conf
```

```Shell
[global]
timeout = 1000
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
extra-index-url = https://pypi.mirrors.ustc.edu.cn/simple/
                http://pypi.douban.com/simple/
                https://mirrors.aliyun.com/pypi/simple/
                http://pypi.mirrors.ustc.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn
        mirrors.aliyun.com
                pypi.mirrors.ustc.edu.cn
                pypi.douban.com
                pypi.mirrors.ustc.edu.cn
```

拷贝 GPT4 提供的代码

```Python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# 配置 SQLite 数据库路径
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# 定义你的数据模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.name for user in users])

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user added'})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'})
    return jsonify({'name': user.name, 'email': user.email})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
```
