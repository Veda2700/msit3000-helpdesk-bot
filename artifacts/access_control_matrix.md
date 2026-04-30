# Access Control Matrix — TechStart IT Help Bot

## Role-Based Access

| Role       | Run Bot | View review_log | Edit FAQ | View API Key |
|------------|---------|-----------------|----------|--------------|
| Employee   | YES     | NO              | NO       | NO           |
| IT Staff   | YES     | YES             | YES      | NO           |
| IT Admin   | YES     | YES             | YES      | YES          |

## Network Controls

| Traffic              | Direction | Port | Protocol | Allowed |
|----------------------|-----------|------|----------|---------|
| Employee to Bot      | Inbound   | Local| CLI      | YES     |
| Bot to Gemini API    | Outbound  | 443  | HTTPS    | YES     |
| Bot to Internet(other)| Outbound | Any  | Any      | NO      |
| Inbound from internet| Inbound   | Any  | Any      | NO      |

## Least Privilege Decisions
- API key only accessible via environment variable
- review_log readable only by IT staff, not employees
- Bot cannot modify FAQ entries at runtime
- No admin credentials stored in codebase
- Docker container runs as non-root user