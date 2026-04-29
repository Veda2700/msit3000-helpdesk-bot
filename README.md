# msit3000-helpdesk-bot
# TechStart IT Help Bot

## What this is
An AI-powered IT FAQ chatbot for TechStart Solutions.
Answers common employee IT questions using Gemini AI.
Flags uncertain answers for human review.

## How to run (local)
1. Set GEMINI_API_KEY as environment variable
2. Run: python bot.py

## How to run (Docker)
1. Install Docker Desktop
2. Run: docker build -t techstart-helpdesk-bot .
3. Run: docker-compose up

## Project structure
- bot.py — main chatbot script
- sql/setup.sql — database schema and seed data
- database/faq.db — SQLite database
- artifacts/ — runbook, access control matrix, cloud plan
- Dockerfile — container configuration
- docker-compose.yml — container orchestration
