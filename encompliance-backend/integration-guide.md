# Integration, Testing, and Deployment Guide

This guide provides instructions for integrating the Encompliance.io frontend with the backend, testing the integration, and deploying both applications to production.

## 1. Integration Setup

The integration between the frontend and backend components has been set up as follows:

1. **Frontend Service Files**:
   - `api.ts`: Base API client for making HTTP requests
   - `authService.ts`: Authentication services (login, signup, token management)
   - `pdfService.ts`: PDF document management
   - `aiService.ts`: AI chatbot integration
   - `userService.ts`: User profile management
   - `paymentService.ts`: Stripe payment processing

2. **Authentication Context**:
   - `AuthContext.tsx`: Manages authentication state throughout the application

3. **Environment Configuration**:
   - Frontend: `.env` file with `VITE_API_BASE_URL` pointing to the backend
   - Backend: `.env` file with database, storage, and API settings

## 2. Testing the Integration

### 2.1. Start the Backend

1. Create a PostgreSQL database:
   ```bash
   # Install PostgreSQL if not already installed
   # Create a database named 'encompliance'
   createdb encompliance
   ```

2. Set up MinIO for local storage:
   ```bash
   # Pull and run MinIO using Docker
   docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
   ```

3. Configure the backend environment:
   ```bash
   # Navigate to the backend directory
   cd encompliance-backend
   
   # Create a Python virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Update .env file with your configuration details
   # Especially:
   # - DATABASE_URL
   # - AI_MODEL_API_KEY (if using OpenAI)
   # - STRIPE_API_KEY (if testing payments)
   ```

4. Start the backend server:
   ```bash
   # Development mode
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using Docker Compose (recommended)
   docker-compose up -d
   ```

5. Verify the backend is running by accessing:
   - API documentation: http://localhost:8000/api/v1/docs
   - Health check: http://localhost:8000/health

### 2.2. Start the Frontend

1. Configure the frontend environment:
   ```bash
   # Navigate to the frontend directory
   cd encompliance
   
   # Install dependencies
   npm install
   
   # Update .env file with your backend URL (if different from default)
   # Default is: VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

2. Start the frontend development server:
   ```bash
   npm run dev
   ```

3. Access the frontend at: http://localhost:5173

### 2.3. Test Each Integration Point

#### Authentication
1. Test user registration:
   - Fill out the signup form
   - Complete the state selection
   - Verify account creation and redirection to the dashboard

2. Test user login:
   - Use registered credentials
   - Verify successful authentication and access to protected routes

#### PDF Document Management
1. Test document upload:
   - Navigate to document upload page
   - Upload a PDF file
   - Verify successful upload and file display

2. Test document retrieval:
   - Verify uploaded documents appear in the user's dashboard
   - Test document viewing functionality

#### AI Chatbot
1. Test chat functionality:
   - Navigate to document viewer or chat section
   - Submit queries about Texas childcare regulations
   - Verify meaningful responses from the AI

#### User Profile Management
1. Test profile updates:
   - Navigate to user profile page
   - Update user information
   - Verify changes are saved and displayed correctly

#### Payment Processing (if implemented)
1. Test subscription purchase:
   - Navigate to subscription page
   - Select a subscription plan
   - Complete checkout using Stripe test cards
   - Verify subscription status update

## 3. Deployment

### 3.1. Backend Deployment (AWS)

1. **Set up AWS infrastructure** using the Terraform configurations in `deployment/terraform`:
   ```bash
   cd encompliance-backend/deployment/terraform
   
   # Initialize Terraform
   terraform init
   
   # Plan deployment
   terraform plan -out=tfplan
   
   # Apply configuration
   terraform apply tfplan
   ```

2. **Build and push Docker image**:
   ```bash
   # Build Docker image
   docker build -t encompliance-backend .
   
   # Tag for AWS ECR
   docker tag encompliance-backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/encompliance-backend:latest
   
   # Push to ECR
   aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
   docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/encompliance-backend:latest
   ```

3. **Configure environment variables** for production:
   - Update the ECS task definition with production environment variables
   - Ensure secrets are stored securely in AWS Secrets Manager

### 3.2. Frontend Deployment

1. **Build the frontend**:
   ```bash
   cd encompliance
   
   # Set production API URL in .env
   echo "VITE_API_BASE_URL=https://api.encompliance.io/api/v1" > .env.production
   
   # Build for production
   npm run build
   ```

2. **Deploy to hosting service** (AWS S3 + CloudFront, Vercel, Netlify):

   For AWS S3 + CloudFront:
   ```bash
   # Sync build directory to S3
   aws s3 sync dist/ s3://encompliance-website/
   
   # Invalidate CloudFront cache
   aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"
   ```

   For Vercel:
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Deploy
   vercel --prod
   ```

### 3.3. Domain and SSL Configuration

1. **Configure domains**:
   - Frontend: `encompliance.io`
   - Backend API: `api.encompliance.io`

2. **Set up SSL certificates**:
   - Using AWS Certificate Manager for AWS deployments
   - Using Let's Encrypt for other hosting providers

### 3.4. Monitoring and Logging

1. **Set up monitoring** for both applications:
   - AWS CloudWatch for backend
   - Frontend error tracking using a service like Sentry

2. **Configure alerts**:
   - Set up alerts for API errors, high latency, and service disruptions

## 4. Post-Deployment Verification

1. **Verify API functionality**:
   - Test all API endpoints using Postman or a similar tool
   - Verify proper authentication and authorization

2. **Test frontend against production API**:
   - Perform end-to-end testing of all features
   - Verify correct integration with backend services

3. **Monitor for errors**:
   - Check for any errors in logs
   - Address any issues that arise

## 5. Continuous Integration/Deployment

1. **Set up CI/CD pipeline** using GitHub Actions or AWS CodePipeline:
   - Automatic testing
   - Deployment to staging environment
   - Production deployment after approval

2. **Implement blue/green deployment** for zero-downtime updates:
   - Deploy new version alongside existing version
   - Switch traffic when new version is verified

## 6. Security Considerations

1. **Regular security scanning**:
   - Run vulnerability scans on dependencies
   - Perform penetration testing

2. **Keep dependencies updated**:
   - Regularly update libraries and frameworks
   - Address security vulnerabilities promptly

3. **Implement proper CORS settings**:
   - Restrict API access to known domains
   - Use secure headers

## 7. Backup and Recovery

1. **Database backups**:
   - Configure automated backups for PostgreSQL database
   - Test restoration process

2. **S3 data redundancy**:
   - Ensure cross-region replication for critical data
   - Implement proper data lifecycle policies 