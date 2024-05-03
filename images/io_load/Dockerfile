# create a dockerfile to build an image with python3.11 and httpd

# Pull the base image
FROM python:3.11

# Set the working directory
WORKDIR /

# Copy the current directory contents into the container at /app
COPY ./src /src

# Install any needed packages specified in requirements.txt
RUN apt-get update
RUN pip install requests 
RUN apt install -y vim
RUN pip install flask
RUN pip install numpy

# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 9376

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["sleep", "infinity"]
