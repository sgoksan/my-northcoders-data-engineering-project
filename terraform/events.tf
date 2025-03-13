data "template_file" "SFDefinitionFile" {
  template = file("${path.module}/mystatemachine.asl.json")
  vars = {
    LambdaFunctionIngest    = aws_lambda_function.ingestion_lambda.arn,
    LambdaFunctionTransform = aws_lambda_function.transform_lambda.arn,
    LambdaFunctionLoad      = aws_lambda_function.load_lambda.arn
  }
}

resource "aws_sfn_state_machine" "pipeline_state_machine" {
  name       = var.state_machine
  role_arn   = aws_iam_role.state_machine_role.arn
  definition = data.template_file.SFDefinitionFile.rendered
  type       = "STANDARD"
  depends_on = [aws_lambda_function.ingestion_lambda]
}


resource "aws_scheduler_schedule" "step_function_eventbridge" {
  name = var.eventbridge_scheduler
  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression = "rate(5 minute)"
  target {
    arn      = aws_sfn_state_machine.pipeline_state_machine.arn
    role_arn = aws_iam_role.event_bridge_role.arn
  }
}