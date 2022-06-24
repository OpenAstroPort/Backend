# backend
This application is mapping the Meade Firmware Commands used by the OpenAstroTracker-Desktop Application to a REST API so it is possible to build a WebFrontend that has the same functionality.
## Installation
On Raspberry Pi [Astroberry](https://www.astroberry.io):
1. **Install Docker**:
``` bash
# First update the system
sudo apt update && sudo apt upgrade
# Install Docker and Docker-Compose 
sudo apt install docker docker-compose
# Run Docker on System Startup
sudo systemctl enable docker
# Reboot to make changes effective
sudo reboot
```
2. **Clone the Repo**:
``` bash
git clone https://github.com/OpenAstroPort/backend
cd backend
```
3. **Build and Run the Backend Application**:
``` bash
docker-compose build
docker-compose up -d
```

#### Done ... You have installed the OpenAtroPort backend

## Updating the Application
``` bash
# get upstream
git pull
# stop the application
docker-compose down
# rebuild the Docker Image
docker-compose build
# start the container again
docker-compose up -d
# cleanup old images and containers
docker system prune
```
