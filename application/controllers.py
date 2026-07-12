from flask import render_template, request, session, redirect, url_for

### Attaching current app object ###
from flask import current_app as app

### Attaching all models ###
from application.models import *

### Helper Function
def req_role(required_role):
    # Login Check
    if not session:
        return False
    # Role Check
    if session['user_role'] != required_role:
        return False


### Controllers Functions ###

## >> Home Page << ##
@app.route('/')
def index():
    if session:
        if session['user_role'] == "admin":
            return redirect('/adminDashboard')
        elif session['user_role'] == "staff":
            return redirect('/staffDashboard')
        elif session['user_role'] == "trekker":
            return redirect('/trekkerDashboard')
    else:
        return redirect(url_for('login'))


### Authentication System Start ###

## >> Login Page << ##
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if currently logged in
    if session:
        return redirect(url_for('logout'))

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username = username).first()
        if user:
            if password == user.password:
                session['username'] = user.username
                session['user_role'] = user.user_role
                session['status'] = user.status
                session['user_id'] = user.id

                if session['user_role'] == "admin":
                    return redirect('/adminDashboard')
                elif session['user_role'] == "staff":
                    if session['status'] == "active":
                        staff = Staff.query.filter_by(user_id = user.id).first()
                        session['full_name'] = staff.full_name
                        return redirect('/staffDashboard')
                    else:
                        session.clear()
                        return redirect(url_for('login', failed = "Account is " + user.status))
                elif session['user_role'] == "trekker":
                    if session['status'] == "active":
                        trekker = Trekker.query.filter_by(user_id = user.id).first()
                        session['full_name'] = trekker.full_name
                        return redirect('/trekkerDashboard')
                    else:
                        session.clear()
                        return redirect(url_for('login', failed = "Account is " + user.status))
                        #return f"User status is {session['status']}"                
            else:
                return redirect(url_for('login', failed = "Wrong password"))
        else:
            return redirect(url_for('login', failed = "Account not found"))
        
## >> Staff Signup Page << ##
@app.route('/staffSignup', methods=['GET', 'POST'])
def staff_signup():
    # Check if currently logged in
    if session:
        return redirect(url_for('logout'))

    if request.method == 'GET':
        return render_template('staffSignup.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_role = "staff"
        status = "deactive"

        full_name = request.form['full_name']
        contact_no = request.form['contact_no']
        gender = request.form['gender']

        # Checking if user already exists
        user = User.query.filter_by(username = username).first()
        if user:
            return redirect(url_for('login', failed = "User already exists"))
        else:
            user = User(
                username = username,
                password = password,
                user_role = user_role,
                status = status
            )
            db.session.add(user)
            db.session.flush() ## For getting user.id

            staff = Staff(
                full_name = full_name,
                contact_no = contact_no,
                user_id = user.id,
                gender = gender
            )
            db.session.add(staff)

            db.session.commit()
            return redirect(url_for('login', success = "User successfully created"))
    
## >> Trekker Signup Page << ##
@app.route('/trekkerSignup', methods=['GET', 'POST'])
def trekker_signup():
    # Check if currently logged in
    if session:
        return redirect(url_for('logout'))

    if request.method == 'GET':
        return render_template('trekkerSignup.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_role = "trekker"
        status = "active"

        full_name = request.form['full_name']
        contact_no = request.form['contact_no']
        gender = request.form['gender']

        # Checking if user already exists
        user = User.query.filter_by(username = username).first()
        if user:
            return redirect(url_for('login', failed = "User already exists"))
        else:
            user = User(
                username = username,
                password = password,
                user_role = user_role,
                status = status
            )
            db.session.add(user)
            db.session.flush() ## For getting user.id

            trekker = Trekker(
                full_name = full_name,
                contact_no = contact_no,
                user_id = user.id,
                gender = gender
            )
            db.session.add(trekker)

            db.session.commit()
            return redirect(url_for('login', success = "User successfully created"))
        
## >> Logout Founction << ##
@app.route('/logout')
def logout():
    session.clear() ## For clearing the session object
    return redirect(url_for('login'))

### Authentication System End ###



### Admin Dashboard Start ###

## >> Dashboard Page << ##
@app.route('/adminDashboard')
def admin_dashboard():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))
    
    # Total active Staffs
    staffs = Staff.query.join(User).filter(User.status == "active").all() 
    ## filter is used for flexibility to use multiple / different models
    staffs_active_count = len([staff for staff in staffs])

    # Total active Trekkers
    trekkers = Trekker.query.join(User).filter(User.status == "active").all() 
    ## filter is used for flexibility to use multiple / different models
    trekkers_active_count = len([trekker for trekker in trekkers])

    # Total treks
    treks = Trek.query.all()
    trek_count = len([trek for trek in treks])

    # Total active bookings
    bookings = Booking.query.all()
    active_booking_count = len([booking for booking in bookings if booking.status == "booked"])

    # Last three bookings
    last_three_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(3).all()
    
    return render_template('adminDashboard.html',
        staffs_active_count = staffs_active_count,
        trekkers_active_count = trekkers_active_count,
        trek_count = trek_count,
        active_booking_count = active_booking_count,
        last_three_bookings = last_three_bookings
        )

