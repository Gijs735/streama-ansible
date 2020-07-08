variable "instance_name" {
  description = "The name of the instance"
}

variable "size"{
  description = "The size of the vm"
}

variable "hcloud_token" {
  description = "hetzner api token"
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_ssh_key" "default" {
  name = "ssh_key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "hcloud_server" "streama" {
  depends_on = [hcloud_ssh_key.default]
  name = var.instance_name
  image = "ubuntu-18.04"
  server_type = var.size
  ssh_keys = [hcloud_ssh_key.default.id]
  user_data = "${file("${path.module}/../../cloud-init.yml")}"
}

