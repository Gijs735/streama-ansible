variable "cfapikey"{
  description = "The size of the vm"
}

variable "cfemail"{
  description = "The size of the vm"
}

variable "cfaccid"{
  description = "The size of the vm"
}


variable "domain"{
  description = "The size of the vm"
}

variable "cfzoneid"{
  description = "zoneid cf"
}

provider "cloudflare" {
  email      = var.cfemail
  api_key    = var.cfapikey
  account_id = var.cfaccid
}

resource "cloudflare_record" "domain" {
  depends_on = [hcloud_server.streama]
  zone_id = var.cfzoneid
  name    = var.domain
  value   = hcloud_server.streama.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = true
}

resource "cloudflare_record" "wwwdomain" {
  depends_on = [hcloud_server.streama]
  zone_id = var.cfzoneid
  name    = "www.${var.domain}"
  value   = hcloud_server.streama.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = true
}