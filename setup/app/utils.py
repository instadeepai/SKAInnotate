from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi.responses import RedirectResponse

async def create_cloudsql_instance(credentials, instance_configs):
    if not credentials:
        return RedirectResponse(url='/authorize')

    sqladmin = build('sqladmin', 'v1beta4', credentials=credentials)

    instance_body = {
        'name': instance_configs['instance_name'],
        'settings': {
            'tier': 'db-f1-micro',
        },
        'databaseVersion': 'POSTGRES_15',  # Using PostgreSQL 15
        'region': instance_configs['region']
    }

    try:
        # Check if instance exists
        sqladmin.instances().get(
            project=instance_configs['project_id'],
            instance=instance_configs['instance_name']
        ).execute()
        instance_exists = True
    except HttpError as e:
        if e.resp.status == 404:
            instance_exists = False
        else:
            return {"error": f"Failed to check instance existence: {str(e)}"}

    if not instance_exists:
        try:
            request = sqladmin.instances().insert(
                project=instance_configs['project_id'],
                body=instance_body
            )
            response = request.execute()
            instance_created = True
        except HttpError as e:
            return {"error": f"Failed to create instance: {str(e)}"}
    else:
        instance_created = False

    database_body = {
        'name': instance_configs['database_name'],
    }

    try:
        # Checking if database exists
        sqladmin.databases().get(
            project=instance_configs['project_id'],
            instance=instance_configs['instance_name'],
            database=instance_configs['database_name']
        ).execute()
        database_exists = True
    except HttpError as e:
        if e.resp.status == 404:
            database_exists = False
        else:
            return {"error": f"Failed to check database existence: {str(e)}"}

    if not database_exists:
        try:
            request = sqladmin.databases().insert(
                project=instance_configs['project_id'],
                instance=instance_configs['instance_name'],
                body=database_body
            )
            response = request.execute()
            return {"message": f"Cloud SQL Database '{instance_configs['database_name']}' created in instance '{instance_configs['instance_name']}': {response}"}
        except HttpError as e:
            return {"error": f"Failed to create database: {str(e)}"}
    else:
        return {"message": f"Cloud SQL Database '{instance_configs['database_name']}' already exists in instance '{instance_configs['instance_name']}'."}
