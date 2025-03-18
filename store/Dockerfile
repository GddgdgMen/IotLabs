# Use a stable Python version (Python 3.11)
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Rust properly
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    echo 'source $HOME/.cargo/env' >> ~/.bashrc
ENV PATH="/root/.cargo/bin:${PATH}"

# Verify Rust installation
RUN rustc --version

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]