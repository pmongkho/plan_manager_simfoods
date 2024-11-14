# Stage 1: Build Angular frontend
FROM node:22 AS frontend-builder
WORKDIR /app/client

# Install Angular CLI and dependencies
COPY client/package*.json ./
RUN npm install -g @angular/cli@18.0.7
RUN npm install
COPY client/ .  
RUN ng build --configuration production

# Stage 2: Set up Django backend
FROM python:3.12 AS backend
WORKDIR /app

# Copy Django backend files
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app

# Collect static files from Angular build
COPY --from=frontend-builder /app/client/dist/client /app/staticfiles

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=project.settings 

# Expose port 8000 for Django
EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
