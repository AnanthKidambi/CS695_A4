# create a dockerfile to build an image with python3.11 and httpd

# Pull the base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Install any needed packages specified in requirements.txt
RUN apt-get update 

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]