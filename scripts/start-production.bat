@echo off
REM ==========================================
REM Production Startup Script for Agentic AI (Windows)
REM ==========================================

echo Starting Agentic AI Production Deployment...

REM Check if .env file exists
if not exist .env (
    echo .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit .env file with your configuration before proceeding!
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: docker-compose is not installed
    exit /b 1
)

echo Prerequisites check passed

REM Build images
echo Building Docker images...
docker-compose build --no-cache

REM Start services
echo Starting Docker services...
docker-compose up -d

REM Wait for PostgreSQL
echo Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Initialize database
echo Initializing database...
docker-compose exec -T postgres psql -U agenticai -d agenticai_db -f /docker-entrypoint-initdb.d/init-db.sql

REM Run migrations
echo Running database migrations...
docker-compose exec -T api alembic upgrade head

REM Check service health
echo Checking service health...
timeout /t 5 /nobreak >nul

curl -f http://localhost/health >nul 2>&1
if errorlevel 1 (
    echo API health check failed
    docker-compose logs api
) else (
    echo API is healthy
)

echo.
echo ==========================================
echo Agentic AI is now running!
echo ==========================================
echo.
echo API URL: http://localhost
echo API Docs: http://localhost/docs
echo Grafana: http://localhost:3000 (admin/admin)
echo Prometheus: http://localhost:9090
echo RabbitMQ: http://localhost:15672 (guest/guest)
echo.
echo Useful commands:
echo    View logs:    docker-compose logs -f
echo    Stop:         docker-compose down
echo    Restart:      docker-compose restart
echo    Shell:        docker-compose exec api bash
echo.
