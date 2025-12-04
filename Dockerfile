# Base image with Python
FROM python:3.11-slim

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# 1. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install Node.js dependencies
COPY web/package.json web/package-lock.json* ./web/
WORKDIR /app/web
RUN npm install

# 3. Copy source code
WORKDIR /app
COPY . .

# 4. Build Next.js app
WORKDIR /app/web
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
