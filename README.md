# AWS Data Engineer Pipeline
The original challenge was based on a real-world data engineering technical assessment from a Databricks consulting firm. It was designed to evaluate practical skills in data sourcing, cloud storage, analytics, automation, and infrastructure-as-code.

This project builds an automated AWS data engineering pipeline that ingests public data from the BLS and DataUSA APIs, stores raw files in Amazon S3, processes the datasets, and generates summary reports.

The workflow uses AWS Lambda, S3, SQS, EventBridge, and IAM to support scheduled ingestion, event-driven processing, and downstream reporting.

It also includes multiple deployment approaches using OpenTofu, AWS Cloud Formation and GitHub Actions CI/CD to show how the same pipeline can be managed with infrastructure as code and automation.

## Pipeline Stages
**Ingest → Store → Analyze → Deploy-as-Code**

1. **Ingest**  
   AWS Lambda pulls data from the BLS and DataUSA APIs.

2. **Store**  
   Amazon S3 stores raw and processed data.

3. **Analyze**  
   A processing function joins datasets, validates data, applies hashing for deduplication, and generates reports.

4. **Deploy-as-Code**  
   Infrastructure is managed using OpenTofu, Python CDK, and GitHub Actions CI/CD.
---

## 1. API Data from BLS → AWS S3

Uses the BLS API to fetch productivity and inflation data, then stores the results in Amazon S3.

- Uses a compliant User-Agent
- Uses file hash checks to skip unchanged data
- Stores JSON results in Amazon S3
- Enhanced sync version keeps S3 updated by adding, updating, and deleting files automatically
- **[View Notebook – Enhanced Sync Version](https://github.com/ScottySchmidt/AWS_DataEngineer_API/blob/main/01-ingest-api-sync.ipynb)**

## 2. API Request via AWS Lambda → S3

Automates pulling API data from BLS and dropping JSON into S3 on a monthly schedule using AWS Lambda and Amazon EventBridge.
This acts as the bridge between API ingestion and downstream data analysis.

- **[View Script](https://github.com/ScottySchmidt/data-engineer-aws/blob/main/02-api-lambda-s3.py)**

## 3. Data Processing and Analysis

Loads data from S3 into a Pandas notebook where it is cleaned, merged, and transformed before producing summary reports.

- **[Enhanced Sync Version](https://github.com/ScottySchmidt/data-engineer-aws/blob/main/03-analytics-report.ipynb)**

## 4. Infrastructure as Code IAC

Automates the AWS pipeline infrastructure using multiple deployment methods. This section shows how the pipeline can be deployed and managed with OpenTofu, Python CDK, and GitHub Actions CI/CD.

The event-driven workflow connects S3, SQS, and Lambda so new files can trigger downstream report processing.

**S3 → SQS → Lambda**

### Method A: OpenTofu

Defines and deploys AWS infrastructure using OpenTofu.

- **[View OpenTofu Files](https://github.com/ScottySchmidt/AWS_DataEngineer_API)**

### Method B: Python CDK

Deploys the AWS pipeline using Python CDK.

- **[View CDK Notebook](https://github.com/ScottySchmidt/AWS_DataEngineer_API/blob/main/04-cdk-iac-python-local.ipynb)**


## Part 5: CI/CD with GitHub Actions

Uses GitHub Actions to automate build, test, and deployment steps.

Uses GitHub Actions to automate build, test, and deployment steps.

- **Pipeline:** Git push → GitHub Actions → Build/Test → AWS
- **[View CI/CD Workflows - In Progress](https://github.com/ScottySchmidt/AWS_DataEngineer_API)**

## Deployment Proof

The screenshot below shows the deployed AWS pipeline stack.

<img width="600" height="400" alt="bls_pipeline_stack" src="https://github.com/user-attachments/assets/0540c36d-3b47-42f5-98ea-a2a08e2436ed" />

---

## AWS Tech Stack

- **Amazon S3** — stores raw and processed datasets
- **AWS Lambda** — pulls API data and runs processing logic
- **Amazon SQS** — queues S3 events for downstream report processing
- **Amazon EventBridge** — triggers scheduled Lambda runs
- **AWS IAM** — manages scoped permissions for Lambda, S3, and SQS
- **OpenTofu** — manages infrastructure as code
- **AWS CDK** — deploys AWS infrastructure using Python
- **GitHub Actions** — supports CI/CD automation
- **Amazon Athena** — runs SQL queries directly on S3 through the Glue catalog

## Security, SDKs & Data Sources

- **Secrets:** GitHub Secrets, Kaggle Secrets, AWS Secrets Manager
- **SDKs:** Python, Pandas, Boto3
- **Data Sources:** BLS API, DataUSA API
