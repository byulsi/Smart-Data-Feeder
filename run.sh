#!/bin/bash

# 1. Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 2. Function to run collector
run_collector() {
    if [ -z "$1" ]; then
        echo "Usage: ./run.sh collect [ticker]"
        echo "Example: ./run.sh collect 005930"
        exit 1
    fi
    echo "Running Data Collector for $1..."
    python collector.py "$1"
}

# 3. Function to run web server
run_web() {
    echo "Starting Web Application..."
    cd web
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    fi
    npm run dev
}

# 4. Main logic
if [ "$1" == "collect" ]; then
    run_collector "$2"
elif [ "$1" == "web" ]; then
    run_web
else
    echo "Antz - Easy Runner"
    echo "-------------------------------"
    echo "1. To collect data:  ./run.sh collect [Ticker]"
    echo "   Example: ./run.sh collect 005930"
    echo ""
    echo "2. To start website: ./run.sh web"
    echo "-------------------------------"
fi
