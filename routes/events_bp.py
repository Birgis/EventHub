from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import DataBase
from models.event import Event
from forms.event_forms import EventForm
from datetime import datetime

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def upcoming_events():
    events = []
    search_term = request.args.get("search", "")

    with DataBase() as db:
        if search_term:
            events_data = db.search_events(search_term)
        else:
            events_data = db.get_all_events()

        for event_data in events_data:
            event = Event.from_dict(event_data)

            registrations = db.get_registrations_by_event_id(event.id)
            event.registrations = registrations

            if current_user.is_authenticated:
                registration = db.get_registration(current_user.id, event.id)
                event.is_registered = registration is not None
            else:
                event.is_registered = False

            events.append(event)

    return render_template("events/index.html", events=Event.upcoming_events(events))


@events_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_event():
    form = EventForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        date_obj = form.date.data
        time_obj = form.time.data
        location = form.location.data

        combined_date = datetime.combine(date_obj, time_obj)

        with DataBase() as db:
            db.create_event(current_user.id, name, description, combined_date, location)
            flash("Arrangement opprettet!")
            return redirect(url_for("users.profile"))

    return render_template("events/create.html", form=form)


@events_bp.route("/<int:event_id>")
def event_details(event_id):
    with DataBase() as db:
        event_data = db.get_event_by_id(event_id)

        if not event_data:
            flash("Arrangementet ble ikke funnet.")
            return redirect(url_for("events.upcoming_events"))

        event = Event.from_dict(event_data)

        registrations = db.get_registrations_by_event_id(event_id)
        event.registrations = registrations

        is_registered = False
        if current_user.is_authenticated:
            registration = db.get_registration(current_user.id, event_id)
            is_registered = registration is not None

    return render_template(
        "events/details.html", event=event, is_registered=is_registered
    )


@events_bp.route("/<int:event_id>/register")
@login_required
def register_event(event_id):
    with DataBase() as db:
        event_data = db.get_event_by_id(event_id)

        if not event_data:
            flash("Arrangementet ble ikke funnet.")
            return redirect(url_for("events.upcoming_events"))

        existing_registration = db.get_registration(current_user.id, event_id)
        if existing_registration:
            flash("Du er allerede påmeldt dette arrangementet.")
            return redirect(url_for("events.event_details", event_id=event_id))

        if event_data["user_id"] == current_user.id:
            flash("Du kan ikke melde deg på ditt eget arrangement.")
            return redirect(url_for("events.event_details", event_id=event_id))

        db.create_registration(current_user.id, event_id)
        flash("Du er nå påmeldt dette arrangementet.")

    return redirect(url_for("events.event_details", event_id=event_id))


@events_bp.route("/<int:event_id>/unregister")
@login_required
def unregister_event(event_id):
    with DataBase() as db:
        event_data = db.get_event_by_id(event_id)

        if not event_data:
            flash("Arrangementet ble ikke funnet.")
            return redirect(url_for("events.upcoming_events"))

        existing_registration = db.get_registration(current_user.id, event_id)
        if not existing_registration:
            flash("Du er ikke påmeldt dette arrangementet.")
            return redirect(url_for("events.event_details", event_id=event_id))

        db.delete_registration(current_user.id, event_id)
        flash("Du er nå avmeldt dette arrangementet.")

    return redirect(url_for("events.event_details", event_id=event_id))


@events_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    with DataBase() as db:
        event_data = db.get_event_by_id(event_id)

        if not event_data:
            flash("Arrangementet ble ikke funnet.")
            return redirect(url_for("events.upcoming_events"))

        if event_data["user_id"] != current_user.id:
            flash("Du har ikke tillatelse til å redigere dette arrangementet.")
            return redirect(url_for("events.event_details", event_id=event_id))

        form = EventForm()

        if request.method == "GET":
            event = Event.from_dict(event_data)
            form.name.data = event.name
            form.description.data = event.description
            form.date.data = event.date.date()
            form.time.data = event.date.time()
            form.location.data = event.location

        if form.validate_on_submit():
            name = form.name.data
            description = form.description.data
            date_obj = form.date.data
            time_obj = form.time.data
            location = form.location.data

            combined_date = datetime.combine(date_obj, time_obj)

            if db.update_event(event_id, name, description, combined_date, location):
                flash("Arrangement oppdatert!")
                return redirect(url_for("events.event_details", event_id=event_id))
            else:
                flash("Det oppsto et problem med å oppdatere arrangementet.")

    return render_template("events/edit.html", form=form, event_id=event_id)


@events_bp.route("/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    with DataBase() as db:
        event_data = db.get_event_by_id(event_id)

        if not event_data:
            flash("Arrangementet ble ikke funnet.")
            return redirect(url_for("events.upcoming_events"))

        if event_data["user_id"] != current_user.id:
            flash("Du har ikke tillatelse til å slette dette arrangementet.")
            return redirect(url_for("events.event_details", event_id=event_id))

        if db.delete_event(event_id):
            flash("Arrangement slettet!")
        else:
            flash("Det oppsto et problem med å slette arrangementet.")

    return redirect(url_for("users.profile"))
