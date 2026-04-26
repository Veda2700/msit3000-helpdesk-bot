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
    prompt = f"""You are an IT help desk assistant for TechStart Solutions.
Answer ONLY from the FAQ below. If not covered, say exactly:
I'm not confident - flagging for human review.

FAQ:
{faq}

Employee question: {question}"""
    r = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
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