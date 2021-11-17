# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, StringField
from wtforms.validators import InputRequired, Email, DataRequired


class HCForm(FlaskForm):
    ip = StringField('IP', validators=[DataRequired()])
    port = StringField('PORT', validators=[DataRequired()], default="80")
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
