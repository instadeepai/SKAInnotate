# Google OAuth 2.0 Authentication Setup Guide

This guide provides step-by-step instructions on how to set up Google OAuth 2.0 authentication for SKAInnotate.

## Step 1: Enable Google OAuth 2.0 API

1. In the Google Cloud Console, navigate to **APIs & Services** > **Library**.
2. Ensure the right project is selected
3. Search for **Google People API**.
4. Click on it, then click **Enable**.

## Step 3: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** > **Credentials**.
2. Click on **Create Credentials** > **OAuth client ID**.
3. Set up the OAuth 2.0 Client ID:
   - Choose **Web application**.
   - Add **Authorized JavaScript origins** (e.g., `https://skainnotate.app`). 
   (This step should be done after the application is deployed and cloud url is obtained)
   - Click **Create**.
4. Copy and paste the **Client ID** into the SKAInnotate Deployment form.