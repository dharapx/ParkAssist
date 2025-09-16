# Add Docker's official GPG key:
```
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
```

# Install the Docker packages.
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl status docker

#Some systems may have this behavior disabled and will require a manual start:
sudo systemctl start docker
```

# Install Docker-Compose
```
sudo apt  install docker-compose
```

# install ifconfig (Optional)
```
sudo apt install net-tools
```

# Add your user to the docker group so you don’t need to use sudo:
```
sudo usermod -aG docker $USER
newgrp docker
```

# Create Docker File for FastAPI app
```
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir "uvicorn[standard]" "fastapi" && pip install --no-cache-dir .

# Copy the app code
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```

# Create docker-compose.yml to deploy the App
```
version: "3.8"

services:
  fastapi_app:
    build: .
    container_name: fastapi_app
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```
# Running Docker Compose
```
docker-compose up -d --build
docker ps
```


# Install NGINX-PROXY-MANAGER
```
mkdir -p ~/nginx-proxy-manager/data
mkdir -p ~/nginx-proxy-manager/letsencrypt
cd ~/nginx-proxy-manager
```
### Create docker-compose.yml
```
version: "3"

services:
  npm:
    image: jc21/nginx-proxy-manager:latest
    container_name: nginx-proxy-manager
    restart: unless-stopped
    ports:
      - "80:80"       # HTTP
      - "443:443"     # HTTPS
      - "81:81"       # Admin UI
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```
# Running Docker Compose to deploy NGINX-PROXY-MANAGER
```
docker-compose up -d --build
docker ps
```
# Nesscery Steps:
```
Default login:

Email: admin@example.com

Password: changeme

👉 Make sure to change the admin password immediately after logging in.
```

# CRITICAL
## Check firewall
```
sudo ufw status
```
if Status: inactive then

# First, enable UFW (if not already enabled)
```
sudo ufw enable
```
# Then allow OpenSSH permanently
```
sudo ufw allow OpenSSH
```
# Also allow HTTP & HTTPS (if not already):
```
sudo ufw allow 80/tcp
sudo ufw allow 81/tcp
sudo ufw allow 443/tcp
```

# Reload UFW to apply any pending changes (if needed):
```
sudo ufw reload
```
# To remove port 8000 from UFW rules permanently, run:
```
sudo ufw delete allow 8000/tcp
```
# Check Status
```
sudo ufw status
```

## Expected Output
```
To                         Action      From
--                         ------      ----
80/tcp                     ALLOW       Anywhere
81                         ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
OpenSSH                    ALLOW       Anywhere
80/tcp (v6)                ALLOW       Anywhere (v6)
81 (v6)                    ALLOW       Anywhere (v6)
443/tcp (v6)               ALLOW       Anywhere (v6)
OpenSSH (v6)               ALLOW       Anywhere (v6)
```

