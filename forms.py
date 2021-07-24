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
    email = StringField('Email', validators=[DataRequired(), Email('El correo no es válido')])
    names = StringField('Nombres', validators=[DataRequired()])
    password1 = PasswordField('Contraseña', validators=[DataRequired(), EqualTo('password2', 'Las constraseñas deben ser iguales')])
    password2 = PasswordField('Confirmar contraseña',
                              validators=[DataRequired()])
    submit = SubmitField('Registrarse')

    def validate_email(self, email):
        conn = sqlite3.connect('app.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users where email = (?)", [email.data])
        valemail = curs.fetchone()
        if valemail is not None:
            raise ValidationError(
                'Ya existe un usuario con esa direccion de correo. Intente usar otro.')