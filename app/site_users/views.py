# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import render_template, abort, redirect, current_app, request, url_for, flash
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.babel import gettext as _

from . import site_users_blueprint

from .forms import SearchUserForm, AddUserForm, EditUserForm, AclSettingForm, SearchOperationRecordForm
from .. import db
from ..models import User, UserAcl, OperationRecord
from ..util import add_log, acl_required, get_rand_string

try:
    import simplejson as json
except:
    import json

@site_users_blueprint.route('/list', methods=['GET', 'POST'])
def user_list():
    form = SearchUserForm()
    context = {
        'admin_username': current_app.config['ADMIN_USERNAME'],
        'users'         : [],
        'form'          : form,
    }

    page_num = request.args.get('pageNum', 1, type=int)
    keyword = {}

    # Submit
    if form.validate_on_submit():
        if form.name.data:
            keyword['name'] = form.name.data
        if form.username.data:
            keyword['username'] = form.username.data
        return redirect(url_for('site_users.user_list', pageNum=1, **keyword))

    name     = request.args.get('name', type=unicode)
    username = request.args.get('username', type=str)

    q = User.query
    if name:
        form.name.data = name
        q = q.filter(User.name.like(u"%{}%".format(name)))

    if username:
        form.username.data = username
        q = q.filter(User.username.like(u"%{}%".format(username)))

    p = q.order_by(
            # Uncomment only for MySQL
            # db.func.field(User.username, current_user.username).desc(),
            # db.func.field(User.status, 'normal', 'disabled'),
            User.last_seen.desc(),
            User.username).paginate(
                page_num,
                per_page=current_app.config['RECORDS_PER_PAGE'],
                error_out=False)

    if name:
        keyword['name'] = name
    if username:
        keyword['username'] = username

    context['users']       = p.items
    context['pagination']  = p
    context['prevKeyword'] = keyword
    context['hasKeyword']  = any([v for k, v, in keyword.items()])
    return render_template('site_users/user_list.html', **context)

@site_users_blueprint.route('/add', methods=['GET', 'POST'])
@acl_required('addSiteUser')
def user_add():
    # Open Page
    form = AddUserForm()
    context = {
        'form': form
    }
    if not form.validate_on_submit():
        return render_template('site_users/user_add.html', **context)

    # Submit
    new_user = User.new(
            username=form.username.data,
            name=form.name.data,
            password=form.password.data,
            last_seen=None)
    db.session.add(new_user)
    db.session.commit()

    flash(_('User {} ({}) has been added').format(
            new_user.name,
            new_user.username), 'success')

    add_log('[Site User][Add User] Added user：{}；username：{}'.format(new_user.name, new_user.username))
    return redirect(url_for('site_users.user_add'))

@site_users_blueprint.route('/<user_id>/edit', methods=['GET', 'POST'])
@acl_required('editSiteUser')
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_admin() or current_user.id == user.id:
        pass
    elif user.is_admin() or user.can('editSiteUser'):
        abort(403)

    origin_user_username = user.username
    origin_user_name     = user.name

    # Open Page
    form = EditUserForm()
    form.prev = user
    context = {
        'form': form
    }

    if not form.validate_on_submit():
        form.username.data = user.username
        form.name.data  = user.name
        return render_template('site_users/user_edit.html', **context)

    # Submit
    user.username = form.username.data
    user.name  = form.name.data
    if form.password.data:
        user.password = form.password.data
    db.session.add(user)
    db.session.commit()

    flash(_('User {} ({}) has been edited').format(
            user.name, user.username), 'success')

    add_log('[Site User][Edit User] Edited user: {}; username: {}'.format(origin_user_name, origin_user_username))
    return redirect(url_for('site_users.user_edit', user_id=user_id))