## >> Manage Treks Page << ##
@app.route('/adminManageTreks')
def admin_manage_treks():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))

    ## Getting Trek Objects
    treks = Trek.query.all()
    
    count_open = len([trek for trek in treks if trek.status =='open'])
    count_closed = len([trek for trek in treks if trek.status =='closed'])
    return render_template('adminManageTreks.html',
        treks = treks,
        count_open = count_open,
        count_closed = count_closed
        )

## >> Manage Treks Add << ##
@app.route('/adminManageTreks/add', methods =['GET', 'POST'])
def admin_manage_treks_add():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))


    if request.method == 'GET':
        staffs = Staff.query.join(User).filter(User.status == "active").all() 
        ## filter is used for flexibility to use multiple / different models
        return render_template('adminManageTreksAdd.html', staffs = staffs)
    
    if request.method == 'POST':
        from datetime import date 
        ## For handling form date string data into iso date object (YYYY-MM-DD)

        trek_name = request.form['trek_name']
        location = request.form['location']
        difficulty = request.form['difficulty']
        duration = request.form['duration']
        total_slots = request.form['total_slots']
        staff_id = request.form['staff_id']
        status = request.form['status']
        trek_description = request.form['trek_description']
        trek_image_link = request.form['trek_image_link']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Converting date string data into iso date object (YYYY-MM-DD)
        start_date_iso = date.fromisoformat(start_date)
        end_date_iso = date.fromisoformat(end_date)

        trek = Trek(
            trek_name = trek_name,
            location = location,
            difficulty = difficulty,
            duration = duration,
            total_slots = total_slots,
            start_date = start_date_iso,
            end_date = end_date_iso,
            assigned_staff_id = staff_id,
            status = status,
            trek_image_link = trek_image_link,
            trek_description = trek_description
        )

        db.session.add(trek)
        db.session.commit()
        return redirect(url_for('admin_manage_treks'))

## >> Manage Treks Edit << ##
@app.route('/adminManageTreks/edit/<int:trek_id>', methods =['GET', 'POST'])
def admin_manage_treks_edit(trek_id):
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))

    if request.method == 'GET':
        staffs = Staff.query.join(User).filter(User.status == "active").all() 
        ## filter is used for flexibility to use multiple / different models

        trek_data = Trek.query.filter_by(id = trek_id).first()
        if trek_data:

            # Getting participant Data
            bookings = Booking.query.join(Trekker).filter(Booking.trek_id == trek_id).all()
            participants_count = len(bookings)

            return render_template('adminManageTreksEdit.html',
                staffs = staffs,
                trek_data = trek_data,
                bookings = bookings,
                participants_count = participants_count
                )
        else:
            return "Invalid TrekID"
        
    if request.method == 'POST':
        from datetime import date 
        ## For handling form date string data into iso date object (YYYY-MM-DD)
        trek = Trek.query.filter_by(id = trek_id).first()

        trek.trek_name = request.form['trek_name']
        trek.location = request.form['location']
        trek.difficulty = request.form['difficulty']
        trek.duration = request.form['duration']
        trek.total_slots = request.form['total_slots']
        trek.assigned_staff_id = request.form['staff_id']
        trek.status = request.form['status']
        trek.trek_image_link = request.form['trek_image_link']
        trek.trek_description = request.form['trek_description']
        
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Converting date string data into iso date object (YYYY-MM-DD)
        trek.start_date = date.fromisoformat(start_date)
        trek.end_date = date.fromisoformat(end_date)

        if trek.status == 'completed' or trek.status == 'started':
            # Getting booking data
            bookings = Booking.query.filter_by(trek_id = trek_id).all()
            
            for booking in bookings:
                booking.status = trek.status
                if request.form['status'] == 'completed':
                    booking.completion_date = date.today() ## Current date as YYYY-MM-DD format
        
        db.session.commit()
        return redirect(url_for('admin_manage_treks'))

