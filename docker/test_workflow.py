from gbdxtools import Interface
import boto3

gbdx = Interface()
sts = boto3.client('sts')

creds = sts.get_session_token()['Credentials']

ingest = gbdx.Task(
    'ingest-s3-data',
    data='s3://viper-projects/open_data/intermediate/PreprocessImage/1030010069650A00/059441867010_01/',
    aws_access_key_id=creds['AccessKeyId'],
    aws_secret_access_key=creds['SecretAccessKey'],
    aws_session_token=creds['SessionToken']
)

cog = gbdx.Task(
    'CloudOptimizedGeoTIFF:2.0.0',
    data=ingest.outputs.data.value,
)

save = gbdx.Task(
    'SaveToS3',
    data=cog.outputs.data.value,
    destination='s3://jduckworth/cog-tests/1030010069650A00',
    access_key_id=creds['AccessKeyId'],
    secret_key=creds['SecretAccessKey'],
    session_token=creds['SessionToken'],
)

workflow = gbdx.Workflow([ingest, cog, save])
workflow.execute()

print(workflow.id)
