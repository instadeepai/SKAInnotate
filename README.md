# SKAInnotate

## Overview

This project consists of two main components:
1. **Google Cloud Infrastructure Setup**: This includes setting up the project, database, authentication, container image, and Cloud Run deployment and can run locally on localhost (http://127.0.0.1:8000, http://localhost:8000).

2. **Web Hosted Application for Data Annotation**: A web application designed for data annotation tasks, providing a user-friendly interface for annotators, reviewers, and admins.

## Table of Contents
1. [Google Cloud Infrastructure Setup](#google-cloud-infrastructure-setup)
    - [Project Setup](#project-setup)
    - [Database Setup](#database-setup)
    - [Google Authentication Setup](#google-authentication-setup)
    - [Container Image Setup](#container-image-setup)
    - [Cloud Run Deployment](#cloud-run-deployment)
2. [Web Hosted Application for Data Annotation](#web-hosted-application-for-data-annotation)
    - [Application Overview](#application-overview)
    - [Installation](#installation)
    - [Usage](#usage)
3. [Contributing](#contributing)
4. [License](#license)

## Google Cloud Infrastructure Setup

This part of the project involves setting up the necessary Google Cloud infrastructure to support the web hosted application for data annotation.

### Project Setup

1. **Create a virtual environment**:
   Create a virtual environment and install the libraries; fastapi

    ```sh
      pip install fastapi 'uvicorn[standard]'
    ```
### Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/instadeepai/SKAInnotate.git 
    (current active branch: main)

    cd your-repo
    ```

2. **Run the Setup Server**:
    - Start the FastAPI server from the project root and follow the steps to set up the project.
    ```sh
    uvicorn setup.app.main:app --reload --port 8000
    ```
### Project Setup
1. **Set up Project**:
   - Set Project ID and service account path. Service account must have sufficient permissions which are all included in the `Storage Admin` and `Cloud SQL Admin` roles. This will be used to access GCS bucket and Cloud SQL in the next steps.

### Database Setup
1. **Set Up Cloud SQL**:
    - Navigate to the database setup form and provide the necessary details (instance name, region, database name, user, and password).
    - The script will create the Cloud SQL instance and the database if they do not already exist.

### Google Authentication Setup

1. **Enable OAuth 2.0 APIs**:

    * In the Google Cloud Console, navigate to APIs & Services > Library.
    * Search for Google Identity Toolkit API or OAuth 2.0 API.
    Click Enable to activate the API.

2. Configure OAuth 2.0 Credentials
    - Create OAuth 2.0 Client IDs
    Go to APIs & Services > Credentials. \
    Click Create Credentials and select OAuth 2.0 Client ID.
    If prompted, configure your OAuth consent screen:

    -  Application Name: Give your app a name (visible to users).

Once the consent screen is configured, return to the Credentials tab.

In Authorized JavaScript Origins, add the URL where your app will be hosted (e.g., https://yourdomain.com). This is the cloud run frontend link provided after deployment.

Copy the Client ID and Client Secret (you'll need these later).

### Container Image Setup

1. **Build and Push Container Image**:
    - Choose the build option (none, local, or cloud).
    - Provide the container image name.
    - A container image will be built locally if build_option is `local` or built with `google builds submit` and pushed to Google Artifact Registry or use an available container image from artifact registry if build_option is set to `none`.

### Cloud Run Deployment

1. **Deploy to Cloud Run**:
    - Provide the service name and region.
    - Your web application will be deployed in the container image to Cloud Run. Application URL can be found for the cloud run service in cloud Run console.

As a final step, copy the frontend url after deployment.
Navigate to Google OAuth 2.0; APIs & Services > Credentials
In Authorized JavaScript Origins, paste the frontend url to receive requests.


## Web Hosted Application for Data Annotation

### Application Overview

The web application is designed to facilitate data annotation tasks. It includes roles for annotators, reviewers, and admins, each with specific functionalities.


### Usage

1. **Access the Application**:
    - Open a web browser and navigate to the url provided by cloud run.
    format: `https://<service-name>-<hashing>-<region>.a.run.app`
2. **Update OAuth authorized redirect URI**
   - Visit the GCP OAuth settings for the application and add a redirect URI to the Authorized redirect URIs settings. The redirect URI should look like this; `https://<service-name>-<hashing>-<region>.a.run.app/auth/oauth2callback`.
   For instance `https://skainnotate-test-kse2o5g36a-uc.a.run.app/auth/oauth2callback` in the case of the sample deployment app below.


3. **Roles and Functionalities**:
    - **Admins**: Can create projects and set configurations, add/remove users, upload tasks, assign tasks, and retrieve annotations.
    - **Annotators**: Receive tasks, annotate data, and submit annotations.
    - **Reviewers**: Review submitted annotations and provide feedback.

## Sample deployment
```
https://skainnotate-demo-kse2o5g36a-uc.a.run.app
```

In order to access any of the roles and functionalities, you must be assigned the appriopriate role first.