## >> Manage Treks Delete << ##
@app.route('/adminManageTreks/delete/<int:trek_id>', methods = ['GET', 'POST'])
def admin_manage_treks_delete(trek_id):
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))
    
    if request.method == 'GET':
        staffs = Staff.query.join(User).filter(User.status == "active").all() 
        ## filter is used for flexibility to use multiple / different models

        trek_data = Trek.query.filter_by(id = trek_id).first()
        if trek_data:

            # Getting participant Data
            bookings = Booking.query.join(Trekker).filter(Booking.trek_id == trek_id).all()
            participants_count = len(bookings)

            return render_template('adminManageTreksDelete.html',
                staffs = staffs,
                trek_data = trek_data,
                bookings = bookings,
                participants_count = participants_count
                )
        else:
            return "Invalid TrekID"

    if request.method == 'POST':
        trek = Trek.query.filter_by(id = trek_id).first()
        if trek:
            
            # Delete Booking Data
            bookings = Booking.query.filter_by(trek_id = trek_id).all()
            for booking in bookings:
                db.session.delete(booking)

            # Delete Trek
            db.session.delete(trek)

            db.session.commit()
            return redirect(url_for('admin_manage_treks'))
        else:
            return "Invalid TrekID"

## >> Manage Staffs Page << ##
@app.route('/adminManageStaff')
def admin_manage_staff():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))


    ## Getting Staff Objects
    staffs = Staff.query.all()
    
    count_deactive = len([staff for staff in staffs if staff.user.status =='deactive'])
    count_active = len([staff for staff in staffs if staff.user.status =='active'])
    count_blacklisted = len([staff for staff in staffs if staff.user.status =='blacklisted'])
    return render_template('adminManageStaff.html',
        staffs = staffs,
        count_deactive = count_deactive,
        count_active = count_active,
        count_blacklisted = count_blacklisted
        )

## >> Manage Staffs Actions << ##
@app.route('/adminManageStaff/<string:action>/<int:user_id>')
def admin_manage_staff_action(action, user_id):
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))


    user = User.query.filter_by(id = user_id).first()

    if action == "approve":
        user.status = "active"
        db.session.commit()
        return redirect(url_for('admin_manage_staff'))

    if action == "deactive":
        user.status = "deactive"
        db.session.commit()
        return redirect(url_for('admin_manage_staff', tabID=2))
    
    if action == "blacklist":
        user.status = "blacklisted"
        db.session.commit()
        return redirect(url_for('admin_manage_staff', tabID=2))
    
    if action == "active":
        user.status = "active"
        db.session.commit()
        return redirect(url_for('admin_manage_staff', tabID=3))
    
    if action == "delete":
        staff = Staff.query.filter_by(user_id = user_id).first()

        db.session.delete(staff)
        db.session.delete(user)

        db.session.commit()
        return redirect(url_for('admin_manage_staff', tabID=1))

## >> View Trekker Page << ##
@app.route('/adminViewTrekkers')
def admin_view_trekkers():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))


    ## Getting User Objects
    trekkers = Trekker.query.all()
    
    count_active = len([trekker for trekker in trekkers if trekker.user.status =='active'])
    count_blacklisted = len([trekker for trekker in trekkers if trekker.user.status =='blacklisted'])
    return render_template('adminViewTrekkers.html',
        trekkers = trekkers,
        count_active = count_active,
        count_blacklisted = count_blacklisted
        )

