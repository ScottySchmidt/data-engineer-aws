output "sqs_queue_name" {
  description = "Name of the SQS queue that receives DataUSA JSON S3 events"
  value       = aws_sqs_queue.datausa_json_queue.name
}

output "sqs_queue_url" {
  description = "URL of the SQS queue"
  value       = aws_sqs_queue.datausa_json_queue.url
}

output "daily_eventbridge_rule_name" {
  description = "Name of the daily EventBridge rule"
  value       = aws_cloudwatch_event_rule.daily_ingest_rule.name
}

output "reporting_lambda_name" {
  description = "Name of the reporting Lambda created by OpenTofu"
  value       = aws_lambda_function.reporting_lambda.function_name
}

output "processed_reports_prefix" {
  description = "S3 prefix where processed reports are written"
  value       = "s3://${var.bucket_name}/processed/reports/"
}