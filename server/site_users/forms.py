# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo
from wtforms import ValidationError
from flask.ext.babel import lazy_gettext as _

from ..models import User

class SearchUserForm(Form):
    username = StringField()
    name     = StringField()
    submit   = SubmitField(_('Search'))

class AddUserForm(Form):
    username = StringField(validators=[
            Required(message=_('Please enter a username')),
            Length(1, 64)])

    name = StringField(validators=[
            Required(message=_('Please enter a name')),
            Length(1, 64)])

    password = PasswordField(validators=[
            Required(message=_('Please enter a password')),
            EqualTo('password2', message=_('The passwords you entered do not match'))])

    password2 = PasswordField(validators=[
            Required(message=_('Please confirm the password'))])

    submit = SubmitField(_('Add'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError(_('This username already existed'))

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(_('This name already existed'))

class EditUserForm(Form):
    username = StringField(validators=[
            Required(message=_('Please enter a username')),
            Length(1, 64)])

    name = StringField(validators=[
            Required(message=_('Please enter a name')),
            Length(1, 64)])

    password = PasswordField()

    submit = SubmitField(_('Edit'))

    def validate_username(self, field):
        if field.data != self.prev.username and \
                User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError(_('This username already existed'))

class AclSettingForm(Form):
    acl_actions = TextAreaField()
    submit = SubmitField(_('OK'))

class SearchOperationRecordForm(Form):
    name           = StringField()
    username        = StringField()
    operation_note = StringField()

    submit = SubmitField(_('Search'))
