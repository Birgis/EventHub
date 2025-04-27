from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("E-post", validators=[DataRequired(), Email()])
    password = PasswordField("Passord", validators=[DataRequired()])
    submit = SubmitField("Logg inn")


class RegistrationForm(FlaskForm):
    name = StringField("Navn", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("E-post", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Passord",
        validators=[
            DataRequired(),
            Length(min=6, message="Passordet må være minst 6 tegn"),
        ],
    )
    confirm_password = PasswordField(
        "Bekreft passord",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passordene må stemme overens"),
        ],
    )
    submit = SubmitField("Registrer")
