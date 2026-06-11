#!/usr/bin/env bash

# Exit immediately if a command fails, an unset variable is used, 
# or if a component of a pipeline fails.
set -euo pipefail

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
ADMIN_USER="airflow_admin"
ADMIN_PASS="airflow"
USER_HOME="/home/${ADMIN_USER}"

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root or with sudo." >&2
   exit 1
fi

# ---------------------------------------------------------------------
# 1. SYSTEM UPDATES & PACKAGES
# ---------------------------------------------------------------------
echo "Updating package lists and installing OpenSSH and Sudo..."
apt-get update
apt-get install -y openssh-server sudo

echo "Enabling and starting SSH service..."
systemctl enable --now ssh

# ---------------------------------------------------------------------
# 2. USER CREATION
# ---------------------------------------------------------------------
echo "Checking if user '${ADMIN_USER}' exists..."
if id "$ADMIN_USER" &>/dev/null; then
    echo "User '${ADMIN_USER}' already exists. Skipping creation."
else
    echo "Creating user '${ADMIN_USER}'..."
    useradd -m -s /bin/bash -G sudo "$ADMIN_USER"
    echo "${ADMIN_USER}:${ADMIN_PASS}" | chpasswd
fi

# ---------------------------------------------------------------------
# 3. SUDOERS CONFIGURATION
# ---------------------------------------------------------------------
echo "Configuring passwordless sudo for '${ADMIN_USER}'..."
mkdir -p /etc/sudoers.d
echo "${ADMIN_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${ADMIN_USER}"
chmod 0440 "/etc/sudoers.d/${ADMIN_USER}"

# ---------------------------------------------------------------------
# 4. SSH DIRECTORY SETUP
# ---------------------------------------------------------------------
echo "Setting up secure .ssh directory..."
mkdir -p "${USER_HOME}/.ssh"
chown "${ADMIN_USER}:${ADMIN_USER}" "${USER_HOME}/.ssh"
chmod 700 "${USER_HOME}/.ssh"

echo "Setup completed successfully!"