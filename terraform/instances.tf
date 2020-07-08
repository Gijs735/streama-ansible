# Where to store the terraform state
terraform {
  backend "azurerm" {
    storage_account_name = "terraformstatic2"
    container_name       = "terstatic"
    key                  = "hetznerstreama.terraform.tfstate"
  }
}

## Create new instances here ##
  module "streama" {
    source = "./hetzner"
    #name of the VM on hetzner
    instance_name = "streama1"
    #hetzner VM size
    size = "cx11"
    #the domain for streama !!!EDIT HERE AND IN VARS.YML!!!
    domain = "streama.finestbit.com"
    #hetzner api key
    hcloud_token = ""
    #cloudflare global token
    cfapikey = ""
    #cloudflare zone id
    cfzoneid = ""
    #cloudflare e-mail
    cfemail = ""
    #cloudflare account id
    cfaccid = ""
 }