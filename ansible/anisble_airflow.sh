# AIRFLOW CONTAINER (MANAGED NODE)
apt update && apt install -y openssh-server python3 sudo
systemctl enable --now ssh

useradd -m -s /bin/bash ansible_admin -G sudo
echo "ansible_admin:<PASSWORD>" | chpasswd

mkdir -p /etc/sudoers.d/
echo "ansible_admin ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ansible
chmod 0440 /etc/sudoers.d/ansible

mkdir -p /home/ansible_admin/.ssh
chown ansible_admin:ansible_admin /home/ansible_admin/.ssh
chmod 700 /home/ansible_admin/.ssh

# ANSIBLE CONTAINER (CONTROLLER NODE)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
ssh-copy-id ansible_admin@<ip_address_of_managed_node>
ssh ansible_admin@<ip_address_of_managed_node>

# Run this on the Controller if the IP was used previously
ssh-keygen -f "/root/.ssh/known_hosts" -R "<ip_address_of_managed_node>"
ssh-copy-id ansible_admin@<ip_address_of_managed_node>