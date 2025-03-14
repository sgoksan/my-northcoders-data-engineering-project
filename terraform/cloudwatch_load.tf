#==================================================================================================================================================================
#Alarm for errors


resource "aws_cloudwatch_log_metric_filter" "load_error_metric_filter" {
  name           = "Errors_for_load_lambda"
  pattern        = "ERROR"
  log_group_name = "/aws/lambda/${var.load_lambda}"

  metric_transformation {
    name      = "load_lambda_errors"
    namespace = "load_lambda"
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "load_lambda_error_alarm" {
  alarm_name          = "Load-lambda-error"
  alarm_description   = "Triggers when load lambda fails due to error."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.load_error_metric_filter.metric_transformation[0].name
  namespace           = "load_lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.team_sperrins_topic.arn]
}

#==================================================================================================================================================================
#Alarm for critical errors
resource "aws_cloudwatch_log_metric_filter" "load_critical_metric_filter" {
  name           = "Critical_errors_for_load_lambda"
  pattern        = "CRITICAL"
  log_group_name = "/aws/lambda/${var.load_lambda}"

  metric_transformation {
    name      = "load_lambda_critical"
    namespace = "load_lambda"
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "load_lambda_critical_alarm" {
  alarm_name          = "Load-lambda-critical"
  alarm_description   = "Triggers when load lambda fails due to critical error."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.load_critical_metric_filter.metric_transformation[0].name
  namespace           = "load_lambda"
  period              = 10
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.team_sperrins_topic.arn]
}