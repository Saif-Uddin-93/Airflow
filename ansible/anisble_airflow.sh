# AIRFLOW CONTAINER (MANAGED NODE)
apt update && apt install -y openssh-server python3 sudo
systemctl enable --now ssh

useradd -m -s /bin/bash airflow_admin -G sudo
echo "airflow_admin:airflow" | chpasswd

mkdir -p /etc/sudoers.d/
echo "airflow_admin ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/airflow_admin
chmod 0440 /etc/sudoers.d/airflow_admin

mkdir -p /home/airflow_admin/.ssh
chown airflow_admin:airflow_admin /home/airflow_admin/.ssh
chmod 700 /home/airflow_admin/.ssh

# ANSIBLE CONTAINER (CONTROLLER NODE)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
ssh-copy-id airflow_admin@<ip_address_of_managed_node>
# test ssh connection 
# ssh airflow_admin@<ip_address_of_managed_node>

# Run this on the Controller if the IP was used previously
ssh-keygen -f "/root/.ssh/known_hosts" -R "<ip_address_of_managed_node>"
ssh-copy-id airflow_admin@<ip_address_of_managed_node>