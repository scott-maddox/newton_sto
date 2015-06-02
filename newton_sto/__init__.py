# Copyright (c) 2015, Scott J Maddox. All rights reserved.
# Use of this source code is governed by the BSD-3-Clause
# license that can be found in the LICENSE file.

# std lib imports
import os

# third party imports
from flask import Flask, render_template, request, Response

# local imports
from .system_config import systems
from .target import Target
from .generate_sto import generate_sto

app = Flask(__name__)
app.config.from_object(dict(
    WTF_CSRF_ENABLED=True,
    SECRET_KEY=os.urandom(24),
    ))

@app.route('/', methods=['GET'])
def index():
    system_info = {}
    for system, cells in systems.items():
        system_info[system] = cells.keys()
    return render_template('index.html', system_info=system_info)

@app.route('/newton_sto.txt', methods=['POST'])
def newton_sto_txt():
    system_name = request.form['system_select']
    if system_name not in systems:
        return "Error: unkown system name"
    system_cells = systems[system_name]

    targets = []
    for cell_name in request.form.get('cells', '').split():
        if cell_name + '_checkbox' in request.form:
            cell = system_cells[cell_name]
            bep_str = request.form.get(cell_name + '_bep', '')
            temp_str = request.form.get(cell_name + '_temp', '')
            try:
                bep = float(bep_str)
            except:
                return 'Invalid {} BEP: "{}"'.format(cell_name, bep_str)
            try:
                temp = float(temp_str)
            except:
                return 'Invalid {} temperature: "{}"'.format(cell_name, temp_str)
            targets.append(Target(cell, bep, temp))


    kwargs = dict(
        targets=targets,
        num_temps=int(request.form.get('num_temps', 4)),
        num_shutterings=int(request.form.get('num_shutterings', 3)),
        num_samples=int(request.form.get('num_samples', 3)),
        temp_tolerance=float(request.form.get('temp_tolerance', 0.2)),
        bf_var=request.form.get('bf_var', 'bf'),
        update_time=int(request.form.get('update_time', 10)),
    )
    return Response(generate_sto(**kwargs),
                    content_type='text/plain')

@app.route('/get_cells', methods=['POST'])
def get_cells():
    system_name = request.form['system_select']
    if system_name not in systems:
        return "Error: unkown system name"
    cell_names = [cell_name for cell_name in systems[system_name].keys()]
    return render_template('cells.html', cell_names=cell_names)
