# SKAInnotate

## Overview

SKAInnotate consists of two primary components:

1. **Google Cloud Infrastructure Setup**: This includes setting up the project, database, authentication, container image, and Cloud Run deployment. It can also run locally on [localhost](http://127.0.0.1:8000) or [http://localhost:8000](http://localhost:8000).
   
2. **Web Hosted Application for Data Annotation**: A user-friendly web application designed for data annotation tasks with roles for annotators, reviewers, and admins.

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

---

## Google Cloud Infrastructure Setup

This section guides you through setting up the Google Cloud infrastructure necessary for the data annotation web application.

### Project Setup

1. **Create a Virtual Environment**:  
   Create a virtual environment and install FastAPI and Uvicorn:

    ```sh
    pip install fastapi 'uvicorn[standard]'
    ```

2. **Clone the Repository**:  
   Clone the SKAInnotate repository:

    ```sh
    git clone https://github.com/instadeepai/SKAInnotate.git
    cd SKAInnotate
    ```

3. **Run the Setup Server**:  
   Start the FastAPI server to initiate the project setup:

    ```sh
    uvicorn setup.app.main:app --reload --port 8000
    ```

### Database Setup

1. **Cloud SQL Configuration**:  
   Set up the Cloud SQL instance and provide necessary details like instance name, region, database name, user, and password.

### Google Authentication Setup

1. **Enable OAuth 2.0 APIs**:  
   - In Google Cloud Console, navigate to `APIs & Services > Library`.
   - Search for **Google Identity Toolkit API** or **OAuth 2.0 API**, and click `Enable`.

2. **Configure OAuth 2.0 Credentials**:
   - Create OAuth 2.0 Client IDs in `APIs & Services > Credentials`.
   - Fill in the necessary details for OAuth consent screen and set the **Authorized JavaScript Origins** to your web application URL.
   - Copy the Client ID and Client Secret for later use.

### Container Image Setup

1. **Build and Push Container Image**:  
   Choose your build option (`local`, `cloud`, or `none`). The container image will either be built locally or using `gcloud builds submit` and pushed to Google Artifact Registry.

### Cloud Run Deployment

1. **Deploy to Cloud Run**:  
   Deploy the containerized application to Cloud Run by providing a service name and region. The deployment URL can be found in the Cloud Run console.

2. **Update OAuth 2.0 Credentials**:  
   After deployment, update the **Authorized JavaScript Origins** in your OAuth 2.0 settings with the frontend deployment URL.

---

## Web Hosted Application for Data Annotation

### Application Overview

The SKAInnotate web application facilitates data annotation tasks. It includes roles for **admins**, **annotators**, and **reviewers**, each with specific functionalities.

### Usage

1. **Access the Application**:  
   Open a web browser and navigate to the deployed Cloud Run URL:

   ```plaintext
   https://<service-name>-<hashing>-<region>.a.run.app
   ```

2. **Update OAuth Redirect URI**:  
   Add the following redirect URI to your OAuth settings:

   ```plaintext
   https://<service-name>-<hashing>-<region>.a.run.app/auth/oauth2callback
   ```

### Roles and Functionalities

- **Admins**:  
  Can create projects, configure settings, add/remove users, upload and assign tasks, and retrieve annotations.

- **Annotators**:  
  Receive tasks, annotate data, and submit annotations.

- **Reviewers**:  
  Review submitted annotations and provide feedback.

---

## Sample Deployment

You can explore a sample deployment at:

```plaintext
https://skainnotate-demo-kse2o5g36a-uc.a.run.app
```

> Note: You must be assigned an appropriate role (admin, annotator, or reviewer) to access relevant functionalities.