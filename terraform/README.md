# Howto: Streama Terraform for Hetzner Cloud

- Fill in all the fields in *instances.tf*.
- Do all the things in the main [readme.md](../README.md).
- Change the backend fields in *instances.tf* to where you want to store the terraform state (I use Azure).
- If you don't want to use cloudflare (why? :cry:) delete the file in the hetzner folder and remove all cloudflare variables.
- Run `terraform init && terraform apply`. 
- This will deploy an instance on Hetzner with cloud-init + Cloudflare DNS records.
