terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Get current AWS account information
data "aws_caller_identity" "current" {}

# Existing S3 bucket for the project
data "aws_s3_bucket" "data_bucket" {
  bucket = var.bucket_name
}

# Existing Lambda that runs Part 1 and Part 2
data "aws_lambda_function" "combined_ingest" {
  function_name = var.combined_ingest_lambda_name
}

# Package the reporting Lambda code from the main lambda folder
data "archive_file" "reporting_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/reporting.py"
  output_path = "${path.module}/reporting_lambda.zip"
}

# SQS queue populated when DataUSA JSON is written to S3
resource "aws_sqs_queue" "datausa_json_queue" {
  name                       = "dataquest-datausa-json-queue"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 345600
}

# Allow S3 to send messages to the SQS queue
resource "aws_sqs_queue_policy" "allow_s3_to_send_messages" {
  queue_url = aws_sqs_queue.datausa_json_queue.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "AllowS3ToSendMessages"
        Effect = "Allow"

        Principal = {
          Service = "s3.amazonaws.com"
        }

        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.datausa_json_queue.arn

        Condition = {
          ArnEquals = {
            "aws:SourceArn" = data.aws_s3_bucket.data_bucket.arn
          }
        }
      }
    ]
  })
}

# S3 notification sends raw/datausa/*.json object-created events to SQS
resource "aws_s3_bucket_notification" "datausa_json_notification" {
  bucket = data.aws_s3_bucket.data_bucket.id

  queue {
    queue_arn     = aws_sqs_queue.datausa_json_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "raw/datausa/"
    filter_suffix = ".json"
  }

  depends_on = [
    aws_sqs_queue_policy.allow_s3_to_send_messages
  ]
}

# EventBridge daily schedule for the existing combined ingest Lambda
resource "aws_cloudwatch_event_rule" "daily_ingest_rule" {
  name                = "dataquest-daily-ingest-opentofu"
  description         = "Runs the DataQuest combined ingest Lambda daily"
  schedule_expression = "rate(1 day)"
  state               = "ENABLED"
}

# Connect the EventBridge rule to the combined ingest Lambda
resource "aws_cloudwatch_event_target" "daily_ingest_target" {
  rule      = aws_cloudwatch_event_rule.daily_ingest_rule.name
  target_id = "CombinedIngestLambda"
  arn       = data.aws_lambda_function.combined_ingest.arn
}

# Allow EventBridge to invoke the combined ingest Lambda
resource "aws_lambda_permission" "allow_eventbridge_to_invoke_combined_ingest" {
  statement_id  = "AllowEventBridgeInvokeCombinedIngestOpenTofu"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.combined_ingest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_ingest_rule.arn
}

# IAM role for the reporting Lambda
resource "aws_iam_role" "reporting_lambda_role" {
  name = "dataquest-reporting-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Allow reporting Lambda to write CloudWatch logs
resource "aws_iam_role_policy_attachment" "reporting_lambda_basic_execution" {
  role       = aws_iam_role.reporting_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Allow reporting Lambda to process SQS messages and read/write S3
resource "aws_iam_role_policy" "reporting_lambda_policy" {
  name = "dataquest-reporting-lambda-policy"
  role = aws_iam_role.reporting_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "AllowSQSProcessing"
        Effect = "Allow"

        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]

        Resource = aws_sqs_queue.datausa_json_queue.arn
      },
      {
        Sid    = "AllowS3ReadWrite"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]

        Resource = [
          data.aws_s3_bucket.data_bucket.arn,
          "${data.aws_s3_bucket.data_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Reporting Lambda triggered by SQS
resource "aws_lambda_function" "reporting_lambda" {
  function_name    = var.reporting_lambda_name
  role             = aws_iam_role.reporting_lambda_role.arn
  handler          = "reporting.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.reporting_lambda_zip.output_path
  source_code_hash = data.archive_file.reporting_lambda_zip.output_base64sha256
  timeout          = 60

  environment {
    variables = {
      BUCKET_NAME      = var.bucket_name
      PROCESSED_PREFIX = "processed/reports/"
    }
  }
}

# Connect SQS queue to reporting Lambda
resource "aws_lambda_event_source_mapping" "sqs_to_reporting_lambda" {
  event_source_arn = aws_sqs_queue.datausa_json_queue.arn
  function_name    = aws_lambda_function.reporting_lambda.arn
  batch_size       = 1
  enabled          = true
}