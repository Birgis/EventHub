from flask import render_template, redirect, url_for, request, Blueprint, flash
from flask_login import (
    LoginManager,
    logout_user,
    login_required,
    login_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import DataBase
from models.user import User
from models.event import Event
from forms.user_forms import LoginForm, RegistrationForm

users_bp = Blueprint("users", __name__)
login_manager = LoginManager()
login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(user_id):
    with DataBase() as db:
        user_data = db.get_user_by_id(user_id)
    if user_data:
        return User(
            user_data["id"],
            user_data["name"],
            user_data["email"],
            user_data["password_hash"],
        )
    return None


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        with DataBase() as db:
            existing_user = db.get_user_by_email(email)

            if existing_user:
                flash("E-post er allerede registrert.")
                return redirect(url_for("users.register"))

            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            user_id = db.create_user(name, email, hashed_password)
            flash("Registrering vellykket! Du kan nå logge inn.")
            return redirect(url_for("users.login"))

    return render_template("users/register.html", form=form)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        with DataBase() as db:
            user_data = db.get_user_by_email(email)

            if not user_data or not check_password_hash(
                user_data["password_hash"], password
            ):
                flash("Ugyldig e-post eller passord.")
                return redirect(url_for("users.login"))

            user = User(
                user_data["id"],
                user_data["name"],
                user_data["email"],
                user_data["password_hash"],
            )
            login_user(user)
            flash("Logget inn!")

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("index"))

    return render_template("users/login.html", form=form)


@users_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du er nå logget ut.")
    return redirect(url_for("index"))


@users_bp.route("/profile")
@login_required
def profile():
    user_events = []
    user_registrations = []

    with DataBase() as db:
        events_data = db.get_events_by_user_id(current_user.id)

        for event_data in events_data:
            event = Event.from_dict(event_data)
            registrations = db.get_registrations_by_event_id(event.id)
            event.registrations = registrations
            user_events.append(event)

        registrations_data = db.get_registrations_by_user_id(current_user.id)
        for reg_data in registrations_data:
            event = Event(
                reg_data["id"],
                reg_data["event_user_id"],
                reg_data["name"],
                reg_data["description"],
                reg_data["date"],
                reg_data["location"],
                reg_data["creator_name"],
            )
            user_registrations.append(event)

    return render_template(
        "users/profile.html",
        user_events=user_events,
        user_registrations=user_registrations,
    )
