# Initial IAM role set up

# Trust Policies for Lambda and State Machine
# Define
data "aws_iam_policy_document" "trust_policy_lambda" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}



# Roles

# Create
# Attach
resource "aws_iam_role" "ingestion_lambda_role" {
  name_prefix        = "role-${var.ingestion_lambda}"
  assume_role_policy = data.aws_iam_policy_document.trust_policy_lambda.json
}

resource "aws_iam_role" "transform_lambda_role" {
  name_prefix        = "role-${var.transform_lambda}"
  assume_role_policy = data.aws_iam_policy_document.trust_policy_lambda.json
}

resource "aws_iam_role" "load_lambda_role" {
  name_prefix        = "role-${var.load_lambda}"
  assume_role_policy = data.aws_iam_policy_document.trust_policy_lambda.json
}



# Please define the Data blocks for policy documents and 
# Create two Resource blocks:
# One for creating the "aws_iam_policy" (uses the data block above) and 
# One for attaching the "aws_iam_role_policy_attachment" to the roles created above



/*
# ------------------------------
# Lambda IAM Policy for S3-ingestion
# ------------------------------
*/

# Ingestion Lambda permissions

# policy document for s3 bucket
data "aws_iam_policy_document" "ingestion_s3_policy" {
  statement {
    sid = "1"

    actions = ["s3:PutObject",
      "s3:Get*",
      "s3:List*",
      "s3:Describe*",
      "s3-object-lambda:Get*",
    "s3-object-lambda:List*"]
    resources = ["${aws_s3_bucket.ingestion_bucket.arn}",
    "${aws_s3_bucket.ingestion_bucket.arn}/*"]
  }
}


# policy for s3 ingestion bucket
resource "aws_iam_policy" "s3_policy" {
  name_prefix = "s3-policy-${var.ingestion_lambda}-write"

  policy = data.aws_iam_policy_document.ingestion_s3_policy.json

}

# policy attachment to the role "iam_role_for_lambda"
resource "aws_iam_policy_attachment" "lambda_s3_policy_attachment" {
  name       = "lambda-s3-policy-attachment"
  roles      = [aws_iam_role.ingestion_lambda_role.name]
  policy_arn = aws_iam_policy.s3_policy.arn
}

# Transform Lambda permissions

# policy document for s3 bucket
data "aws_iam_policy_document" "transform_s3_policy" {
  statement {
    sid = "1"

    actions = ["s3:PutObject",
      "s3:Get*",
      "s3:List*",
      "s3:Describe*",
      "s3-object-lambda:Get*",
    "s3-object-lambda:List*"]
    resources = ["${aws_s3_bucket.ingestion_bucket.arn}",
      "${aws_s3_bucket.ingestion_bucket.arn}/*",
      "${aws_s3_bucket.processed_bucket.arn}",
    "${aws_s3_bucket.processed_bucket.arn}/*"]
  }
}


# policy for s3 processed bucket
resource "aws_iam_policy" "transform_s3_policy" {
  name_prefix = "s3-policy-${var.transform_lambda}-write"

  policy = data.aws_iam_policy_document.transform_s3_policy.json

}

# policy attachment to the role "iam_role_for_lambda"
resource "aws_iam_policy_attachment" "lambda_transform_s3_policy_attachment" {
  name       = "lambda-s3-policy-attachment"
  roles      = [aws_iam_role.transform_lambda_role.name]
  policy_arn = aws_iam_policy.transform_s3_policy.arn
}

# Load Lambda permissions

# policy document for s3 bucket
data "aws_iam_policy_document" "load_s3_policy" {
  statement {
    sid = "1"

    actions = ["s3:PutObject",
      "s3:Get*",
      "s3:List*",
      "s3:Describe*",
      "s3-object-lambda:Get*",
    "s3-object-lambda:List*"]
    resources = [
      "${aws_s3_bucket.processed_bucket.arn}",
    "${aws_s3_bucket.processed_bucket.arn}/*"]
  }
}