## >> Manage Trekker Actions << ##
@app.route('/adminManageTrekker/<string:action>/<int:user_id>')
def admin_manage_trekker_action(action, user_id):
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))


    user = User.query.filter_by(id = user_id).first()

    if action == "blacklist":
        user.status = "blacklisted"
        db.session.commit()
        return redirect(url_for('admin_view_trekkers'))
    
    if action == "active":
        user.status = "active"
        db.session.commit()
        return redirect(url_for('admin_view_trekkers', tabID=2))

## >> View All Bookings << ##
@app.route('/adminViewBookings')
def admin_view_bookings():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))

    # List of all bookings
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()

    return render_template('adminViewBookings.html', bookings = bookings)

## >> View / Manage Booking << ##
@app.route('/adminViewBookingDetails/<int:booking_id>', methods = ['GET', 'POST'])
def admin_view_booking_details(booking_id):
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))

    if request.method == 'GET':

        # Get booking data
        booking = Booking.query.filter_by(id = booking_id).first()

        if booking:
            return render_template('adminViewBookingDetails.html', booking = booking)
        else:
            return "Invalid BookingID"

    if request.method == 'POST':
        # Get booking data
        booking = Booking.query.filter_by(id = booking_id).first()

        if booking:
            # Delete booking data
            db.session.delete(booking)
            db.session.commit()

            return redirect(url_for('admin_view_bookings'))
        else:
            return "Invalid BookingID"

## >> Treks History << ##
@app.route('/adminTreksHistory')
def admin_treks_history():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))
    
    ## Getting Trek Objects
    treks = Trek.query.all()
    
    count_started = len([trek for trek in treks if trek.status =='started'])
    count_completed = len([trek for trek in treks if trek.status =='completed'])
    return render_template('adminTreksHistory.html',
        treks = treks,
        count_started = count_started,
        count_completed = count_completed
        )

## >> Search << ##
@app.route('/adminSearch', methods = ['GET', 'POST'])
def admin_search():
    # Authentication & Role Check
    auth = req_role('admin')
    if auth == False:
        return redirect(url_for('logout'))
    
    if request.method == 'GET':
        return render_template('adminSearch.html')
    
    if request.method == 'POST':
        q = request.form['q']

        ## Search for Treks
        treks = Trek.query.filter( (Trek.id == q) | (Trek.trek_name.ilike(f"%{q}%")) ).all()

        ## Search for Staffs
        staffs = Staff.query.filter( (Staff.id == q) | (Staff.full_name.ilike(f"%{q}%")) ).all()

        ## Search for Trekkers
        trekkers = Trekker.query.filter( (Trekker.id == q) | (Trekker.full_name.ilike(f"%{q}%")) ).all()

        return render_template('adminSearch.html', treks = treks, staffs = staffs, trekkers = trekkers)

### Admin Dashboard End ###



### Staff Dashboard Start ###

## >> Dashboard Page << ##
@app.route('/staffDashboard')
def staff_dashboard():
    # Authentication & Role Check
    auth = req_role('staff')
    if auth == False:
        return redirect(url_for('logout'))

    # Getting logged staff_id
    logged_user_id = session['user_id']
    staff = Staff.query.filter_by(user_id = logged_user_id).first()
    logged_staff_id = staff.id

    # Getting assigned trek objects
    assigned_treks = Trek.query.filter_by(assigned_staff_id = logged_staff_id).all()
    assigned_treks_count = len([trek for trek in assigned_treks])
    open_treks_count = len([trek for trek in assigned_treks if trek.status == 'open'])

    # For participant counts
    total_participants_count = 0
    for trek in assigned_treks:
        # Creating temporary arrtibute for each trek object
        trek.participant_count = Booking.query.filter_by(trek_id = trek.id).count()
        total_participants_count += trek.participant_count


    return render_template('staffDashboard.html',
        assigned_treks = assigned_treks,
        assigned_treks_count = assigned_treks_count,
        open_treks_count = open_treks_count,
        total_participants_count = total_participants_count
        )

