import json
import click
from gbdxtools import Interface


@click.command()
@click.argument('task_definition', type=click.Path(exists=True, writable=True, dir_okay=False, resolve_path=True))
@click.option('--version', default=None, help='The task version to deploy. If not provided, defaults to the current version in the task definition.')
def register_task(task_definition, version):
    """Register this task with GBDX using the provided version."""

    # Create the interface instance
    gbdx = Interface()
    print('Created GBDX Interface instance')

    # Write the new version, if present
    if version is not None:
        print('Writing new version {version} to {task_definition}'.format(version=version, task_definition=task_definition))
        with open(task_definition, 'rb') as f:
            definition = json.load(f)
        definition['version'] = version
        with open(task_definition, 'wb') as f:
            json.dump(definition, f)

    # Load the (possibly updated) definition
    print('Loading task definition from {task_definition}'.format(task_definition=task_definition))
    with open(task_definition, 'rb') as f:
        definition = json.load(f)

    # Construct the full task name with version
    version = definition['version']
    task_name = definition['name']
    full_name = '{task_name}:{version}'.format(task_name=task_name, version=version)

    # If the task is already present, delete it
    if full_name in gbdx.task_registry.list():
        print('Deleting existing task {full_name}'.format(full_name=full_name))
        gbdx.task_registry.delete(full_name)

    print('Registering task {full_name}'.format(full_name=full_name))
    response = gbdx.task_registry.register(task_json=definition)

    if str(response) == '{full_name} has been submitted for registration':
        print(response)
    else:
        print(response)


if __name__ == '__main__':
    register_task()
