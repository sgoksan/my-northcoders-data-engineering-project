# creates 3 archive files for the 3 lambda functions

data "archive_file" "ingestion_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/ingestion_lambda/function.zip"
  source_dir  = "${path.module}/../src/src_ingestion"
}

data "archive_file" "transform_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/transform_lambda/function.zip"
  source_dir  = "${path.module}/../src/src_transform"
}

data "archive_file" "load_lambda" {
  type        = "zip"
  output_path = "${path.module}/../packages/load_lambda/function.zip"
  source_dir  = "${path.module}/../src/src_load"
}

# provisions the s3 bucket for the the lambda code

resource "aws_s3_bucket" "code_bucket" {
  bucket_prefix = "team-09-amazing-code-"
}


resource "aws_s3_object" "lambda_code" {
  for_each = toset([var.ingestion_lambda, var.transform_lambda, var.load_lambda])
  bucket   = aws_s3_bucket.code_bucket.bucket
  key      = "${each.key}/function.zip"
  source   = "${path.module}/../packages/${each.key}/function.zip"
  etag     = filemd5("${path.module}/../packages/${each.key}/function.zip")
}

#This creates the lambda layer zip file, the s3 object from the zip file and creates the lambda layer resource block
resource "null_resource" "pip_install" {
  triggers = {
    shell_hash = "${sha256(file("${path.module}/../layer/requirements.txt"))}"
  }
  provisioner "local-exec" {
    command = "python3 -m pip install -r ../layer/requirements.txt -t ${path.module}/../layer/python"
  }
}
data "archive_file" "layer" {
  type             = "zip"
  output_file_mode = "0666"
  source_dir       = "${path.module}/../layer"
  output_path      = "${path.module}/../packages/layers/layer.zip"
  depends_on       = [null_resource.pip_install]
}
resource "aws_s3_object" "layer_code" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "layer_code/layer.zip"
  source = data.archive_file.layer.output_path
}
resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name          = "lambda_layer"
  compatible_runtimes = [var.python_runtime]
  s3_bucket           = aws_s3_bucket.code_bucket.id
  s3_key              = aws_s3_object.layer_code.key
}


# creates the 3 lambda resources

resource "aws_lambda_function" "ingestion_lambda" {
  function_name    = var.ingestion_lambda
  source_code_hash = data.archive_file.ingestion_lambda.output_base64sha256
  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.ingestion_lambda}/function.zip"
  role             = aws_iam_role.ingestion_lambda_role.arn
  handler          = "${var.ingestion_lambda}.lambda_handler"
  runtime          = var.python_runtime
  timeout          = var.default_timeout
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  depends_on       = [aws_s3_object.lambda_code, aws_s3_object.layer_code]
  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.ingestion_bucket.id
    }
  }
}

resource "aws_lambda_function" "transform_lambda" {
  function_name    = var.transform_lambda
  source_code_hash = data.archive_file.transform_lambda.output_base64sha256
  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.transform_lambda}/function.zip"
  role             = aws_iam_role.transform_lambda_role.arn
  handler          = "${var.transform_lambda}.lambda_handler"
  runtime          = var.python_runtime
  timeout          = var.default_timeout
  layers           = [aws_lambda_layer_version.lambda_layer.arn, "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"]
  depends_on       = [aws_s3_object.lambda_code, aws_s3_object.layer_code]
  environment {
    variables = {
      S3_BUCKET_NAME_INGESTION = aws_s3_bucket.ingestion_bucket.id,
      S3_BUCKET_NAME_PROCESSED = aws_s3_bucket.processed_bucket.id
    }
  }
}

resource "aws_lambda_function" "load_lambda" {
  function_name    = var.load_lambda
  source_code_hash = data.archive_file.load_lambda.output_base64sha256
  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "${var.load_lambda}/function.zip"
  role             = aws_iam_role.load_lambda_role.arn
  handler          = "${var.load_lambda}.lambda_handler"
  runtime          = var.python_runtime
  timeout          = var.default_timeout
  layers           = [aws_lambda_layer_version.lambda_layer.arn, "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"]
  depends_on       = [aws_s3_object.lambda_code, aws_s3_object.layer_code]
  environment {
    variables = {
      S3_BUCKET_NAME_PROCESSED = aws_s3_bucket.processed_bucket.id
    }
  }
}
