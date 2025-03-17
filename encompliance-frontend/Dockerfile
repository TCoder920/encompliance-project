# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Install terser for production build
RUN npm install -D terser

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"] 