## >> Staff My Treks Page << ##
@app.route('/staffMyTreks')
def staff_my_treks():
    # Authentication & Role Check
    auth = req_role('staff')
    if auth == False:
        return redirect(url_for('logout'))


    # Getting logged staff_id
    logged_user_id = session['user_id']
    staff = Staff.query.filter_by(user_id = logged_user_id).first()
    logged_staff_id = staff.id

    # Getting assigned trek objects
    assigned_treks = Trek.query.filter_by(assigned_staff_id = logged_staff_id).all()

    # For participant counts
    for trek in assigned_treks:
        # Creating temporary arrtibute for each trek object
        trek.participant_count = Booking.query.filter_by(trek_id = trek.id).count()

    return render_template('staffMyTreks.html',
        assigned_treks = assigned_treks,
        )

## >> Staff Manage Trek Page << ##
@app.route('/staffManageTrek/<int:trek_id>', methods = ['GET', 'POST'])
def staff_manage_trek(trek_id):
    # Authentication & Role Check
    auth = req_role('staff')
    if auth == False:
        return redirect(url_for('logout'))

    # Getting logged staff_id
    logged_user_id = session['user_id']
    staff = Staff.query.filter_by(user_id = logged_user_id).first()
    logged_staff_id = staff.id

    # Getting assigned trek objects
    assigned_trek = Trek.query.filter_by(assigned_staff_id = logged_staff_id, id = trek_id).first()
    
    ## Checking validity of assigned trek started
    if assigned_trek:
    ## Checking validity of assigned trek completed

        if request.method == 'GET':
            # Getting trek data
            trek = Trek.query.filter_by(id = trek_id).first()

            if trek:
                # Getting participant Data
                bookings = Booking.query.join(Trekker).filter(Booking.trek_id == trek_id).all()
                participants_count = len(bookings)

                return render_template('staffManageTrek.html',
                    trek = trek,
                    bookings = bookings,
                    participants_count = participants_count
                    )
            else:
                return "Invalid Trek ID"
            
        if request.method == 'POST':
        
            if request.form['status'] == 'completed' or request.form['status'] == 'started':
                from datetime import date 
                ## For handling form date string data into iso date object (YYYY-MM-DD)
                
                # Getting trek data
                trek = Trek.query.filter_by(id = trek_id).first()
                trek.status = request.form['status']
                trek.total_slots = request.form['total_slots']

                # Getting booking data
                bookings = Booking.query.filter_by(trek_id = trek_id).all()
                
                for booking in bookings:
                    booking.status = trek.status
                    if request.form['status'] == 'completed':
                        booking.completion_date = date.today() ## Current date as YYYY-MM-DD format

                db.session.commit()
        
            else:
                # Getting trek data
                trek = Trek.query.filter_by(id = trek_id).first()
                trek.status = request.form['status']
                trek.total_slots = request.form['total_slots']

                db.session.commit()

        return redirect(url_for('staff_my_treks'))

    else:
        ## Not ssigned trek
        return "Invalid TrekID"

## >> View / Manage Bookings << ##
@app.route('/staffViewBookings')
def staff_view_bookings():
    # Authentication & Role Check
    auth = req_role('staff')
    if auth == False:
        return redirect(url_for('logout'))
    
    # Getting logged staff_id
    logged_user_id = session['user_id']
    staff = Staff.query.filter_by(user_id = logged_user_id).first()
    logged_staff_id = staff.id

    # List of all bookings
    bookings = Booking.query.join(Trek).filter(Trek.assigned_staff_id == logged_staff_id).order_by(Booking.booking_date.desc()).all()

    return render_template('staffViewBookings.html', bookings = bookings)

## >> View / Manage Bookings << ##
@app.route('/staffViewBookingDetails/<int:booking_id>', methods = ['GET', 'POST'])
def staff_view_booking_details(booking_id):
    # Authentication & Role Check
    auth = req_role('staff')
    if auth == False:
        return redirect(url_for('logout'))
    
    # Getting logged staff_id
    logged_user_id = session['user_id']
    staff = Staff.query.filter_by(user_id = logged_user_id).first()
    logged_staff_id = staff.id

    if request.method == 'GET':

        # Get booking data
        booking = Booking.query.join(Trek).filter(Booking.id == booking_id, Trek.assigned_staff_id == logged_staff_id).first()

        if booking:
            return render_template('staffViewBookingDetails.html', booking = booking)
        else:
            return "Invalid BookingID"

    if request.method == 'POST':
        # Get booking data
        booking = Booking.query.join(Trek).filter(Booking.id == booking_id, Trek.assigned_staff_id == logged_staff_id).first()

        if booking:
            # Delete booking data
            db.session.delete(booking)
            db.session.commit()

            return redirect(url_for('staff_view_bookings'))
        else:
            return "Invalid BookingID"

