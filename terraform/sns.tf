# Create an SNS topic
resource "aws_sns_topic" "team_sperrins_topic" {
  name = var.lambda_failure_topic_name
}


#havent figured out names
resource "aws_sns_topic_subscription" "team_sperrins_topic" {
  topic_arn = aws_sns_topic.team_sperrins_topic.arn
  protocol  = "email"
  endpoint  = var.email_address
}