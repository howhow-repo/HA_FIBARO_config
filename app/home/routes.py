# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.home.forms import HCForm
from requests.exceptions import ConnectTimeout, InvalidURL, ConnectionError
from app.lib.hc3 import FibaroHC3


@blueprint.route('/')
# @login_required
def index():
    hc_form = HCForm()
    return render_template('HC-config.html', segment='HC-config', form=hc_form)


@blueprint.route('/set_hc_config', methods=['POST'])
def set_hc_config():
    try:
        hc = FibaroHC3(ip=request.form['ip'], port=request.form['port'],
                       username=request.form['username'], password=request.form['password'])
        status_code = hc.check_connection(timeout=1).status_code

        if status_code == 200:
            return render_template('HC-config-ok.html', hc_info=hc.get_info().json(), form_data=request.form.to_dict())

        elif status_code == 401:
            return render_template('HC-config-failed.html', err_msg='wrong username/password')

    except ConnectTimeout:
        return render_template('HC-config-failed.html', err_msg='connection timeout')
    except InvalidURL:
        return render_template('HC-config-failed.html', err_msg='Wrong URL format')
    except Exception as e:
        return render_template('HC-config-failed.html', err_msg=e)


@blueprint.route('/set_hc_config/overwrite', methods=['POST'])
def overwrite_ha_config():
    with open('./app/home/file_templates/configuration.yaml', 'r') as f:
        config_temp = f.read()
    config_temp = config_temp.replace("{{HC_URL}}", f" http://{request.form['ip']}:{request.form['port']}/api/")
    config_temp = config_temp.replace("{{USERNAME}}", request.form['username'])
    config_temp = config_temp.replace("{{PASSWORD}}", request.form['password'])

    if os.path.isfile('/.homeassistant/configuration.yaml'):
        with open('/.homeassistant/configuration.yaml', 'w') as f:
            f.write(config_temp)
        return
    else:
        return render_template('HC-config-failed.html', err_msg='home assistant config file not exist')


@blueprint.route('/<template>')
# @login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template(template, segment=segment)

    except TemplateNotFound:
        return render_template('page-404.html'), 404

    except:
        return render_template('page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
