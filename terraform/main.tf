terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Note with the backend bucket bellow is for the centralized version.
  # When making tests or working locally you must adjust the name and make a bucket on your personal console for it to work

  backend "s3" {
    #test bucket name format should be:
    # <Your name>-sperrins-data-bucket
    bucket = "dev-sperrins-data-bucket"
    key    = "tf_state/project_sperrins.tfstate"
    region = "eu-west-2"
  }
}


provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      project_name = "team-09-amazing"
      Environment  = var.environment
    }
  }
}


