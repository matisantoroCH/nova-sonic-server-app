terraform {
  backend "s3" {
    bucket         = "nova-sonic-terraform-state"
    key            = "demo/terraform.tfstate"
    region         = "us-east-1"
    use_lockfile   = true
    encrypt        = true
  }
} 