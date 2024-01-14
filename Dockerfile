# Use an official Python runtime as a parent image
FROM python:3.12
RUN apt-get update && apt-get install -y python3-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install Rust and required build tools
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"


# Copy the current directory contents into the container at /app
COPY code /app/

# Copy .env
COPY .env /app/.env

# Create the virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Activate venv
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the requirements file into the container
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Generate PyO3 modules with maturin
RUN cd /app/rust_extensions && maturin develop

# Run Django migrations and start the development server
# Command to run the Django development server within the virtual environment
CMD ["/bin/bash", "-c", "if [ -n \"$VIRTUAL_ENV\" ]; then echo \"Virtual environment is activated: $VIRTUAL_ENV\"; else echo \"Virtual environment is not activated\"; fi && python manage.py runserver 0.0.0.0:8989"]
