# FutureSelf Backend

This is the backend for the FutureSelf project, built with FastAPI.

## Prerequisites

Before you begin, ensure you have the following installed:
- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Python](https://www.python.org/downloads/) 3.8+

## Getting Started

Follow these steps to get your development environment set up and running.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd FurtureSelf_V1/Backend
```

### 2. Start Services with Docker

The project uses Docker to manage the PostgreSQL database and Redis cache. You can start these services with a single command:

```bash
docker-compose up -d
```

This command will download the necessary images and start the containers in the background. You can check the status of the containers with `docker-compose ps`.

### 3. Set Up Python Environment

It is highly recommended to use a virtual environment to manage Python dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

Once the virtual environment is activated, you can install the project's dependencies.

```bash
# Install the project in editable mode
pip install -e .
```
This command uses the `setup.py` file to install all the required packages listed in `requirements.txt`. The `-e` flag (editable) means that changes you make to the source code will be reflected immediately without needing to reinstall.

### 5. Run the Application

Now you can start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will be running at `http://127.0.0.1:8000`. The `--reload` flag will automatically restart the server whenever you make changes to the code.

### 6. (Optional) Database Initialization

The `docker-compose` setup automatically runs the `init_db.sql` script to set up necessary PostgreSQL extensions. The application's tables are created by SQLAlchemy when the application starts. If you need to manually reset the database, you can do so by stopping the containers, removing the volumes, and starting again.

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Start again
docker-compose up -d
```

## Production Deployment (Recommended)

For a production environment, it is highly recommended to run the application behind a reverse proxy like Nginx or Traefik to handle HTTPS, manage connections, and serve static files if needed.

### 1. Configure a Reverse Proxy (Nginx Example)

Here is a basic Nginx configuration example that handles HTTPS termination and proxies requests to the Uvicorn server.

```nginx
server {
    listen 80;
    server_name your-api-domain.com;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-api-domain.com;

    # SSL Certificate
    ssl_certificate /path/to/your/fullchain.pem; # e.g., from Let's Encrypt
    ssl_certificate_key /path/to/your/privkey.pem; # e.g., from Let's Encrypt

    # SSL Configuration
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Obtain an SSL Certificate

You can get a free SSL certificate from [Let's Encrypt](https://letsencrypt.org/) using tools like Certbot.

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-api-domain.com
```

### 3. Run Uvicorn without Reload

In production, you should run Uvicorn without the `--reload` flag and potentially use a process manager like Gunicorn to manage multiple Uvicorn workers for better performance and reliability.

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

This setup ensures that all data in transit between the client and your server is encrypted via HTTPS, fulfilling the security requirements outlined in the API documentation.