## >> Staff Profile Page << ##
@app.route('/staffProfile', methods = ['GET', 'POST'])
def staff_profile():
    # Authentication & Role Check
    auth = req_role('staff')
    if auth == False:
        return redirect(url_for('logout'))
    
    # Getting logged staff_id
    logged_staff_id = session['user_id']
    staff = Staff.query.filter_by(user_id = logged_staff_id).first()

    if request.method == 'GET':
        return render_template('staffProfile.html', staff = staff)
    
    if request.method == 'POST':
        staff.full_name = request.form['full_name']
        staff.gender = request.form['gender']
        staff.contact_no = request.form['contact_no']
        staff.user.password = request.form['password']

        db.session.commit()

        # Update full_name in session
        session['full_name'] = staff.full_name

        return redirect(url_for('staff_dashboard'))

### Staff Dashboard End ###



### Trekker Dashboard Start ###

## >> Dashboard Page << ##
@app.route('/trekkerDashboard')
def trekker_dashboard():
    # Authentication & Role Check
    auth = req_role('trekker')
    if auth == False:
        return redirect(url_for('logout'))


    # Getting open treks
    treks = Trek.query.filter_by(status ='open').all()

    # For participant counts of each trek
    for trek in treks:
        # Creating temporary arrtibute for each trek object
        trek.participant_count = Booking.query.filter_by(trek_id = trek.id).count()

    # Getting logged trekker_id
    logged_trekker_id = session['user_id']
    trekker = Trekker.query.filter_by(user_id = logged_trekker_id).first()
    logged_trekker_id = trekker.id

    # Getting my booking data
    bookings = Booking.query.filter_by(trekker_id = logged_trekker_id).all()

    return render_template('trekkerDashboard.html', treks = treks, bookings = bookings)

## >> Browse Treks << ##
@app.route('/trekkerBrowseTreks', methods = ['GET', 'POST'])
def trekker_browse_treks():
    # Authentication & Role Check
    auth = req_role('trekker')
    if auth == False:
        return redirect(url_for('logout'))
    
    # Collecting all available locations
    trks = Trek.query.all()
    location_list = {trek.location for trek in trks}
    
    if request.method == 'POST':
        q = request.form['q']

        if request.form['searchBtn'] == 'search':
            ## Search for Treks without difficulty and without location
            treks = Trek.query.filter( (Trek.id == q) | (Trek.trek_name.ilike(f"%{q}%")) ).all()
            difficulty = 'all'
            location = 'all'

            # For participant counts
            for trek in treks:
                # Creating temporary arrtibute for each trek object
                trek.participant_count = Booking.query.filter_by(trek_id = trek.id).count()

            return render_template(
                'trekkerBrowseTreks.html',
                treks = treks,
                q = q,
                difficulty = difficulty,
                location = location,
                location_list = location_list
                )
        
        if request.form['searchBtn'] == 'filter':

            if request.form.get('difficulty') in ['easy', 'moderate', 'hard']:
                difficulty = request.form.get('difficulty')
                if request.form.get('location') == 'all':
                    ## Search for Treks with difficulty and without location
                    treks = Trek.query.filter( (Trek.difficulty == difficulty) & ((Trek.id == q) | (Trek.trek_name.ilike(f"%{q}%"))) ).all()
                    location = 'all'
                else:
                    location = request.form.get('location')
                    ## Search for Treks with difficulty and location
                    treks = Trek.query.filter( (Trek.difficulty == difficulty) & (Trek.location == location) & ((Trek.id == q) | (Trek.trek_name.ilike(f"%{q}%"))) ).all()  

            elif request.form.get('difficulty') == 'all':
                if request.form.get('location') == 'all':
                    ## Search for Treks without difficulty and without location
                    treks = Trek.query.filter( ((Trek.id == q) | (Trek.trek_name.ilike(f"%{q}%"))) ).all()
                    difficulty = 'all'
                    location = 'all'
                else:
                    location = request.form.get('location')
                    ## Search for Treks with location and without difficulty
                    treks = Trek.query.filter( (Trek.location == location) & ((Trek.id == q) | (Trek.trek_name.ilike(f"%{q}%"))) ).all() 
                    difficulty = 'all'


            # For participant counts
            for trek in treks:
                # Creating temporary arrtibute for each trek object
                trek.participant_count = Booking.query.filter_by(trek_id = trek.id).count()

            return render_template('trekkerBrowseTreks.html',
                treks = treks,
                q = q,
                difficulty = difficulty,
                location = location,
                location_list = location_list
                )
    
    if request.method == 'GET':
        return render_template('trekkerBrowseTreks.html', location_list = location_list)

