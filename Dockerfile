# Use an official Python image as the base
FROM python:3.11-slim-buster

# Set environment variables (customize as needed)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /civs

# Install system dependencies (if any)
# For example, if you need PostgreSQL, uncomment the following line:
# RUN apt-get update && apt-get install -y postgresql-client

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the Django project code into the container
COPY . .

# Expose the port your Django app will run on (usually 8000)
EXPOSE 8000

# Run migrations and start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
