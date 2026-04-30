# Cloud Deployment Plan — TechStart Solutions

## Current State
Bot runs locally on IT staff MacBook.
SQLite database stored on local filesystem.
API key stored as local environment variable.

## Why Cloud Matters
- Local deployment creates single point of failure
- IT staff laptop being offline = bot offline
- No backup, no monitoring, no uptime guarantee

## Proposed AWS Architecture
| Component        | AWS Service         | Purpose                    | Cost        |
|------------------|---------------------|----------------------------|-------------|
| Bot hosting      | EC2 t2.micro        | Run bot.py 24/7            | Free tier   |
| Database         | RDS PostgreSQL      | Replace SQLite             | ~$15/month  |
| API key storage  | Secrets Manager     | Secure key management      | ~$0.40/mo   |
| Monitoring       | CloudWatch          | Uptime + error alerts      | Free tier   |
| Container reg.   | ECR                 | Store Docker image         | Free tier   |

## Migration Path
Phase 1 (current): Local Python + SQLite — DONE
Phase 2 (next):    Docker container on EC2 + RDS
Phase 3 (future):  Auto-scaling with load balancer

## Why Not Deployed to Cloud Yet
This is a proof-of-concept phase. Cloud deployment
is the next milestone once:
- FAQ database reaches 20+ validated entries
- Usage patterns are confirmed
- IT staff training is complete

## Total Estimated Monthly Cost
Free tier: $0/month for first 12 months
After free tier: ~$16/month