@site_users_blueprint.route('/<user_id>/set_status', methods=['GET'])
@acl_required('setSiteUserStatus')
def user_set_status(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_admin() and current_user.id != user.id:
        pass
    elif user.is_admin() or user.can('setSiteUserStatus'):
        abort(403)

    next_status = request.args.get('nextStauts', type=str)
    if next_status not in ['normal', 'disabled']:
        flash('Does not support such status: {}'.format(next_status), 'danger')
        abort(400)

    user.status = next_status
    db.session.add(user)
    db.session.commit()

    flash(_('User {} ({}) status has been setted: {}').format(
            user.name, user.username, next_status), 'success')

    add_log('[Site User][User List] Setted user status: {}; username: {}; status: {}'.format(user.name, user.username, next_status))
    return redirect(url_for('site_users.user_list'))

@site_users_blueprint.route('/<user_id>/acl_setting', methods=['GET', 'POST'])
@acl_required('setSiteUserAcl')
def user_acl_setting(user_id):
    user = User.query.get_or_404(user_id)
    user = User.query.get_or_404(user_id)
    if current_user.is_admin():
        pass
    elif user.is_admin() or user.can('setSiteUserAcl') or current_user.id == user.id:
        abort(403)

    user_acl_actions = UserAcl.query.filter_by(user_id=user.id).all()
    user_acl_action_list = [r.action for r in user_acl_actions]
    if user.is_admin():
        user_acl_action_list.extend(current_app.config['ADMIN_DEFAULT_ACL_ACTIONS'])

    form = AclSettingForm()
    context = {
        'admin_username'      : current_app.config['ADMIN_USERNAME'],
        'user'                : user,
        'user_acl_action_list': user_acl_action_list,
        'acl_actions'         : current_app.config['ACL_ACTIONS'],
        'limited_acl_actions' : current_app.config['LIMITED_ACL_ACTIONS'],
        'form'                : form,
    }

    # Open Page
    if not form.validate_on_submit():
        form.acl_actions.data = json.dumps(user_acl_action_list)
        return render_template('site_users/acl_setting.html', **context)

    # Submit
    UserAcl.query.filter_by(user_id=user.id).delete()
    user_acl_action_list = json.loads(form.acl_actions.data)

    db.session.add_all([
            UserAcl.new(user_id=user.id, action=action)
            for action in user_acl_action_list])
    db.session.commit()

    flash(_('User {} ({}) ACL has been setted').format(
            user.name, user.username), 'success')

    add_log('[Site User][ACL Setting] Setted user ACL: {}; username: {}'.format(user.name, user.username))
    return redirect(url_for('site_users.user_acl_setting', user_id=user_id))

@site_users_blueprint.route('/operation_records', methods=['GET', 'POST'])
@acl_required('showManageSiteUserOperationRecords')
def operation_records():
    form = SearchOperationRecordForm()
    context = {
        'admin_username'   : current_app.config['ADMIN_USERNAME'],
        'operation_records': [],
        'form'             : form,
    }

    page_num = request.args.get('pageNum', 1, type=int)
    keyword = {}

    # Submit
    if form.validate_on_submit():
        if form.name.data:
            keyword['name'] = form.name.data
        if form.username.data:
            keyword['username'] = form.username.data
        if form.operation_note.data:
            keyword['operationNote'] = form.operation_note.data
        return redirect(url_for('site_users.operation_records', pageNum=1, **keyword))

    name           = request.args.get('name', type=str)
    username       = request.args.get('username', type=str)
    operation_note = request.args.get('operationNote', type=str)

    q = OperationRecord.query.add_entity(User).join(User, OperationRecord.user_id == User.id)
    if name:
        form.name.data = name
        q = q.filter(User.name.like(u"%{}%".format(name)))

    if username:
        form.username.data = username
        q = q.filter(User.username.like(u"%{}%".format(username)))

    if operation_note:
        form.operation_note.data = operation_note
        q = q.filter(OperationRecord.operation_note.like(u"%{}%".format(operation_note)))

    p = q.order_by(OperationRecord.created_timestamp.desc()).paginate(
        page_num,
        per_page=current_app.config['RECORDS_PER_PAGE'],
        error_out=False)

    if name:
        keyword['name'] = name
    if username:
        keyword['username'] = username
    if operation_note:
        keyword['operationNote'] = operation_note

    context['operation_records'] = p.items
    context['pagination']        = p
    context['prevKeyword']       = keyword
    context['hasKeyword']        = any([v for k, v, in keyword.items()])
    return render_template('site_users/operation_records.html', **context)

