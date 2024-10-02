# SKAInnotate

## Overview

**SKAInnotate** is a versatile platform designed to streamline data annotation tasks. It comprises two main components:

1. **Google Cloud Infrastructure Setup**:  
   This comprises setup of essential Google Cloud services, including project configuration, database setup, authentication and Cloud Run deployment.

2. **Web Application for Data Annotation**:  
   A user-friendly, web-based platform tailored for data annotation with role-based access for annotators, reviewers, and admins.

---

## Google Cloud Infrastructure Setup

This section provides step-by-step instructions to set up the Google Cloud infrastructure required to run the SKAInnotate web application.

### Project Setup

1. **Install Google Cloud SDK**:  
   Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed, and authenticate with your Google account.

   ```sh
      gcloud auth login
      gcloud config set project YOUR_PROJECT_ID
   ```
2. **Set Up Google Cloud SQL and OAuth**:
   Create a Google Cloud SQL instance and configure OAuth for authentication. Refer to the following guides for detailed instructions:

   * [Cloud SQL Setup](/setup/docs/)
   * [OAuth Setup](/setup/docs/)
3. Clone the Repository:
   Clone the SKAInnotate repository and navigate to the project directory:
   
   ```sh
      git clone https://github.com/instadeepai/SKAInnotate.git
      cd SKAInnotate
   ```
4. Create a Virtual Environment and Install Dependencies:
   Set up a Python virtual environment and install the required libraries:

   ```sh
      python3 -m venv env
      source env/bin/activate
      pip install -r requirements.txt
   ```

5. Run the Setup Script:
   Execute the setup script to build the server:

```sh
bash setup.sh <PORT> <OS>   # <OS> defaults to linux, e.g., bash setup.sh 8000 macos
```
To start the backend server in future sessions, you can run:

```sh
uvicorn setup.backend.app.main:app --reload --port <PORT>
```
The setup can run locally (e.g., `http://127.0.0.1` or `http://localhost`) and hosted on Google Cloud.

6. Launch Application Deployment:
   Provide necessary project details (Google Cloud SQL, OAuth credentials, etc.) and click the Launch button to deploy the application.

   After deployment, update the Authorized JavaScript Origins in your OAuth 2.0 settings with the URL provided by the setup form. Then, open the deployment URL in your browser to begin using SKAInnotate.

## Web Application for Data Annotation
### Application Overview
   The SKAInnotate web application enables seamless data annotation by providing a role-based system with the following roles:
   
   **Admins:** Manage projects, tasks, and users.
   **Annotators:** Perform data annotations.
   **Reviewers:** Review and validate annotations submitted by annotators.
   
### Roles and Functionalities
   **Admins:**
   * Create and manage annotation projects.
   * Configure project settings.
   * Add or remove users.
   * Upload and assign annotation tasks.
   * Retrieve completed annotations.
     
   **Annotators:**
   * Receive and complete annotation tasks.
   * Submit annotations to the system.
     
   **Reviewers:**
   * Review the annotations submitted by annotators.
   * Approve or modify annotations as needed.
   
   ### Usage
   1. Access the Application:
   Once the application is deployed, open the following URL in a web browser to access SKAInnotate:
   
   ```plaintext
   https://<service-name>-<hashing>-<region>.a.run.app
   ```
   2. Login and Select Role:
   Use Google Authentication to log in and select your role (admin, annotator, or reviewer) based on your permissions.
   
   3. Start Annotating:
   Once logged in, admins can manage projects and tasks, while annotators and reviewers can begin working on assigned tasks.
