# Deploying Encompliance.io to Render.com

This guide will walk you through deploying the Encompliance.io application to Render.com.

## Prerequisites

1. A Render.com account (you've already created one using your GitHub login)
2. The deployment files prepared in the `deploy` directory

## Step 1: Deploy the PostgreSQL Database

1. Log in to your Render.com account at https://dashboard.render.com/
2. Click on "New +" in the top right corner
3. Select "PostgreSQL" from the dropdown menu
4. Fill in the following details:
   - Name: `encompliance-db`
   - Database: `encompliance`
   - User: `encompliance_user`
   - Region: Choose the region closest to your users
   - Plan: Select the free plan
5. Click "Create Database"
6. Wait for the database to be provisioned (this may take a few minutes)
7. Once provisioned, note the "Internal Database URL" - you'll need this for the backend

## Step 2: Deploy the Backend

1. In the Render.com dashboard, click on "New +" in the top right corner
2. Select "Web Service" from the dropdown menu
3. Click on "Build and deploy from a Git repository"
4. You'll be prompted to connect your GitHub account if you haven't already
5. Click on "Configure account" for GitHub
6. Authorize Render.com to access your GitHub repositories
7. Create a new GitHub repository for the backend:
   ```
   cd deploy/backend
   git remote add origin https://github.com/YOUR_USERNAME/encompliance-backend.git
   git push -u origin main
   ```
8. Refresh the Render.com page and select your new repository
9. Fill in the following details:
   - Name: `encompliance-backend`
   - Environment: `Python 3`
   - Region: Choose the same region as your database
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Select the free plan
10. Under "Advanced", add the following environment variables:
    - `DATABASE_URL`: Paste the Internal Database URL from Step 1
    - `JWT_SECRET_KEY`: Generate a random string (you can use https://www.uuidgenerator.net/)
    - `ACCESS_TOKEN_EXPIRE_MINUTES`: `10080`
    - `FRONTEND_URL`: Leave blank for now (we'll update this after deploying the frontend)
    - `ENCRYPTION_KEY`: Generate another random string
    - `PDF_STORAGE_PATH`: `/var/data/encompliance-documents`
11. Click "Create Web Service"
12. Wait for the deployment to complete (this may take several minutes)
13. Once deployed, note the URL of your backend service (e.g., `https://encompliance-backend.onrender.com`)

## Step 3: Deploy the Frontend

1. In the Render.com dashboard, click on "New +" in the top right corner
2. Select "Static Site" from the dropdown menu
3. Click on "Build and deploy from a Git repository"
4. Create a new GitHub repository for the frontend:
   ```
   cd deploy/frontend
   git remote add origin https://github.com/YOUR_USERNAME/encompliance-frontend.git
   git push -u origin main
   ```
5. Refresh the Render.com page and select your new repository
6. Fill in the following details:
   - Name: `encompliance-frontend`
   - Environment: `Node`
   - Region: Choose the same region as your backend
   - Branch: `main`
   - Build Command: `npm ci && npm run build`
   - Publish Directory: `dist`
   - Plan: Select the free plan
7. Under "Advanced", add the following environment variables:
   - `VITE_API_URL`: `https://encompliance-backend.onrender.com/api` (use the backend URL from Step 2)
8. Click "Create Static Site"
9. Wait for the deployment to complete
10. Once deployed, note the URL of your frontend service (e.g., `https://encompliance-frontend.onrender.com`)

## Step 4: Update Backend with Frontend URL

1. Go back to your backend service in the Render.com dashboard
2. Click on "Environment" in the left sidebar
3. Add or update the `FRONTEND_URL` environment variable with your frontend URL from Step 3
4. Click "Save Changes"
5. This will trigger a redeployment of the backend

## Step 5: Test Your Deployed Application

1. Once both services are deployed, visit your frontend URL in a web browser
2. Test the application functionality to ensure everything is working correctly

## Troubleshooting

If you encounter any issues during deployment, check the logs in the Render.com dashboard for error messages. The most common issues are related to environment variables or database connections.

- For backend issues, check the "Logs" tab in your Web Service
- For frontend issues, check the "Logs" tab in your Static Site
- For database issues, check the "Logs" tab in your PostgreSQL service

## Next Steps

Once your application is deployed and working correctly, you can:

1. Set up a custom domain for your application
2. Configure SSL certificates
3. Set up automatic deployments from your GitHub repository
4. Configure backup and restore for your database

Refer to the Render.com documentation for more information on these topics. 