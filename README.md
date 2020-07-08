# streama-ansible
This repo will install streama with ansible and/or cloud-init.

Included is:
- Streama
- MariaDB
- nginx reverse proxy with a letsencrypt SSL certificate (can be configured)

Things to do before using:
- Make sure the the latest streama version is packed. Currenly **version 1.9.1** is packed. You can pack you own version by reading the readme here: https://github.com/Gijs735/streama-ansible/tree/master/files
- Make sure vars.yml is correct for your use-case, especially the domains part.
- cloud-init.yml pulls from this git repo, if you don't want this change the url.
- put a database password into cloud init instead of the default 'PASSWORD'.
- Delete secret.yml, then run:
    ansible-vault create --vault-id db@prompt secret.yml
- put in the following data:
    db_user_pass: PASSWORD
    db_root_pass: PASSWORD

After this is done run:
    ansible-galaxy install -r requirements.yml
    ansible-playbook --vault-id db@prompt main.yml