from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, PasswordField, BooleanField, IntegerField, DateField, SelectMultipleField, widgets
from wtforms.validators import Required, ValidationError, DataRequired, Email, EqualTo
from flask_login import current_user
from app.models import *
import datetime


class PitchChoiceIterable(object):
    def __iter__(self):
        pitches = Pitch.query.all()
        choices = [(pitch.id, pitch.pitchName) for pitch in pitches]
        for choice in choices:
            yield choice


class BookbookingForm(FlaskForm):
    title = StringField('EPL team', validators=[DataRequired()])
    pitches = SelectField('Choose Pitch', coerce=int,
                        choices=PitchChoiceIterable())
    date = DateField('Choose date', format="%m/%d/%Y",
                     validators=[DataRequired()])
    startTime = SelectField('Choose starting time(in 24hr expression)',
                            coerce=int, choices=[(i, i) for i in range(9, 19)])
    duration = SelectField('Choose duration of the game(in hours)',
                           coerce=int, choices=[(i, i) for i in range(1, 6)])
   
    submit = SubmitField('Book')

    def validate_title(self, title):
        booking = Booking.query.filter_by(title=self.title.data).first()
        if booking is not None:  # username exist
            raise ValidationError('Please use another booking title.')

    def validate_date(self, date):
        if self.date.data < datetime.datetime.now().date():
            raise ValidationError('You can only book for day after today.')


class PitchavailableForm(FlaskForm):
    date = DateField('Choose date', format="%m/%d/%Y",
                     validators=[DataRequired()])
    startTime = SelectField('Choose starting time(in 24hr expression)',
                            coerce=int, choices=[(i, i) for i in range(9, 19)])
    duration = SelectField('Choose duration of the game(in hours)',
                           coerce=int, choices=[(i, i) for i in range(1, 6)])
    submit = SubmitField('Check')


class PitchoccupationForm(FlaskForm):
    date = DateField('Choose date', format="%m/%d/%Y",
                     validators=[DataRequired()])
    submit = SubmitField('Check')


class BookingChoiceIterable(object):
    def __iter__(self):
        bookings = Booking.query.filter_by(bookerId=current_user.id).all()
        choices = [
            (booking.id, f'{booking.title} in {Pitch.query.filter_by(id=booking.pitchId).first().pitchName} start at {booking.date.date()} from {booking.startTime}') for booking in bookings]
        for choice in choices:
            yield choice



class CancelbookingForm(FlaskForm):
    ids = SelectField('Choose booking to cancel:', coerce=int,
                      choices=BookingChoiceIterable())
    submit = SubmitField('Cancel')



