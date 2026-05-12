from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length
from wtforms.fields import PasswordField, StringField, IntegerField

class LoginForm(FlaskForm):
    credential = StringField('Přihlašovací jméno/Emailová adresa', validators=[DataRequired(), Length(max=50, message="Přihlašovací jméno/Emailová adresa může mít maximálně 50 znaků")])
    password = PasswordField('Heslo', validators=[DataRequired(), Length(min = 5, max=50, message="Heslo musí mít 5 až 50 znaků.")])

class RegistrationForm(FlaskForm):
    username = StringField('Přihlašovací jméno', validators=[DataRequired(), Length(min=4, max=20, message="Uživatelské jméno musí mít 4 až 20 znaků.")])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50, message="Email musí mít maximálně 50 znaků.")])
    password = PasswordField('Heslo', validators=[DataRequired(), Length(min=5, max=50, message="Heslo musí mít 5 až 50 znaků.")])
    invitation_code = StringField('Invitační Kód', validators=[DataRequired(), Length(min=6, max=6, message="Kód má přesně 6 číslic.")])

class VerifyForm(FlaskForm):
    code = StringField('Kód', validators=[DataRequired(), Length(min=6, max=6, message="Kód má přesně 6 číslic.")])