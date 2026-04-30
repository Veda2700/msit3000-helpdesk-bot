from flask import Flask, render_template_string, request, jsonify
import sqlite3, os
from google import genai
import markdown

app = Flask(__name__)
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
    prompt = f"""You are a knowledgeable IT support assistant for TechStart Solutions.
Use the FAQ below for company-specific info. For general IT questions, use your expertise.

TechStart FAQ:
{faq}

Question: {question}

Give a complete, helpful answer. If you're unsure, say: I'm not confident - flagging for review."""
    r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    answer = markdown.markdown(r.text)
    conf = "low" if "not confident" in answer.lower() else "high"
    log_to_db(question, answer, conf)
    return answer, conf

@app.route('/')
def index():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>TechStart IT Bot</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f5f5f5;height:100vh;display:flex;flex-direction:column}
.top{background:#1a1a2e;color:#fff;padding:14px 20px;display:flex;align-items:center;gap:10px}
.top h1{font-size:15px}
.chat{flex:1;overflow-y:auto;padding:20px;max-width:800px;width:100%;margin:0 auto}
.msg{display:flex;gap:10px;margin-bottom:16px;max-width:75%}
.msg.user{flex-direction:row-reverse;align-self:flex-end;margin-left:auto}
.av{width:32px;height:32px;border-radius:50%;background:#4f46e5;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0}
.msg.user .av{background:#e5e7eb;color:#333}
.bubble{padding:12px 16px;border-radius:18px;background:#fff;font-size:14px;line-height:1.6;box-shadow:0 1px 2px rgba(0,0,0,0.1);overflow-wrap:break-word;word-wrap:break-word}
.bubble p{margin:0 0 0.75rem}
.bubble ol,.bubble ul{margin:0.5rem 0 0.5rem 1.2rem;padding-left:1.2rem}
.bubble li{margin-bottom:0.45rem}
.bubble code{background:#f3f4f6;padding:2px 4px;border-radius:4px;font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace}
.msg.user .bubble{background:#4f46e5;color:#fff}
.typing{display:flex;gap:4px;padding:12px 16px;background:#fff;border-radius:18px}
.dot{width:6px;height:6px;background:#999;border-radius:50%;animation:b 1.2s infinite}
.dot:nth-child(2){animation-delay:0.2s}
.dot:nth-child(3){animation-delay:0.4s}
@keyframes b{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-5px)}}
.sugg{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}
.sugg span{background:#fff;border:1px solid #ddd;padding:6px 12px;border-radius:20px;font-size:13px;cursor:pointer;color:#4f46e5}
.sugg span:hover{background:#4f46e5;color:#fff}
.input-area{background:#fff;border-top:1px solid #e5e7eb;padding:16px 20px}
.input-row{display:flex;gap:10px;max-width:800px;margin:0 auto}
#inp{flex:1;border:1px solid #ddd;border-radius:24px;padding:10px 16px;font-size:14px;outline:none}
#inp:focus{border-color:#4f46e5}
#btn{background:#4f46e5;color:#fff;border:none;width:40px;height:40px;border-radius:50%;cursor:pointer;font-size:16px}
#btn:disabled{background:#ccc}
.warn{background:#fef3c7;border:1px solid #f59e0b;padding:8px 12px;border-radius:8px;margin-top:6px;font-size:12px;color:#92400e}
</style>
</head><body>
<div class="top"><h1>🤖 TechStart IT Help Bot</h1></div>
<div class="chat" id="chat">
<div class="msg"><div class="av">IT</div><div>
<div class="bubble">Hi! I'm TechStart's IT Help Bot. Ask me anything or try a suggestion:</div>
<div class="sugg">
<span onclick="ask(this)">My laptop is running slow</span>
<span onclick="ask(this)">How do I set up 2FA?</span>
<span onclick="ask(this)">My Wi-Fi keeps dropping</span>
<span onclick="ask(this)">How do I reset my password?</span>
</div></div></div>
</div>
<div class="input-area">
<div class="input-row">
<input id="inp" placeholder="Ask an IT question..." onkeydown="if(event.key==='Enter')send()">
<button id="btn" onclick="send()">➤</button>
</div></div>
<script>
function add(txt,who,flag){
const d=document.createElement('div');
d.className='msg '+(who||'bot');
const processedTxt = who === 'user' ? txt.replace(/\\n/g,'<br>') : txt;
d.innerHTML='<div class="av">'+(who==='user'?'You':'IT')+'</div><div><div class="bubble">'+processedTxt+'</div>'+(flag?'<div class="warn">⚠ Flagged for review</div>':'')+'</div>';
chat.appendChild(d);
chat.scrollTop=9999;
}
function typing(){
const d=document.createElement('div');d.className='msg';d.id='typ';
d.innerHTML='<div class="av">IT</div><div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
chat.appendChild(d);chat.scrollTop=9999;
}
async function send(){
const q=inp.value.trim();
if(!q)return;
inp.value='';btn.disabled=true;
add(q,'user');
typing();
try{
const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
const data=await r.json();
typ.remove();
add(data.answer,'bot',data.flagged);
}catch(e){typ.remove();add('Error: '+e.message,'bot');}
btn.disabled=false;inp.focus();
}
function ask(el){inp.value=el.textContent;send();}
</script>
</body></html>"""

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    answer, conf = ask_bot(question)
    return jsonify({'answer': answer, 'flagged': conf == 'low'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)