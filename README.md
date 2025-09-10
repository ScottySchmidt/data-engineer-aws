# AWS Data Engineering Pipeline (Four-Part) 
**Note:** The code for this project cannot be shared publicly due to confidentiality agreements.  

---
A four-stage pipeline on AWS — **ingest → store → analyze → deploy-as-code**.  
Uses S3, Lambda, SQS, EventBridge, IAM, and CDK (Python). Mirrors real-world data pipeline flows for scalability and easy maintenance.  

## Three Deployment Methods
- A. Local Jupyter Notebook (Python CDK)
- B. AWS CloudShell (Python CDK)  
- C. GitHub Actions CI/CD *(automated deploys — in process)*

## Pipeline Overview:
- One Lambda ingests data directly from the BLS and DataUSA APIs.  
- An S3 bucket stores raw and processed outputs.  
- Another Lambda joins the datasets, applies hashing for integrity/deduplication, and generates summary reports.  
- EventBridge triggers the ingest Lambda on a daily schedule.  
- When a new file lands in S3, it sends a notification to SQS.  
- The queue holds the event until the report Lambda processes it.  

---

## CI/CD with GitHub Actions  
**Goal:** Deploy fast and debug faster.  
- **Pipeline:** Git push → Actions → Build/Test → AWS   
[**View CI/CD workflows (in progress)**](https://github.com/ScottySchmidt/AWS_DataEngineer_API)
<img width="337" height="70" alt="image" src="https://github.com/user-attachments/assets/fd656576-0b56-490c-b159-1caab543429e" />

---

## 1. API Data from BLS → AWS S3  
Uses API to fetch productivity & inflation data and bulk files.  
- Uses compliant User-Agent & file hash checks to skip unchanged data  
- Stores JSON results in Amazon S3
- Enhanced Sync version keeps S3 updated—adds, updates, and deletes automatically
- **[View Notebook – Enhanced Sync Version](https://github.com/ScottySchmidt/AWS_DataEngineer_API/blob/main/01-ingest-api-sync.ipynb)**

## 2. **API Request via AWS Lambda → S3**  
   Automates pulling API data from BLS and dropping JSON into S3 on a monthly schedule using AWS Lambda Amazon EventBridge. 
   Acts as a bridge between Part 1 and Part 3 data analysis.  
   **[View Script](https://github.com/ScottySchmidt/AWS_DataEngineer_API/blob/main/02-api-lambda-s3.py)**

## 3. **Data Processing and Analysis**  
   Loads data from S3 into a Pandas notebook where it’s cleaned, merged, and transformed before producing summary reports. 
   
   **[Enhanced Sync Version - In Process](https://github.com/ScottySchmidt/AWS_DataEngineer_API/blob/main/03-analytics-sync-reports.ipynb)**

## 4. **Infrastructure as Code — AWS CDK Deployment**
Automate the above steps. The SQS queue is actively mapped to two Lambda functions:  
Both event source mappings are Enabled, confirming that the event-driven pipeline is live: S3 → SQS → Lambda
<img width="833" height="117" alt="lambda" src="https://github.com/user-attachments/assets/8e1d245a-f54b-4a60-bd92-769eb512a110" />

   #### Method A: Python CDK (Local Jupyter Notebook)
   Runs directly from a Jupyter Notebook with minimal or no CloudShell usage.  
   This approach is easier to iterate on, test, and document.  
   **[View Notebook](https://github.com/ScottySchmidt/AWS_DataEngineer_API/blob/main/04-cdk-iac-python-local.ipynb)**
   
   #### Method B: Python CDK (AWS CloudShell)
   No local setup is required.  
   **[View Deployment Logs (sanitized)](https://github.com/ScottySchmidt/AWS_DataEngineer_API/tree/main/docs/part4)**
   
   CloudFormation stack below proves a fully deployed AWS data pipeline:  
   <img width="600" height="400" alt="bls_pipeline_stack" src="https://github.com/user-attachments/assets/0540c36d-3b47-42f5-98ea-a2a08e2436ed" />

---
#### AWS Tech Stack  
- **Amazon S3** — buckets for both raw and processed BLS datasets  
- **AWS Lambda** — pulls API data and drops it into S3  
- **Amazon SQS** — queue for event-driven report processing (Part 4)  
- **Amazon EventBridge** — kicks off Lambda runs on a set schedule  
- **AWS IAM** — scoped-down roles for Lambda, S3, and SQS access  
- **AWS CDK** — spins up the stack (Lambda, S3, SQS) as code  
- **AWS Glue Data Catalog** — keeps S3 datasets organized with schemas  
- **Amazon Athena** — run SQL queries directly on S3 data via the Glue catalog  

#### Security, SDKs & Data Sources
- **Secrets:** Github and Kaggle Secrets; AWS Secrets Manager
- **SDKs:** Python, Pandas, Boto3 (AWS SDK for Python)
- **Sources:** BLS Public API + bulk files; DataUSA API
