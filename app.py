import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DB_PATH = os.getenv("DATABASE_PATH", "marketai.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                product TEXT DEFAULT '',
                status TEXT DEFAULT 'New',
                created_at TEXT NOT NULL
            )
        """)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    product = (data.get("product") or "").strip()
    audience = (data.get("audience") or "सामान्य ग्राहक").strip()
    language = (data.get("language") or "Hindi").strip()
    kind = (data.get("kind") or "ads").strip()
    details = (data.get("details") or "").strip()

    if not product:
        return jsonify({"error": "कृपया प्रोडक्ट का नाम लिखें।"}), 400

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "OPENAI_API_KEY सेट नहीं है। .env फ़ाइल में अपनी API key जोड़ें।"}), 503

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompts = {
            "ads": "Create 3 distinct Meta ad variations. For each include Hook, Primary Text, Headline, Description, CTA. Avoid unsupported claims and deceptive guarantees.",
            "creative": "Create 3 creative concepts for a social media ad. For each include visual scene, on-screen text, voiceover, shot sequence, and an image-generation prompt. Do not claim an image file has been generated.",
            "landing": "Write landing-page copy with hero headline, subheadline, benefits, how-it-works, FAQ, and CTA. Avoid unsupported or guaranteed claims.",
            "meta": "Create a campaign planning brief with objective, audience hypotheses, creative tests, metrics to monitor, and a reporting template. Do not claim to access live Meta account data."
        }
        task = prompts.get(kind, prompts["ads"])
        user_prompt = f"""You are a careful digital marketing assistant. Respond in {language}.
Product/service: {product}
Target audience: {audience}
Verified product details and constraints: {details or 'Not provided; do not invent facts.'}
Task: {task}
Use clear headings and practical output. If this is a health, herbal, financial, or other regulated product, avoid medical/financial guarantees and unsupported efficacy claims."""
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-6-astra"),
            input=user_prompt
        )
        return jsonify({"result": response.output_text})
    except Exception as exc:
        app.logger.exception("AI generation failed")
        return jsonify({"error": f"AI अनुरोध पूरा नहीं हुआ: {str(exc)}"}), 500

@app.route("/api/leads", methods=["GET", "POST"])
def leads():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        product = (data.get("product") or "").strip()
        if not name or not phone:
            return jsonify({"error": "नाम और मोबाइल नंबर आवश्यक हैं।"}), 400
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            return jsonify({"error": "मोबाइल नंबर सही दर्ज करें।"}), 400
        with db() as conn:
            conn.execute(
                "INSERT INTO leads (name, phone, product, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, digits, product, "New", datetime.now().isoformat(timespec="seconds"))
            )
        return jsonify({"ok": True})
    with db() as conn:
        rows = conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 500").fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/leads/<int:lead_id>", methods=["PATCH"])
def update_lead(lead_id):
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip()
    if status not in {"New", "Contacted", "Qualified", "Won", "Lost"}:
        return jsonify({"error": "अमान्य स्थिति"}), 400
    with db() as conn:
        cur = conn.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))
        if cur.rowcount == 0:
            return jsonify({"error": "लीड नहीं मिली"}), 404
    return jsonify({"ok": True})

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

init_db()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", "5000")))