# policy for s3 processed bucket
resource "aws_iam_policy" "load_s3_policy" {
  name_prefix = "s3-policy-${var.load_lambda}-write"

  policy = data.aws_iam_policy_document.load_s3_policy.json

}

# policy attachment to the role "iam_role_for_lambda"
resource "aws_iam_policy_attachment" "lambda_load_s3_policy_attachment" {
  name       = "lambda-s3-policy-attachment"
  roles      = [aws_iam_role.load_lambda_role.name]
  policy_arn = aws_iam_policy.load_s3_policy.arn
}


/*
# ------------------------------
# Lambda IAM Policy for CloudWatch
# ------------------------------
*/


#Policy document for cloudwatch - ingestion
data "aws_iam_policy_document" "cw_document_ingestion" {
  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup"
    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutRetentionPolicy",
      "logs:GetLogEvents",
      "logs:PutLogEvents",

    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.ingestion_lambda}:*"]
  }
}

# Create policy with policy document defined above
resource "aws_iam_policy" "cloudwatch_policy_ingestion" {

  name_prefix = "cloudwatch-policy-${var.ingestion_lambda}-logging"
  policy      = data.aws_iam_policy_document.cw_document_ingestion.json
}

# Attach the cw policy to the lambda role
resource "aws_iam_role_policy_attachment" "ingestion_lambda_cw_policy_attachment" {

  policy_arn = aws_iam_policy.cloudwatch_policy_ingestion.arn
  role       = aws_iam_role.ingestion_lambda_role.name
}

#Policy document for cloudwatch - transform
data "aws_iam_policy_document" "cw_document_transform" {
  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup"
    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutRetentionPolicy",
      "logs:GetLogEvents",
      "logs:PutLogEvents",

    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.transform_lambda}:*"]
  }
}

# Create policy with policy document defined above
resource "aws_iam_policy" "cloudwatch_policy_transform" {

  name_prefix = "cloudwatch-policy-${var.transform_lambda}-logging"
  policy      = data.aws_iam_policy_document.cw_document_transform.json
}

# Attach the cw policy to the lambda role
resource "aws_iam_role_policy_attachment" "transform_lambda_cw_policy_attachment" {

  policy_arn = aws_iam_policy.cloudwatch_policy_transform.arn
  role       = aws_iam_role.transform_lambda_role.name
}

#Policy document for cloudwatch - load
data "aws_iam_policy_document" "cw_document_load" {
  statement {

    effect = "Allow"

    actions = [
      "logs:CreateLogGroup"
    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutRetentionPolicy",
      "logs:GetLogEvents",
      "logs:PutLogEvents",

    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.load_lambda}:*"]
  }
}

# Create policy with policy document defined above
resource "aws_iam_policy" "cloudwatch_policy_load" {

  name_prefix = "cloudwatch-policy-${var.load_lambda}-logging"
  policy      = data.aws_iam_policy_document.cw_document_load.json
}

# Attach the cw policy to the lambda role
resource "aws_iam_role_policy_attachment" "load_lambda_cw_policy_attachment" {

  policy_arn = aws_iam_policy.cloudwatch_policy_load.arn
  role       = aws_iam_role.load_lambda_role.name
}


/*
# ------------------------------
# Lambda IAM Policy for Secret Manager
# ------------------------------
*/

