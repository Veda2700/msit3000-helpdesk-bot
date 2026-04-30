import sqlite3, os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
DB_PATH = "database/faq.db"

def get_faq_context():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT question, answer FROM faq").fetchall()
    conn.close()
    return "\n".join([f"Q: {r[0]}\nA: {r[1]}" for r in rows])

def log_to_db(query, response, confidence):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO review_log (user_query,ai_response,confidence) VALUES(?,?,?)",
                 (query, response, confidence))
    conn.commit()
    conn.close()

def ask_bot(question):
    faq = get_faq_context()
    prompt = f"""You are a knowledgeable IT support assistant for TechStart Solutions, a 20-person tech startup.
You have access to TechStart's internal FAQ below. Use it as your primary reference for company-specific details
(like internal URLs, contacts, and policies). For general IT questions, use your own expertise to give
complete, helpful, step-by-step answers.

TechStart Internal FAQ (use for company-specific info):
{faq}

Guidelines:
- For questions covered in the FAQ: use the FAQ answer but expand it with helpful context
- For general IT questions not in FAQ: answer fully using your IT expertise
- For questions completely outside IT scope: politely decline and suggest who can help
- Always be specific and actionable — no vague answers
- If something is truly unknown or specific to TechStart's unreleased systems, say:
  I'm not confident about this specific detail - flagging for IT staff review.
- Keep answers concise but complete — use bullet points or numbered steps when helpful

Employee question: {question}"""

    r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    answer = r.text
    conf = "low" if "not confident" in answer.lower() else "high"
    log_to_db(question, answer, conf)
    return answer, conf

if __name__ == "__main__":
    print("TechStart IT Help Bot — type quit to exit\n")
    while True:
        q = input("Your question: ")
        if q.lower() == "quit": break
        ans, conf = ask_bot(q)
        print(f"\nBot: {ans}")
        if conf == "low": print("WARNING: Flagged for human review")
        print()