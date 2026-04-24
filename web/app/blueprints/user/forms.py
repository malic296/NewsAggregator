from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

class CredentialsForm(FlaskForm):
    old_password = PasswordField("Momentální heslo", validators=[DataRequired(), Length(min=5, max=30, message="Heslo musí mít 5 až 30 znaků.")])
    new_username = StringField("Nové uživatelské jméno", validators=[Length(min=4, max=20, message="Uživatelské jméno musí mít 4 až 20 znaků.")])
    new_password = PasswordField("Nové heslo", validators=[Length(min=5, max=50, message="Heslo musí mít 5 až 50 znaků.")])
    new_password_integrity = PasswordField(
        "Znovu nové heslo",
        validators=[
            EqualTo('new_password', message='Hesla se musí shodovat'),
            Length(min=5, max=50, message="Heslo musí mít 5 až 50 znaků.")
        ]
    )