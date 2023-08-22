# Set base image (host OS)
FROM python:3.11

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /MTG app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
# Need to add rest of app
COPY web.py .
COPY config.json .
COPY app/* ./app/
COPY static/* ./static/
COPY templates/* ./templates/

# Specify the command to run on container start
CMD [ "python", "./web.py" ]