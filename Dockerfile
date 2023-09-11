# Docker file to install Python Flask Modules and Run the Application

FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose PORT FLASK_PORT in .env to outside world
EXPOSE $FLASK_PORT

# Run app.py when the container launches
CMD ["python", "app.py"]