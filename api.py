from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api,reqparse,fields,marshal_with,abort
from werkzeug.security import generate_password_hash, check_password_hash
app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api=Api(app)
db=SQLAlchemy(app)

class UserModel(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),unique=True,nullable=False)
    email=db.Column(db.String(80),unique=True ,nullable=False)
    password=db.Column(db.String(80),nullable=False)

    # hash password
    def hash_password(self):
        self.password=generate_password_hash(self.password)
    # check password
    def check_password(self,password):
        return check_password_hash(self.password,password)

    def __repr__(self):
        return f"User(name={self.name} ,email={self.email} ,password={self.password})"
    
user_args=reqparse.RequestParser()
user_args.add_argument('name',type=str,required=True, help="Name cannot be blank")
user_args.add_argument('email',type=str,required=True,help="Email cannot be blank")
user_args.add_argument('password',type=str,required=True,help="Password cannot be blank")

login_args=reqparse.RequestParser()
login_args.add_argument('email',type=str,required=True,help="Email cannot be blank")
login_args.add_argument('password',type=str,required=True,help="Password Is Required")

userFields={
    'id':fields.Integer,
    'name':fields.String,
    'email':fields.String,
    
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users=UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        args=user_args.parse_args()
        user=UserModel(name=args.name,email=args.email,password=args.password)
        # hash password
        user.hash_password()
        # check password
        if not user.check_password(args.password):
            abort(400,"Password is incorrect")
        # check if user already exists

        existing_user=UserModel.query.filter_by(email=args.email).first()
        if existing_user:
            abort(400,"User already exists")
        # check if name already exists
        existing_user=UserModel.query.filter_by(name=args.name).first()
        if existing_user:
            abort(400,"User already exists")
        # check if email already exists
        existing_user=UserModel.query.filter_by(email=args.email).first()
        if existing_user:
            abort(400,"User already exists")
        db.session.add(user)
        db.session.commit()
        users=UserModel.query.all()
        return users,201

class User(Resource):
    @marshal_with(userFields)
    def get(self,id):
        user=UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404,"User not Found")
        return user
    
    @marshal_with(userFields)
    def patch(self,id):
        args=user_args.parse_args()
        user=UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404,"User not Found")
            return user
        user.name=args["name"]
        user.email=args["email"]
        user.password=args["password"]
        db.session.commit()
        return user
    
    @marshal_with(userFields)
    def delete(self,id):
        user=UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404,"User not Found")
            return user
        db.session.delete(user)
        db.session.commit()
        users=UserModel.query.all()
        return users,204
class Login(Resource):
    def post(self):
        args=login_args.parse_args()
        user=UserModel.query.filter_by(email=args.email).first()
        if not user:
            abort(404,"User not Found")
        if not user.check_password(args.password):
            abort(400,"Password is incorrect")
        return {"message": "Login successful", "user": user.name}, 200

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>', endpoint='user_by_id')
api.add_resource(Login, '/api/login/', endpoint='user_login')

@app.route('/')
def home():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)
