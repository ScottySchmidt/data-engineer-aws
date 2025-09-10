# AWS Data Engineering Pipeline Project
This independent study focuses on designing and deploying a scalable, event-driven data pipeline using Amazon Web Services (AWS). The project follows a four-part architecture that includes ingesting data from public APIs, storing and processing that data in the cloud, and deploying the entire infrastructure using the AWS Cloud Development Kit (CDK) in Python. The pipeline is designed to reflect real-world best practices in cloud-based data engineering, with an emphasis on automation, scalability, and maintainability.

The project will result in a fully functional pipeline that automates API data ingestion, triggers processing events, and delivers analytics outputs — all orchestrated through AWS-native services and deployed as code.

## Numbered Deliverables

1. **Video Demonstration**  
   A recorded demo showing the pipeline in action, including data ingestion, processing, and deployment using AWS CDK.

2. **User Documentation & Manual**  
   A written guide detailing how to use, deploy, and maintain the pipeline, intended for developers or technical stakeholders.

3. **Jupyter Notebook – API Ingestion (Local Sync Version)**  
   Python notebook for manually syncing public API data to Amazon S3 with hash checking to avoid duplicates.

4. **AWS Lambda Script – API to S3**  
   A serverless function that fetches data from public APIs and stores it in S3 on a recurring schedule using EventBridge.

5. **Jupyter Notebook – Data Processing & Reporting**  
   Notebook that reads raw data from S3, processes it using Pandas, and generates cleaned and summarized reports.

6. **Infrastructure as Code (AWS CDK)**  
   CDK codebase for deploying S3, Lambda, SQS, and EventBridge resources as reproducible infrastructure.

7. **CI/CD Workflow (GitHub Actions)**  
   A version-controlled CI/CD workflow (in progress) for deploying the pipeline automatically from GitHub.

---

## Technical Overview

### Pipeline Architecture

- **Ingest:** Lambda function fetches data from public APIs and stores it in Amazon S3.
- **Store:** S3 buckets hold raw and processed data, organized by ingestion type.
- **Analyze:** A second Lambda function listens for S3 events, processes the data, and writes summaries.
- **Deploy:** AWS CDK scripts in Python automate the deployment of all infrastructure resources.

### Deployment Options

- **Local Jupyter Notebook (Python CDK)**
- **AWS CloudShell (Python CDK)**
- **GitHub Actions CI/CD** (in progress)

---

## AWS Services Used
- **Amazon S3** – Cloud object storage for raw and processed datasets
- **AWS Lambda** – Serverless compute for ingesting and processing data
- **Amazon SQS** – Queuing system for event-driven processing
- **Amazon EventBridge** – Scheduled and event-based triggers
- **AWS CDK (Python)** – Infrastructure as Code
- **AWS IAM** – Role-based permissions for secure access

---

## Technologies
- **Languages & Libraries:** Python, Pandas, Boto3
- **DevOps Tools:** GitHub Actions (CI/CD)
- **Secrets Management:** AWS Secrets Manager, GitHub Secrets
- **Data Sources:** Public APIs (e.g., BLS, DataUSA)

---

## Notes
- This document omits any mention of outside companies and institutional partnerships per academic guidelines.

