# AWS deployment roadmap (matches the submitted synopsis)

The submitted synopsis describes the following flow: web/mobile frontend -> HTTPS REST API -> EC2 backend -> RDS or DynamoDB -> Kinesis -> Glue or EMR -> Redshift -> QuickSight.

This ZIP is a **local working prototype**, not a one-click production AWS deployment. The following choices are recommended for a manageable college demo:

| Layer in submitted architecture | Suggested AWS choice | What must be configured |
|---|---|---|
| Frontend | Static site on S3 (optional CloudFront) | Build/host frontend and configure API URL |
| Cloud backend | EC2 | Launch Linux instance, install Python, configure security group, run API behind a web server |
| Database | Amazon RDS (PostgreSQL) OR DynamoDB | Choose one and adapt backend persistence layer; local version currently uses SQLite |
| Real-time stream | Kinesis Data Streams | Create stream and send record-created events from backend |
| Processing | AWS Glue (simpler batch ETL option) | Create Glue job and IAM role to read stream/exported data |
| Analytics store | Redshift Serverless | Create workgroup/namespace and load processed aggregates |
| Visualization | QuickSight | Connect QuickSight to Redshift and create datasets/charts |

## Safe implementation order
1. First run and test the local app using `README.md`.
2. Create an AWS budget alert before creating paid resources.
3. Choose **one** database option (RDS or DynamoDB) with your project supervisor. The local SQLite database is only for laptop development.
4. Deploy the backend to EC2 and secure it (do not expose database ports publicly).
5. Add Kinesis event publishing and test it with non-sensitive sample records.
6. Configure Glue/EMR processing and Redshift only after the basic API and database work.
7. Connect QuickSight to Redshift and build the final visual reports.
8. Take screenshots of the working resources and dashboard for the college report.
9. Delete demo resources when finished to avoid ongoing charges.

## Cost and security warnings
- AWS services may incur charges. Free-tier eligibility and prices vary by account, region and date.
- Set an AWS Budget alert first and check the Pricing Calculator.
- Never put AWS access keys, passwords, database credentials or tokens in source files or screenshots.
- Use IAM roles for EC2 permissions, least-privilege policies, HTTPS, and private database networking.
- Do not use real student personal information in a public demo.
