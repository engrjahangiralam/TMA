from flask import Flask

# Creating app object
app = Flask(__name__)

### Configurations ###
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tma.sqlite3'
app.config['SECRET_KEY'] = 'TheQuiCkBroWnFoXJumpsoVeRthElaZYDoG' #For session object to work

# To make app object available globally, .push() to activate it
app.app_context().push()

### Attaching Models ###
from application.models import *

### Connect db object with app object ###
db.init_app(app)
db.create_all()

## Create admin user ##
admin = User.query.filter_by(user_role = "admin").first()
if admin is None:
    admin = User(
        username = "admin",
        password = "admin",
        user_role = "admin",
        status = "active"
    )
    
    db.session.add(admin)
    db.session.commit()

### Attaching Controllers ###
from application.controllers import *

## Run the app
if __name__ == '__main__':
    app.run()