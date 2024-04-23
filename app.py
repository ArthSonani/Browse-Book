from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from helpers import login_required


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///events.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


headlines = {   'business' : "Discover Business Meetups, Professional Events & Conferences In ",
                'music' : "Upcoming Music Events, Festivals And Concerts In ",
                'festival' : "Cultural, Arts & Educational Festivals In ",
                'workshop' : "Art, Business And Motivational Workshops In ",
                'performance' : "Musicals, Plays And Theater Shows In ",
                'theatre' : "Theatre, Performances And Plays In ",
                'sports' : "Tournaments, Tickets And Marathons In ",
                'other' : "Connect with the Best Venues and Discover Exciting Events Near You"
            }

# ==================================================================================================== #
# ===========================================  INDEX PAGE  =========================================== #
# ==================================================================================================== #


@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        search_name = request.form.get('search').strip().lower()
        events_list = db.execute("SELECT * FROM tickets t JOIN events e ON t.event_id = e.event_id WHERE (e.category = ? OR e.name = ?) OR e.event_id IN (SELECT e1.event_id FROM events e1 JOIN locations l ON e1.location_id = l.location_id WHERE l.location = ? OR l.city = ? OR l.state = ?);",
                                 search_name, 
                                 search_name, 
                                 search_name, 
                                 search_name, 
                                 search_name
                                )

        return render_template('explore_events.html', category_bg = "other-bg.jpeg", headline = headlines['other'], result = search_name, events_list = events_list)

    else:

        if 'user_id' in session:
            username = db.execute("SELECT name FROM users WHERE user_id = ?", session['user_id'])[0]['name'].upper()
        else:
            username = None
    
        events_list = db.execute("SELECT * FROM events JOIN tickets ON events.event_id = tickets.event_id LIMIT 8")  # sort based on rating
        return render_template("index.html", events_list = events_list, username = username)



# ==================================================================================================== #
# ===========================================  LOGIN PAGE  =========================================== #
# ==================================================================================================== #



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
          
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", error="Must provide username!")

        elif not password:
            return render_template("login.html", error="Must provide password!")
        
        else:
            
            user_identity = db.execute(
                "SELECT * FROM users WHERE username = ?", username
            )

            if len(user_identity) != 1 or not check_password_hash(user_identity[0]["hash"], password):
                return render_template("login.html", error="Invalid username or password!")
        
        session["user_id"] = user_identity[0]["user_id"]

        return redirect('/')
    
    else:
        return render_template('login.html')


# ==================================================================================================== #
# =========================================  REGISTER PAGE  ========================================== #
# ==================================================================================================== #


@app.route('/register', methods=['GET', 'POST'])
def register():

    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    vpassword = request.form.get("confirmation")

    if request.method == "POST":
        if name == "" or username == "" or password == "":
            return render_template("register.html", error="Name / Username / Password is missing!")
        
        elif password != vpassword:
            return render_template("register.html",error="Password verification failed!")
        
        users_data = db.execute("SELECT * FROM users")
        for user in users_data:
            if user["username"] == username:
                return render_template("register.html",error="Username already exists!")
        
        hashed_password = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (name, username, hash) VALUES (?, ?, ?)",
            name,
            username,
            hashed_password
        )

        user_identity = db.execute(
                "SELECT * FROM users WHERE username = ?", username
            )

        session["user_id"] = user_identity[0]["user_id"]

        return redirect("/")
    
    else:
        return render_template('register.html')
    


# ==================================================================================================== #
# ============================================  LOGOUT  ============================================== #
# ==================================================================================================== #



@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



# ==================================================================================================== #
# =======================================  CREATE EVENT PAGE  ======================================== #
# ==================================================================================================== #




