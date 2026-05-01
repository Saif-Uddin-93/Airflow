############################################################################
# AIRFLOW CONTAINER (MANAGED NODE - ALPINE)

# Bring up the interface and manually configure the network
ip link set dev eth0 up
ip addr add 192.168.1.29/24 dev eth0
ip route add default via 192.168.1.1
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Install required packages (shadow is added to ensure chpasswd works)
apk update && apk add openssh python3 sudo bash shadow

# Generate SSH host keys (Required in Alpine before starting the daemon)
ssh-keygen -A

# Start the SSH daemon (systemctl does not exist in standard Alpine containers)
/usr/sbin/sshd

# Create the user (-D creates the user without assigning a password prompt)
adduser -D -s /bin/bash airflow_admin
echo "airflow_admin:airflow" | chpasswd

# Configure passwordless sudo for the user
mkdir -p /etc/sudoers.d/
echo "airflow_admin ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/airflow_admin
chmod 0440 /etc/sudoers.d/airflow_admin

# Setup SSH directory
mkdir -p /home/airflow_admin/.ssh
chown airflow_admin:airflow_admin /home/airflow_admin/.ssh
chmod 700 /home/airflow_admin/.ssh


############################################################################
# ANSIBLE CONTAINER (CONTROLLER NODE)

ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
ssh-copy-id airflow_admin@<ip_address_of_managed_node>

# test ssh connection 
# ssh airflow_admin@<ip_address_of_managed_node>

# Run this on the Controller if the IP was used previously and the host key changed
ssh-keygen -f "/root/.ssh/known_hosts" -R "<ip_address_of_managed_node>"
ssh-copy-id airflow_admin@<ip_address_of_managed_node>