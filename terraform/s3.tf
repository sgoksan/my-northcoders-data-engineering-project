resource "aws_s3_bucket" "ingestion_bucket" {
  bucket_prefix = var.ingestion_bucket_prefix
  force_destroy = true
  tags = {
    bucket_type = "ingestion"
    Service     = "s3"
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "processed_bucket" {
  bucket_prefix = var.processed_bucket_prefix
  force_destroy = true
  tags = {
    bucket_type = "processed"
    Service     = "s3"
    Environment = var.environment
  }
}
#======================================================================
# this will be the naming scheme for bucket definintions moving forward
# use Hyphens(-) not Underscore (_)

# Use this when testing - 09-sperrins-ingestion-test-bucket
# Proposed name for final bucket name 09-sperrins-ingestion-bucket
