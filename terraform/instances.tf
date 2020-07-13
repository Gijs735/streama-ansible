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
    domain = "fireflix.stream"
    #hetzner api key
    hcloud_token = "xKNdU3vMKlC1Kwda0qcwGOuseXFI20tNPFqbraaPwftNjusAvShXGhSprZRslVnL"
    #cloudflare global token
    cfapikey = "0ce62d256c763aaa9b4b71b83e23caebf3616"
    #cloudflare zone id
    cfzoneid = "c1c89878b83f977facc237e474abae1b"
    #cloudflare e-mail
    cfemail = "gijs15_9@hotmail.com"
    #cloudflare account id
    cfaccid = "43a65a3768f2569190b5ad4b041b34a4"
 }