## >> Trekker Bookings Page << ##
@app.route('/trekkerBookings')
def trekker_bookings():
    # Authentication & Role Check
    auth = req_role('trekker')
    if auth == False:
        return redirect(url_for('logout'))


    # Getting logged trekker_id
    logged_trekker_id = session['user_id']
    trekker = Trekker.query.filter_by(user_id = logged_trekker_id).first()
    logged_trekker_id = trekker.id
    
    # Getting my booking data
    bookings = Booking.query.filter_by(trekker_id = logged_trekker_id).all()

    return render_template('trekkerBookings.html', bookings = bookings)

@app.route('/trekkerBookNow/<int:trek_id>', methods =['GET', 'POST'])
def trekker_book_now(trek_id):
    # Authentication & Role Check
    auth = req_role('trekker')
    if auth == False:
        return redirect(url_for('logout'))


    # Getting logged trekker_id
    logged_trekker_id = session['user_id']
    trekker = Trekker.query.filter_by(user_id = logged_trekker_id).first()
    logged_trekker_id = trekker.id

    # Getting Trek Data
    trek = Trek.query.filter_by(id = trek_id).first()
    if trek:
        # Creating temporary arrtibute for participant count
        trek.participant_count = Booking.query.filter_by(trek_id = trek.id).count()

        if request.method == 'GET':
            # Checking Booking status
            booking = Booking.query.filter_by(trek_id = trek_id, trekker_id = logged_trekker_id).first()

            return render_template('trekkerBookNow.html', trek = trek, booking = booking)
        
        if request.method == 'POST':
            from datetime import date 
            ## For handling form date string data into iso date object (YYYY-MM-DD)
            
            booking = Booking(
                trek_id = trek_id,
                trekker_id = logged_trekker_id,
                booking_date = date.today(), ## Current date as YYYY-MM-DD format
                status = 'booked'
            )
            db.session.add(booking)
            db.session.commit()

            return redirect(url_for('trekker_bookings'))
    else:
        return "Invalid Trek ID"
    
## >> Trekker History Page << ##
@app.route('/trekkerHistory')
def trekker_history():
    # Authentication & Role Check
    auth = req_role('trekker')
    if auth == False:
        return redirect(url_for('logout'))


    # Getting logged trekker_id
    logged_trekker_id = session['user_id']
    trekker = Trekker.query.filter_by(user_id = logged_trekker_id).first()
    logged_trekker_id = trekker.id

    # Getting completed booking data
    completed_bookings = Booking.query.filter_by(trekker_id = logged_trekker_id, status ="completed")

    return render_template('trekkerHistory.html', completed_bookings = completed_bookings)

## >> Trekker Profile Page << ##
@app.route('/trekkerProfile', methods = ['GET', 'POST'])
def trekker_profile():
    # Authentication & Role Check
    auth = req_role('trekker')
    if auth == False:
        return redirect(url_for('logout'))
    
    # Getting logged trekker_id
    logged_trekker_id = session['user_id']
    trekker = Trekker.query.filter_by(user_id = logged_trekker_id).first()

    if request.method == 'GET':
        return render_template('trekkerProfile.html', trekker = trekker)
    
    if request.method == 'POST':
        trekker.full_name = request.form['full_name']
        trekker.gender = request.form['gender']
        trekker.contact_no = request.form['contact_no']
        trekker.user.password = request.form['password']

        db.session.commit()

        # Update full_name in session
        session['full_name'] = trekker.full_name

        return redirect(url_for('trekker_dashboard'))

### Trekker Dashboard End ###