# SKAInnotate

## Overview

SKAInnotate consists of two primary components:

1. **Google Cloud Infrastructure Setup**: This includes setting up the project, database, authentication, container image, and Cloud Run deployment.

The setup can also be run locally at http://127.0.0.1 or http://localhost.
   
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
   - [Usage](#usage)

---

## Google Cloud Infrastructure Setup

This section guides you through setting up the Google Cloud infrastructure necessary for the data annotation web application.

### Project Setup

1. **Create a Virtual Environment**:  
   Create a virtual environment and install required libraries:

    ```sh
    pip install -r requirements.txt
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
    uvicorn setup.backend.app.main:app --reload --port <PORT>
    ```
4. **Install Google Cloud SDK**: \
   Ensure you have [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticate.
   ```sh
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
### Database Setup

1. **Cloud SQL Configuration**:  
   Set up the Cloud SQL instance and provide necessary details like instance name, region, database name, user, and password.

   If you need to create a new Google Cloud SQL Instance, refer to the [Cloud SQL guide](setup/docs/setup_sql.md)

### Google Authentication Setup

Set up a Google Cloud OAuth 2.0 authentication for the application and provide Client ID in setup form. Detailed instructions on [Authentication setup](setup/docs/setup_authentication.md)

### Container Image Setup

<!-- 1. **Build and Push Container Image**:  
   Choose your build option (`local`, `cloud`, or `none`). The container image will either be built locally or using `gcloud builds submit` and pushed to Google Artifact Registry. -->

### Cloud Run Deployment

1. **Deploy to Cloud Run**:  
   Deploy the containerized application to Cloud Run by providing a service name. The deployment URL can be found in the Cloud Run console.

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

### Roles and Functionalities

- **Admins**:  
  Can create projects, configure settings, add/remove users, upload and assign tasks, and retrieve annotations.

- **Annotators**:  
  Receive tasks, annotate data, and submit annotations.

- **Reviewers**:  
  Review submitted annotations and provide final annotation.

---

## Sample Deployment

You can explore a sample deployment at:

```plaintext
https://skainnotate-demo-kse2o5g36a-uc.a.run.app
```

> Note: You must be assigned an appropriate role (admin, annotator, or reviewer) to access relevant functionalities.
