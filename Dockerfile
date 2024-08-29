# Use the official TensorFlow image as a base
FROM tensorflow/tensorflow:2.13.0

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code into the container
COPY . .

# Expose port 8000 for Flask
EXPOSE 8000

# Command to run the Flask app with Uvicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