#lambda policy document for secret manager
data "aws_iam_policy_document" "lambda_secret_manager" {
  statement {
    sid    = "BasePermissions"
    effect = "Allow"
    actions = [
      "secretsmanager:*",
      "lambda:ListFunctions",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "LambdaPermissions"
    effect = "Allow"
    actions = [
      "lambda:AddPermission",
      "lambda:CreateFunction",
      "lambda:GetFunction",
      "lambda:InvokeFunction",
      "lambda:UpdateFunctionConfiguration"
    ]
    resources = ["arn:aws:lambda:*:*:function:SecretsManager*"]
  }
}


# policy for secret manager
resource "aws_iam_policy" "secret_manager_policy" {
  name_prefix = "secret_manager-policy-${var.ingestion_lambda}"

  policy = data.aws_iam_policy_document.lambda_secret_manager.json

}

# policy attachment to the role "iam_role_for_lambda"
resource "aws_iam_policy_attachment" "lambda_secret_manager_policy_attachment" {
  name       = "lambda-secret-manager-attachment"
  roles      = [aws_iam_role.ingestion_lambda_role.name, aws_iam_role.load_lambda_role.name]
  policy_arn = aws_iam_policy.secret_manager_policy.arn
}

/*
# -----------------------------------
# Lambda IAM Policy for StateMachine 
# -----------------------------------
*/

data "aws_iam_policy_document" "trust_policy_state_machine" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "state_machine_role" {
  name_prefix        = "general-state-machine-role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy_state_machine.json
}

data "aws_iam_policy_document" "state_machine_role_policy" {

  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.ingestion_lambda}:*",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.transform_lambda}:*",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.load_lambda}:*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.ingestion_lambda}",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.transform_lambda}",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.load_lambda}"
    ]
  }

}
resource "aws_iam_role_policy" "StateMachinePolicy" {
  role   = aws_iam_role.state_machine_role.id
  policy = data.aws_iam_policy_document.state_machine_role_policy.json
}

/*
# ----------------------------------
# Lambda IAM Policy for EventBridge
# ----------------------------------
*/

data "aws_iam_policy_document" "trust_policy_event_bridge" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["states.amazonaws.com",
      "scheduler.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}

resource "aws_iam_role" "event_bridge_role" {
  name_prefix        = "general-event-bridge-role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy_event_bridge.json
}

data "aws_iam_policy_document" "eventbridge_document_execution" {
  statement {
    actions = ["states:StartExecution"]
    effect  = "Allow"
    resources = [
      "arn:aws:states:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stateMachine:${var.state_machine}"
    ]
  }
}

resource "aws_iam_policy" "eventbridge_policy_state_machine_execution" {
  name_prefix = "state-machine-execution-eventbridge-"
  policy      = data.aws_iam_policy_document.eventbridge_document_execution.json
}


resource "aws_iam_role_policy_attachment" "eventbridge_policy_attachment" {
  role       = aws_iam_role.event_bridge_role.name
  policy_arn = aws_iam_policy.eventbridge_policy_state_machine_execution.arn
}



/*
# ------------------------------
# LOAD Lambda IAM Policy for Secret Manager
# ------------------------------
*/

#load lambda policy document for secret manager
data "aws_iam_policy_document" "load_lambda_secret_manager" {
  statement {
    sid    = "BasePermissions"
    effect = "Allow"
    actions = [
      "secretsmanager:*",
      "lambda:List*",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "LambdaPermissions"
    effect = "Allow"
    actions = [
      "lambda:AddPermission",
      "lambda:CreateFunction",
      "lambda:GetFunction",
      "lambda:InvokeFunction",
      "lambda:UpdateFunctionConfiguration"
    ]
    resources = ["arn:aws:lambda:*:*:function:SecretsManager*"]
  }
}


# policy for secret manager
resource "aws_iam_policy" "load_lambda_secret_manager_policy" {
  name_prefix = "secret_manager-policy-${var.load_lambda}"

  policy = data.aws_iam_policy_document.load_lambda_secret_manager.json

}

# policy attachment to the role "iam_role_for_lambda"
resource "aws_iam_policy_attachment" "load_lambda_secret_manager_policy_attachment" {
  name       = "load-lambda-secret-manager-attachment"
  roles      = [aws_iam_role.load_lambda_role.name]
  policy_arn = aws_iam_policy.load_lambda_secret_manager_policy.arn
}