from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length


class EventForm(FlaskForm):
    name = StringField(
        "Navn på arrangement", validators=[DataRequired(), Length(min=3, max=100)]
    )
    description = TextAreaField(
        "Beskrivelse", validators=[DataRequired(), Length(min=10)]
    )
    date = DateField("Dato", validators=[DataRequired()], format="%Y-%m-%d")
    time = TimeField("Tidspunkt", validators=[DataRequired()], format="%H:%M")
    location = StringField("Sted", validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField("Lagre")
