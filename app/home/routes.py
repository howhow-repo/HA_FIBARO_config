# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os, json
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from app.home.forms import HCForm, HATokenForm
from requests.exceptions import ConnectTimeout, InvalidURL, ConnectionError
from app.lib.hc3 import FibaroHC3
from app.lib.home_assistant import HomeAssistant


@blueprint.route('/')
# @login_required
def index():
    hc_form = HCForm()
    with open("./app/home/data/hc.json", "r") as f:
        hc_info = f.read()
    return render_template('HC-config.html', hc_info=hc_info, form=hc_form)


@blueprint.route('/setting_hc_config', methods=['POST'])
def setting_hc_config():
    try:
        hc = FibaroHC3(ip=request.form['ip'], port=request.form['port'],
                       username=request.form['username'], password=request.form['password'])
        status_code = hc.check_connection(timeout=2).status_code

        if status_code == 200:
            return render_template('HC-config-ok.html', hc_info=hc.get_info().json(), form_data=request.form.to_dict())

        elif status_code == 401:
            return render_template('HC-config-failed.html',
                                   err_title="HC connection fail", err_msg='wrong username/password')

    except ConnectTimeout:
        return render_template('HC-config-failed.html', err_title="HC connection fail", err_msg='connection timeout')
    except InvalidURL:
        return render_template('HC-config-failed.html', err_title="HC connection fail", err_msg='Wrong URL format')
    except Exception as e:
        return render_template('HC-config-failed.html', err_title="HC connection fail", err_msg=e)


@blueprint.route('/set_hc_config/overwrite', methods=['POST'])
def overwrite_ha_config():
    with open('./app/home/file_templates/configuration.yaml', 'r') as f:
        config_temp = f.read()
    config_temp = config_temp.replace("{{HC_URL}}", f"http://{request.form['ip']}:{request.form['port']}/api/")
    config_temp = config_temp.replace("{{USERNAME}}", request.form['username'])
    config_temp = config_temp.replace("{{PASSWORD}}", request.form['password'])

    if os.path.isfile('/home/pi/.homeassistant/configuration.yaml'):
        with open('/home/pi/.homeassistant/configuration.yaml', 'w') as f:
            f.write(config_temp)
        os.system("sudo systemctl restart homeassistant.service")

        hc = FibaroHC3(ip=request.form['ip'], port=request.form['port'],
                       username=request.form['username'], password=request.form['password'])
        hc_info = hc.info.json()
        hc_info = {'ip': request.form['ip'], 'port': request.form['port'],
                   'username': request.form['username'], 'SN': hc_info['serialNumber'], 'mac': hc_info['mac']}

        with open("./app/home/data/hc.json", "w") as f:
            f.write(json.dumps(hc_info))
        return render_template('simple_info_page.html', msg="ok, restarting home assistant service.")

    else:
        return render_template('HC-config-failed.html',
                               err_title="HC connection fail", err_msg='home assistant config file not exist')


@blueprint.route('/ha_token')
def ha_index():
    with open("./app/home/data/ha_token.json", "r") as f:
        d = json.loads(f.read())
    token = d['token']
    return render_template("ha_index.html", last_token=token, form=HATokenForm())


@blueprint.route('/setting_ha_token', methods=['POST'])
def ha_set_token():
    ha = HomeAssistant(ip="localhost", port="8123", token=request.form['token'])
    if not ha.is_connected():
        return render_template('simple_info_page.html', msg="Access failed with this token")
    else:
        with open("./app/home/data/ha_token.json", "w") as f:
            f.write(json.dumps({"token": request.form['token']}))
        return render_template('simple_info_page.html', msg="ok, HA token has saved")


@blueprint.route('/ha_entities')
def ha_entities():
    with open("./app/home/data/ha_token.json", "r") as f:
        d = json.loads(f.read())
    token = d['token']
    if token is None:
        return redirect(url_for("home_blueprint.ha_index"))
    ha = HomeAssistant(ip="localhost", port="8123", token=token)
    if not ha.is_connected():
        return redirect(url_for("home_blueprint.ha_index"))

    entities = ha.get_all_entity()

    return render_template("ha_entities.html", entities=entities, ent_len=len(entities))


@blueprint.route('/bad_entities', methods=['POST'])
def bad_entities():
    s = request.form['bad_entities']
    s = s.replace('[', '')
    s = s.replace(']', '')
    s = s.replace('\r\n', '')
    s = s.replace(' ', '')
    bad_entities_id = [ele for ele in s.split(',') if ele.strip()]

    with open("./app/home/data/ha_token.json", "r") as f:
        d = json.loads(f.read())
    token = d['token']
    if token is None:
        return redirect(url_for("home_blueprint.ha_index"))
    ha = HomeAssistant(ip="localhost", port="8123", token=token)
    entities = ha.get_all_entity()
    bad_entities = [e for e in entities if e['entity_id'] in bad_entities_id]

    return render_template('ha_bad_entities.html', entities=bad_entities, ent_len=len(bad_entities))


@blueprint.route('/del_bad_entities', methods=['POST'])
def del_bad_entities():
    s = request.form['bad_entities']
    s = s.replace('[', '')
    s = s.replace(']', '')
    s = s.replace('\r\n', '')
    s = s.replace(' ', '')
    bad_entities_id = [ele for ele in s.split(',') if ele.strip()]
    with open("/home/pi/.homeassistant/.storage/core.entity_registry", "r+") as f:
        org_data = json.loads(f.read())
        org_entities = org_data['data']['entities']
        good_entities = [e for i, e in enumerate(org_entities) if e["entity_id"] not in bad_entities_id]
        org_data['data']['entities'] = good_entities
    with open("/home/pi/.homeassistant/.storage/core.entity_registry", "w") as f:
        f.write(json.dumps(org_data))

    return render_template('simple_info_page.html',
                           msg_title="Delete Success",
                           msg=f'{[e for e in org_entities if e["entity_id"] in bad_entities_id]}')


@blueprint.route('/ha_rebooter')
def ha_rebooter():
    return render_template("ha_rebooter.html")


@blueprint.route('/ha_rebooter/reboot', methods=['POST'])
def ha_rebooted():
    os.system("sudo systemctl restart homeassistant.service")
    return render_template('simple_info_page.html', msg="ok, restarting home assistant service.")


@blueprint.route('/demo')
def demo_page():
    return render_template("index.html")


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