@app.route("/create_events", methods=["GET", "POST"])
@login_required
def create_events():
    print(request.form)

    if request.method == "POST":

        name = request.form.get('name').strip()
        start_date = request.form.get('start_date') 
        end_date = request.form.get('end_date') 
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        event_mode = request.form.get('mode')

        if event_mode == 'offline':    
            location = request.form.get('location').strip().lower()
            address = request.form.get('address').strip()
            city = request.form.get('city').strip().lower()
            state = request.form.get('state').strip().lower()
            
        event_category = request.form.get('category')
        description = request.form.get('description').strip()
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        banner = request.files['banner']
        thumbnail = request.files['thumbnail']
       
       
        if name == '':
            return render_template("create_events.html",error="Must provide event name!")
        elif start_date == '' or start_time == '' or end_date == '' or end_time == '':
            return render_template("create_events.html",error="Must provide event time!")
        elif event_mode == '':
            return render_template("create_events.html",error="Must provide Mode of your event!")
        elif event_mode == 'offline' and (location == '' or address == '' or city == '' or state == ''):
            return render_template("create_events.html",error="Must provide locations!")
        elif event_category == '':
            return render_template("create_events.html",error="Must provide event category!")
        elif price == '':
            return render_template("create_events.html",error="Must provide event price!")
        elif quantity == '':
            return render_template("create_events.html",error="Must provide Ticket quantity!")
        elif (not banner) or (not thumbnail):
            return render_template("create_events.html",error="Please provide banner/thumbnail to attract more people!")
        else:
            print("hello1")
            banner_name = secure_filename(banner.filename)  
            ext = os.path.splitext(banner_name)
            banner_name = str(session['user_id']) + str('B') + str(name).capitalize().replace(" ", "") + str(ext[-1])
            banner.save(os.path.join('static/events_img', banner_name))

            thumbnail_name = secure_filename(thumbnail.filename)  
            ext = os.path.splitext(thumbnail_name)
            thumbnail_name = str(session['user_id']) + str('T') + str(name).capitalize().replace(" ", "") + str(ext[-1])
            thumbnail.save(os.path.join('static/events_img', thumbnail_name))
         
         
            if event_mode == 'offline':
                db.execute(
                    "INSERT INTO locations (location, address, city, state) VALUES (?, ?, ?, ?)",
                    location,
                    address,
                    city,
                    state
                )

                location_id  =  db.execute(
                                    "SELECT location_id FROM locations WHERE location = ? AND address = ? AND city = ? AND state = ?",
                                    location,
                                    address,
                                    city,
                                    state
                                )[0]['location_id']    
                
            else:
                location_id = None


            db.execute(
                "INSERT INTO events (name, description, start_date, start_time, end_date, end_time, event_mode, category, banner, thumbnail, user_id, location_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                name,
                description, 
                start_date, 
                start_time, 
                end_date, 
                end_time, 
                event_mode, 
                event_category, 
                banner_name, 
                thumbnail_name,
                session['user_id'],
                location_id
            )
            
            event_id = db.execute(
                "SELECT event_id FROM events WHERE name = ? AND user_id = ? AND start_date = ?",
                name,
                session['user_id'],
                start_date
            )[0]['event_id']

            db.execute(
                "INSERT INTO tickets (price, sold, unsold, event_id) VALUES (?, ?, ?, ?)",
                price,
                0,
                quantity,
                event_id
            )

            return redirect('/')
    
    else:

        return render_template('create_events.html')
    



# ==================================================================================================== #
# =======================================  EXPLORE EVENT PAGE  ======================================= #
# ==================================================================================================== #




@app.route("/explore_events", methods=["GET", "POST"])
@login_required
def explore_events():
     
    if request.method == 'POST':
        
        category = request.form.get('category')
        location = request.form.get('location').strip().lower()

        category_bg = category + "-bg.jpeg"

        if location != "":
            events_list = db.execute("SELECT * FROM events JOIN tickets ON events.event_id = tickets.event_id WHERE category = ? AND events.event_id IN (SELECT event_id FROM events JOIN locations ON events.location_id = locations.location_id WHERE location = ? OR city = ? OR state = ?)",
                                 category, 
                                 location, 
                                 location, 
                                 location 
                                )
        else:
            events_list = db.execute("SELECT * FROM events JOIN tickets ON events.event_id = tickets.event_id WHERE category = ?", category)
            location = None

        return render_template('explore_events.html', event_list = events_list, category = category.upper(), city = location, headline = headlines[category], category_bg = category_bg)

    else:

        category = request.args.get('category')

        category_bg = category + "-bg.jpeg"

        events_list = db.execute("SELECT * FROM events JOIN tickets ON events.event_id = tickets.event_id WHERE category = ?", category)


        return render_template('explore_events.html', events_list=events_list, category=category.upper(), city=None, headline=headlines[category], category_bg=category_bg)
    



# ==================================================================================================== #
# ========================================  VISIT EVENT PAGE  ======================================== #
# ==================================================================================================== #



@app.route("/visit_event", methods=["GET", "POST"])
@login_required
def visit_event():
    if request.method == 'POST':
        return render_template('visit_event.html')
    
    else:

        event_id = request.args.get('id')

        event_details = db.execute("SELECT * FROM events WHERE event_id = ?",event_id)[0]
        rating_details = db.execute("SELECT * FROM ratings WHERE event_id = ?", event_id)
        ticket_details = db.execute("SELECT * FROM tickets WHERE event_id = ?", event_id)[0]
        
        if event_details['event_mode'] == 'offline':
            location_id = event_details['location_id']
            location_details = db.execute("SELECT * FROM locations WHERE location_id = ?",location_id)[0]
        else:
            location_details = None

        return render_template('visit_event.html', event=event_details, ratings=rating_details, tickets=ticket_details, locations=location_details)
