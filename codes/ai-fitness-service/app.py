import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# 配置 SQLite 数据库路径
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../../datas/db_planfit_res-20230719.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

# 定义 Resource 数据模型
class Resource(db.Model):
    __tablename__ = 'tb_res_zh'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part_name = db.Column(db.String, nullable=False)
    model_id = db.Column(db.String, nullable=False)
    item_name = db.Column(db.String, nullable=False)
    tag_text = db.Column(db.String)
    video_url = db.Column(db.String)
    content = db.Column(db.String)

    def to_json(self):
        return {
            'id': self.id,
            'part_name': self.part_name,
            'model_id': self.model_id,
            'item_name': self.item_name,
            'tag_text': self.tag_text,
            'video_url': self.video_url,
            'content': self.content
        }

@app.route('/resources', methods=['GET'])
def get_resources():
    resources = Resource.query.all()
    return jsonify([resource.to_json() for resource in resources])

@app.route('/resources/<string:model_id>', methods=['GET'])
def get_resource(model_id):
    resource = Resource.query.filter_by(model_id=model_id).first()
    if resource is None:
        return jsonify({'message': 'Resource not found'})
    return jsonify(resource.to_json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
