# streama-
apt update
apt install git
apt install ansible
git clone https://github.com/Gijs735/streama-ansible.git

password

ansible-galaxy install -r requirements.yml
ansible-playbook --vault-id db@password main.yml