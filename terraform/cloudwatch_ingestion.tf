#==================================================================================================================================================================
#Alarm for errors


resource "aws_cloudwatch_log_metric_filter" "ingestion_error_metric_filter" {
  name           = "Errors_for_ingestion_lambda"
  pattern        = "ERROR"
  log_group_name = "/aws/lambda/${var.ingestion_lambda}"

  metric_transformation {
    name      = "ingestion_lambda_errors"
    namespace = "ingestion_lambda"
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "ingestion_lambda_error_alarm" {
  alarm_name          = "Ingestion-lambda-error"
  alarm_description   = "Triggers when ingestion lambda fails due to error."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.ingestion_error_metric_filter.metric_transformation[0].name
  namespace           = "ingestion_lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.team_sperrins_topic.arn]
}

#==================================================================================================================================================================
#Alarm for critical errors
resource "aws_cloudwatch_log_metric_filter" "ingestion_critical_metric_filter" {
  name           = "Critical_errors_for_ingestion_lambda"
  pattern        = "CRITICAL"
  log_group_name = "/aws/lambda/${var.ingestion_lambda}"

  metric_transformation {
    name      = "ingestion_lambda_critical"
    namespace = "ingestion_lambda"
    value     = "1"
  }
}


resource "aws_cloudwatch_metric_alarm" "ingestion_lambda_critical_alarm" {
  alarm_name          = "Ingestion-lambda-critical"
  alarm_description   = "Triggers when ingestion lambda fails due to critical error."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.ingestion_critical_metric_filter.metric_transformation[0].name
  namespace           = "ingestion_lambda"
  period              = 10
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.team_sperrins_topic.arn]
}