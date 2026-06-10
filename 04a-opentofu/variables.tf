variable "aws_region" {
  description = "AWS region where the DataQuest pipeline resources are deployed"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Existing S3 bucket used for the DataQuest project"
  type        = string
  default     = "rearc-dataquest-scott-2026"
}

variable "combined_ingest_lambda_name" {
  description = "Existing Lambda function that runs Part 1 and Part 2 ingestion"
  type        = string
  default     = "rearc-dataquest-combined-ingest"
}

variable "reporting_lambda_name" {
  description = "Lambda function created by OpenTofu to process SQS messages and run reporting logic"
  type        = string
  default     = "dataquest-reporting-lambda"
}