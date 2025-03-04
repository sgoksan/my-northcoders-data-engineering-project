data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

variable "ingestion_bucket_prefix" {
  description = "Value of the Name tag for the ingestion_bucket_prefix"
  type        = string
  default     = "ingestion-zone"

}

variable "Environment" {
  description = "The enviroment tag for AWS resources"
  type        = string
  default     = "dev"
}

variable "ingestion_lambda" {
  type    = string
  default = "ingestion_lambda"
}

variable "transform_lambda" {
  type    = string
  default = "transform_lambda"
}

variable "load_lambda" {
  type    = string
  default = "load_lambda"
}

variable "state_machine" {
  type    = string
  default = "pipeline_state_machine"
}

variable "eventbridge_scheduler" {
  type    = string
  default = "eventbridge_scheduler"
}

variable "python_runtime" {
  type    = string
  default = "python3.12"
}

variable "default_timeout" {
  type    = number
  default = 20
}

variable "processed_bucket_prefix" {
  description = "Value of the Name tag for the processed_bucket_prefix"
  type        = string
  default     = "processed-zone"

}