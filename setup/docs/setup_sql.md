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
#### Create Instance
1. In the Google Cloud Console, navigate to **SQL**.
2. Click on **Create Instance**. You might have to enable Compute Engine API and Cloud SQL Admin API if not already enabled.
3. Select **PostgreSQL**.
4. Enter the instance ID, password for the default `postgres` user, and configure other settings (region, machine type, etc.).
5. Click **Create**.

#### Create User
1. Once the instance is created, click on your instance to view its details.
2. In the left-hand menu, click **Users**.
3. Click **Add User Account**.
4. Enter the following details:
   - **User Name**: Choose a username (e.g., `myuser`).
   - **Password**: Set a password for this user.
5. Click **Add** to create the user.

*Note*: It’s good practice to avoid using the default `postgres` user for your application and instead create a dedicated user.

#### Create Database
1. In the left-hand menu, click **Databases**.
2. Click **Create Database**.
3. Enter the following details:
   - **Database Name**: Provide a name for your database (e.g., `skainnotate_db`).
4. Click **Create** to set up the database.
