Docker image to run Python Selenium with Chromium on Raspberry Pi

# Usage
1. Install Docker on Raspberry Pi
1. Clone this repo
1. Build the docker image locally by running: `sh build.sh`
1. Test the image by running the command:
```
docker run --rm -w /usr/workspace -v $(pwd):/usr/workspace aedocker python ae.py
```
