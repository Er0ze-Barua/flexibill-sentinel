FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for compiling database drivers
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code into the container
COPY . .

# Expose the standard interface port
EXPOSE 8501

# Run the Streamlit server with dynamic network port binding
CMD ["sh", "-c", "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]