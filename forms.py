from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import validators
from wtforms.fields.core import DecimalField, FloatField, IntegerField, SelectField
from wtforms.fields import html5
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Regexp, URL, ValidationError

from os import path

import sqlite3


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Email('Correo no es válido')])
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
    email = StringField('Email', validators=[
                        DataRequired(), Email('El correo no es válido')])
    names = StringField('Nombres', validators=[DataRequired()])
    password1 = PasswordField('Contraseña', validators=[DataRequired(), EqualTo(
        'password2', 'Las constraseñas deben ser iguales')])
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


class FormCarrito(FlaskForm):
    id = HiddenField()
    cantidad = IntegerField('Cantidad', default=1,
                            validators=[NumberRange(min=1,
                                                    message="Debe ser un númer"
                                                            "o positivo"),
                                        DataRequired("Tienes que introducir el "
                                                 "dato")])
    submit = SubmitField('Aceptar')


class ProductForm(FlaskForm):
    id = HiddenField()
    product_name = StringField('Nombre del producto', validators=[DataRequired()])
    category = SelectField('Categoria', validators=[DataRequired()])
    sub_category = SelectField('Sub Categoria', validators=[DataRequired()],)
    price = html5.DecimalField('Precio', validators=[DataRequired(),NumberRange(min=1, message='Numero no valido')])
    stock = html5.IntegerField('Stock', validators=[DataRequired(),NumberRange(min=1, message='Numero no valido')])
    url_imagen = StringField('url de la imagen', validators=[DataRequired(), URL(message='Debe ser una url valida')])
    submit = SubmitField('Agregar')