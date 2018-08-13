from gbdxtools import Interface
from pprint import pprint

gbdx = Interface()

co_task = gbdx.Task('CloudOptimizedGeoTIFF:0.2.0', data='s3://jduckworth/cloud-optimized-geotiff-test/input/')
s3_task = gbdx.Task('StageDataToS3', data=co_task.outputs.data.value, destination='s3://jduckworth/cloud-optimized-geotiff-test/output/')

w = gbdx.Workflow([co_task, s3_task])
w_id = w.execute()

pprint(w.events)
pprint(w.stdout)
