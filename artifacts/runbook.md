# TechStart IT Help Bot — Operational Runbook

## Purpose
This runbook documents the operational procedures for the TechStart IT Help Bot,
an AI-powered FAQ assistant designed to reduce repetitive IT support tickets.
The bot automatically answers common employee questions using the Gemini AI API,
logs all interactions to a local SQLite database, and flags uncertain responses
for human review. By providing instant self-service answers, the IT team can
focus on complex tasks rather than repeatedly answering the same questions.

---

## How to Start the Bot (Local)
1. Open Terminal and navigate to the project folder:
   cd ~/Documents/GitHub/msit3000-helpdesk-bot
2. Confirm the API key environment variable is set:
   echo $GEMINI_API_KEY
3. Run the bot:
   python bot.py

The bot will display "TechStart IT Help Bot — type quit to exit" when ready.
Employees can then type questions directly into the terminal prompt.
To stop the bot at any time, type "quit" and press Enter.

---

## How to Run with Docker

Docker allows the bot to run in an isolated, reproducible container environment
independent of the host machine's Python installation or system configuration.
This is the recommended deployment method for consistency across environments.

1. Ensure Docker Desktop is installed and running (whale icon visible in menu bar)
2. Open Terminal in the project folder and build the image:
   docker build -t techstart-helpdesk-bot .
3. Start the container using docker-compose:
   docker-compose up

The docker-compose.yml file automatically passes the GEMINI_API_KEY environment
variable into the container so the bot can authenticate with the Gemini API.
The database volume mount ensures all logs are saved to the local filesystem
even after the container stops.

---

## How to Add New FAQ Entries

As TechStart's IT needs evolve, new FAQ entries should be added regularly to
keep the bot's knowledge base accurate and comprehensive. All FAQ content is
stored in sql/setup.sql and loaded into the SQLite database at setup time.

1. Open sql/setup.sql in any text editor
2. Add a new INSERT line following this format:
   INSERT INTO faq (question, answer, category) VALUES
   ('Your question here?', 'Your answer here.', 'Category');
3. Re-run the database setup to apply changes:
   python -c "import sqlite3; conn=sqlite3.connect('database/faq.db');
   conn.executescript(open('sql/setup.sql').read()); conn.close(); print('Done!')"

Categories currently in use: Access, Network, Hardware.
New categories can be added freely — use consistent naming for easier reporting.
It is recommended to test the new entry by asking the bot the exact question
after updating the database.

---

## Human Review Process

The bot automatically logs every interaction to the review_log table in faq.db,
including a confidence field that is set to "low" whenever the bot was uncertain
about its answer. IT staff should review these flagged entries weekly to catch
any incorrect or incomplete responses before they mislead employees.

Weekly review steps:
1. Open Terminal and query the review_log for low-confidence entries:
   python -c "import sqlite3; conn=sqlite3.connect('database/faq.db');
   [print(r) for r in conn.execute(\"SELECT * FROM review_log WHERE confidence='low'\")];
   conn.close()"
2. For each flagged entry, check whether the bot's response was accurate
3. If incorrect or missing: add the correct answer to setup.sql and re-run setup
4. Escalate questions that fall outside IT scope to it-support@techstart.com

Entries in the review_log should be purged after 90 days to limit data retention.
IT staff should never modify the review_log directly — only update the FAQ source
in setup.sql so changes are version-controlled and repeatable.

---

## Security Notes

The bot is designed with a least-privilege security model to minimize risk
while remaining easy to operate for non-technical IT staff at TechStart.

- API key management: The GEMINI_API_KEY is stored exclusively as an operating
  system environment variable. It is never written into bot.py, any config file,
  or the GitHub repository. If the key is accidentally exposed, revoke it
  immediately at aistudio.google.com and generate a new one.

- Approved content only: The bot's system prompt explicitly instructs the Gemini
  AI model to answer only from the approved FAQ knowledge base. The model cannot
  browse the internet, access internal systems, or answer questions outside the
  defined FAQ scope.

- Data retention: All entries in the review_log table are retained for 90 days
  and then deleted. No personally identifiable information is collected — only
  the question text and AI response are stored.

- No inbound access: The bot runs as a local process with no open ports and no
  web interface. It cannot be accessed remotely by employees or external parties
  in its current local deployment configuration.

---

## Network / Ports

The bot's network footprint is minimal by design. Only one outbound connection
is required for the bot to function — all other traffic is blocked.

| Direction | Destination                                  | Port | Protocol | Purpose              |
|-----------|----------------------------------------------|------|----------|----------------------|
| Outbound  | generativelanguage.googleapis.com            | 443  | HTTPS    | Gemini AI API calls  |
| Inbound   | None                                         | N/A  | N/A      | No inbound exposure  |
| Outbound  | All other destinations                       | Any  | Any      | BLOCKED              |

All communication with the Gemini API is encrypted via TLS over HTTPS.
No unencrypted traffic leaves the machine during bot operation.
In the planned AWS cloud deployment, a security group will enforce these same
rules at the network level using inbound/outbound firewall rules.

---

## Troubleshooting

| Problem                        | Likely Cause                        | Fix                                              |
|-------------------------------|-------------------------------------|--------------------------------------------------|
| Bot starts but API call fails  | GEMINI_API_KEY not set or expired   | Run: echo $GEMINI_API_KEY — re-set if blank      |
| "Module not found" error       | google-genai not installed          | Run: pip install google-genai                    |
| Docker build fails             | Docker Desktop not running          | Open Docker Desktop, wait for whale icon         |
| Bot gives wrong answer         | FAQ entry missing or outdated       | Add/update entry in setup.sql, re-run setup      |
| review_log not updating        | faq.db file permissions issue       | Run: ls -la database/ — check file is writable   |

---

## Cloud Migration Notes (Planned)

The current local deployment is a proof-of-concept. The planned next phase
migrates the bot to AWS to provide 24/7 availability independent of IT staff
laptops, centralized logging, and secure credential management.

Planned AWS services:
- AWS EC2 t2.micro: Host the containerized bot using the existing Docker image.
  The t2.micro instance is free-tier eligible for the first 12 months.
- AWS RDS (PostgreSQL): Replace the local SQLite database with a managed
  relational database for improved reliability and concurrent access support.
- AWS Secrets Manager: Store the GEMINI_API_KEY securely in the cloud rather
  than as a local environment variable, with automatic rotation support.
- AWS CloudWatch: Monitor bot uptime, API error rates, and review_log growth
  with automated alerts if the bot goes offline or error rates spike.

Estimated monthly cost after free tier: approximately $16/month.
Migration is planned for Phase 2 once the FAQ database reaches 20+ validated
entries and usage patterns are confirmed over a 30-day pilot period.

---

Last updated at April 2026 | Maintained by: TechStart IT Department