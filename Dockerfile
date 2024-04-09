# Use an official Python runtime as a parent image
FROM python:3.11.9-slim
LABEL authors="akivanotkin"

ENV PYTHONUNBUFFERED=1

# Copy the current directory contents into the container at /app
COPY src/ /app
COPY requirements.txt /app
COPY data/ /app

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Install any needed packages specified in requirements.txt

ENV PYTHONPATH=..

# Make port 5000 available to the world outside this container
EXPOSE 5000

ENTRYPOINT ["python3"]
WORKDIR /app/fake_the_spire
CMD ["run.py"]
