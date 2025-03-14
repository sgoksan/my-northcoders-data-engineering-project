#==================================================================================================================================================================
#Alarm for errors


resource "aws_cloudwatch_log_metric_filter" "transform_error_metric_filter" {
  name           = "Errors_for_transform_lambda"
  pattern        = "ERROR"
  log_group_name = "/aws/lambda/${var.transform_lambda}"

  metric_transformation {
    name      = "transform_lambda_errors"
    namespace = "transform_lambda"
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "transform_lambda_error_alarm" {
  alarm_name          = "Transform-lambda-error"
  alarm_description   = "Triggers when transform lambda fails due to error."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.transform_error_metric_filter.metric_transformation[0].name
  namespace           = "transform_lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.team_sperrins_topic.arn]
}

#==================================================================================================================================================================
#Alarm for critical errors
resource "aws_cloudwatch_log_metric_filter" "transform_critical_metric_filter" {
  name           = "Critical_errors_for_transform_lambda"
  pattern        = "CRITICAL"
  log_group_name = "/aws/lambda/${var.transform_lambda}"

  metric_transformation {
    name      = "transform_lambda_critical"
    namespace = "transform_lambda"
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "transform_lambda_critical_alarm" {
  alarm_name          = "transform-lambda-critical"
  alarm_description   = "Triggers when transform lambda fails due to critical error."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.transform_critical_metric_filter.metric_transformation[0].name
  namespace           = "transform_lambda"
  period              = 10
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.team_sperrins_topic.arn]
}