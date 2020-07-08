# streama-ansible
This repo will install streama using ansible and/or cloud-init.

#### Included is:
* Streama
* MariaDB
* nginx reverse proxy with a letsencrypt SSL certificate (can be configured)

#### Things to do before using:
* Make sure the the latest streama version is packed. Currenly **version 1.9.1** is packed. You can pack you own version by reading the readme [here](files).
* Make sure *vars.yml* is correct for your use-case, especially the domains part.
* Delete secret.yml, then run:
    ```
    ansible-vault create --vault-id db@prompt secret.yml
    ```
    * put in the following data:
        ```
        db_user_pass: `PASSWORD`
        db_root_pass: `PASSWORD`
        ```
* If using you're letsencrypt, make sure your DNS is correctly configured .
* If you're using cloud init be aware of the following:
    * *Cloud-init.yml* pulls from this git repo, if you don't want this change the url inside. This is highly recommended because you don't know the password for secret.yml and this will probably make your installation fail.
    * Put a database password in *cloud-init.yml*, instead of the default.
#### After this is done run:
    
    ansible-galaxy install -r requirements.yml
    ansible-playbook --vault-id db@prompt main.yml
    
