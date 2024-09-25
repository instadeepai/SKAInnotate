# Google Cloud SQL Database Setup Guide

This document provides step-by-step instructions on how to create a Google Cloud SQL database.

## Step 1: Enable Google Cloud SQL Admin API

1. In the Google Cloud Console, navigate to **APIs & Services** > **Library**.
2. Ensure the right project is selected
3. Search for **Google Cloud SQL Admin API**.
4. Click on it, then click **Enable**.

## Step 2: Create a Google Cloud SQL Instance

You can create a Cloud SQL instance using the Google Cloud Console or via the command line.

### Using Google Cloud Console

1. In the Google Cloud Console, navigate to **SQL**.
2. Click on **Create Instance**.
3. Select **PostgreSQL** (or your desired database type).
4. Enter the instance ID, password for the default `postgres` user, and configure other settings (region, machine type, etc.).
5. Click **Create**.

### Using Command Line

Alternatively, you can use the following command:

```bash
gcloud sql instances create INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=REGION \
    --root-password=YOUR_PASSWORD
