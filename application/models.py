from flask_sqlalchemy import SQLAlchemy

### Creating db object ###
db = SQLAlchemy()

### Models ###

# Users basic information for authentication system
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique= True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    user_role = db.Column(db.String(255), nullable = False)
    status = db.Column(db.String(255), nullable = False, default = "deactive") ## Or active / blacklisted

# Staff Profile Information
class Staff(db.Model):
    __tablename__ = 'staffs'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False) ## Added to link User model
    full_name = db.Column(db.String(255), nullable = False)
    contact_no = db.Column(db.Integer, nullable = False)
    gender = db.Column(db.String(255), nullable = False) ## Added additionaly
    user = db.relationship('User')
    # status is not required as already used in the User model

# Trekker Profile Information
class Trekker(db.Model):
    __tablename__ = 'trekkers'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False) ## Added to link User model
    full_name = db.Column(db.String(255), nullable = False)
    contact_no = db.Column(db.Integer, nullable = False)
    gender = db.Column(db.String(255), nullable = False) ## Added additionaly
    user = db.relationship('User')
    # status is not required as already used in the User model

# Trek Information
class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key = True)
    trek_name = db.Column(db.String(255), nullable = False)
    location = db.Column(db.String(255), nullable = False)
    difficulty = db.Column(db.String(255), nullable = False) ## easy / medium / hard
    duration = db.Column(db.Integer, nullable = False) ## In days
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staffs.id'), nullable = False) ## Added to link Staff model
    status = db.Column(db.String(255), nullable = False, default = "deactive") ## (open / closed / completed
    start_date = db.Column(db.Date, nullable = False) ## Date in yyyy-mm-dd format
    end_date = db.Column(db.Date, nullable = False) ## Date in yyyy-mm-dd format
    total_slots = db.Column(db.Integer, nullable = False)
    trek_description = db.Column(db.String(300), nullable = False)
    trek_image_link = db.Column(db.String, nullable = False)

# Booking Information
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key = True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable = False)
    trekker_id = db.Column(db.Integer, db.ForeignKey('trekkers.id'), nullable = False)
    booking_date = db.Column(db.Date, nullable = False) ## Date in yyyy-mm-dd format
    status = db.Column(db.String(255), nullable = False) ## (booked / cancelled / completed)
    completion_date = db.Column(db.Date, nullable = True) ## Date in yyyy-mm-dd format, 
    # completion_date is nullable because we get completion date only after completion of a trek
    trek = db.relationship('Trek')
    trekker  = db.relationship('Trekker')
