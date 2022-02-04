from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests, math


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///weather.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "thisisasecretkey"


db = SQLAlchemy(app)
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=77fc43de6ab4925999874856d38f1e87"
    r = requests.get(url).json()
    return r
    
@app.route("/")
def index_get():
    cities = City.query.all()
    
    weather_data = []

    for c in cities:
        
        r = get_weather_data(c.name)
        weather ={
            "city": c.name,

            "temperature": math.ceil(r["main"]["temp"]),
            "min_temperature": r["main"]["temp_min"],
            "max_temperature": r["main"]["temp_max"],
            "feels": r["main"]["feels_like"],

            "description": r["weather"][0]["description"],
            "icon": r["weather"][0]["icon"],

            "wind": r["wind"]["speed"],
            "humidity": r["main"]["humidity"],
            "visibility": r["visibility"]
        }
        weather_data.insert(0, weather)

    return render_template("weather.html", weather_data=weather_data)

@app.route("/", methods=["POST"])
def index_post():
    err=""
    new_city = request.form.get("city")
    new_city = new_city.upper()
    

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
       
        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if(new_city_data['cod'] == 200):    
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
                
            else:
                err = "City does not exist in the world!"
        else:
            err = "City is already present"
            
        if(err):
            flash(err, "error")
        else:
            flash("City added succesfully!", "success")

    return redirect(url_for("index_get"))

@app.route("/delete<name>")
def delete(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    
    return redirect(url_for("index_get"))

if(__name__ == "__main__"):
    app.run(debug=True)