import os
import json
from gbdxtools import Interface
import inspect
from psma_process import psma_tools as tools
import simplepaths
local_path = simplepaths.fixpaths('pabst', inspect.currentframe())

# Load default params
default_params = tools.read_params(os.path.join(local_path, 'default_params.json'))

# Task definition file
task_definition_fp = 'gbdx_tasks/CloudOptimizedGeoTIFF/register-task.json'

# Create the interface instance
gbdx = Interface(
    username=default_params['gbdx']['username'],
    password=default_params['gbdx']['password'],
    client_id=default_params['gbdx']['client_id'],
    client_secret=default_params['gbdx']['client_secret']
)

# # Register the task
gbdx.task_registry.delete('CloudOptimizedGeoTIFF:0.1.2')
gbdx.task_registry.register(json_filename=task_definition_fp)

# # Update the task
# with open(task_definition_fp, 'r') as task_def:
#     task_json = json.load(task_def)
#
# gbdx.task_registry.update(
#     task_name='CloudOptimizedGeoTIFF',
#     task_json=task_json
# )


# Test out the task
try:
    cloud_geotiff_task = gbdx.Task('CloudOptimizedGeoTIFF')
except AttributeError:
    print('Not created yet')

cloud_geotiff_task.definition


