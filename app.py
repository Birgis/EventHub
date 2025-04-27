from flask import Flask, redirect, url_for
import secrets
from database import DataBase
from routes.user_manager import users_bp, login_manager
from routes.events_bp import events_bp

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

login_manager.init_app(app)

app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(events_bp, url_prefix="/events")

DataBase()


@app.route("/")
def index():
    return redirect(url_for("events.upcoming_events"))


if __name__ == "__main__":
    app.run(debug=True)
