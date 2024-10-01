FROM nathanhess/slurm:full-v1.1.0

# Switch to root user to install additional packages
USER root

# Install necessary packages for JupyterHub
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    curl \
    sudo \
    git \
    && pip3 install --upgrade pip 

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Add npm global binaries to the PATH
ENV PATH=$PATH:/usr/local/lib/node_modules/.bin

# Install configurable-http-proxy globally
RUN npm install -g configurable-http-proxy

# Create the admin user
RUN useradd -m admin && \
    echo "admin:$6$LCWPfNvA26GTyP5p$cPpAXROBc9eOOaGRUYTrKrj1ELd5/DQy6.QtvKbzrCgeEce1Dlw2R4IZvxSvd08WGdghKQC1AKcv82wcMiHXx/" | chpasswd && \
    echo "admin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip setuptools

# Install Python dependencies, including JupyterHub and JupyterLab
RUN pip3 install --no-cache-dir jupyterhub==5.1.0 jupyterlab python-dotenv jupyterhub-dummyauthenticator batchspawner

# Clean up to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory for JupyterHub
WORKDIR /home/admin

# Expose necessary ports (adjust as needed)
EXPOSE 8000 6817 6818 8018 8018 38024

