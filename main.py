import secrets

from flask import Flask, request
from flask_restful import Api, Resource, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
api = Api(app)
SQLALCHEMY_BINDS = {
    'mysqldb': 'mysql://root:new-password@localhost/flaskdb',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flaskuser:flask@localhost/flaskdb'
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
db = SQLAlchemy(app)


class PostgresModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"{self.name}"


class MySqlModel(db.Model):
    __bind_key__ = 'mysqldb'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"{self.name}"


resource_fields = {
    'id': fields.Integer,
    'name': fields.String
}


class PostgresDataView(Resource):
    @marshal_with(resource_fields)
    def get(self):
        result = PostgresModel.query.all()
        return result

    @marshal_with(resource_fields)
    def post(self):
        try:
            obj = PostgresModel(id=request.form['id'], name=request.form['name'])
            db.session.add(obj)
            db.session.commit()
            return obj, 201
        except Exception as e:
            abort(400, message="Object with this id already exists")


class MySqlDataView(Resource):
    @marshal_with(resource_fields)
    def get(self):
        result = MySqlModel.query.all()
        return result

    @marshal_with(resource_fields)
    def post(self):
        try:
            obj = MySqlModel(id=request.form['id'], name=request.form['name'])
            db.session.add(obj)
            db.session.commit()
            return obj, 201
        except Exception as e:
            abort(400, message="Object with this id already exists")


api.add_resource(PostgresDataView, "/postgres-data/")
api.add_resource(MySqlDataView, "/mysql-data/")
if __name__ == "__main__":
    app.run(debug=True)
