from os import PRIO_USER
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from os import path

import sqlite3



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email('Correo no es válido')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesion')

    def validate_email(self, email):
        conn = sqlite3.connect('app.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users where email = (?)", [email.data])
        valemail = curs.fetchone()
        if valemail is None:
            raise ValidationError(
                'No se encontro ningun correo asociado al sitio, registrate primero.')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    names = StringField('Nombres', validators=[DataRequired()])
    password1 = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Confirmar contraseña',
                              validators=[DataRequired()])

    def validate_email(self, email):
        conn = sqlite3.connect('app.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users where email = (?)", [email.data])
        valemail = curs.fetchone()
        if valemail is None:
            raise ValidationError(
                'No se encontro ningun correo asociado al sitio, registrate primero.')

    def validate_password(self):
        if self.password1.data != self.password2.data:
            raise ValidationError('Las contraseñas no son iguales')
