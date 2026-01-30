from flask import Flask, request, jsonify, render_template
import os
import requests
import firebase_admin
from firebase_admin import credentials, db
from google.cloud import language_v1
from bs4 import BeautifulSoup   # for extracting text

app = Flask(__name__)

# 🔐 Firebase Init
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DB_URL", "https://YOUR_PROJECT.firebaseio.com")
})

# 🏠 Frontend routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------------------------
# Backend APIs
# ---------------------------
@app.route("/check_url", methods=["POST"])
def check_url():
    try:
        data = request.get_json(silent=True)
        if not data or "url" not in data:
            return jsonify({"error": "Missing 'url'", "status": "ERROR"}), 400

        url = data["url"].strip()
        if not url.startswith("http"):
            url = "https://" + url   # auto prepend https

        # 1️⃣ Fetch webpage content
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            page_text = " ".join([p.get_text() for p in soup.find_all("p")])
        except Exception as e:
            return jsonify({"error": f"Failed to fetch webpage: {str(e)}", "status": "ERROR"}), 500

        if not page_text or len(page_text.split()) < 20:
            return jsonify({"status": "BLOCKED", "error": "Not enough content to classify"})

        # 2️⃣ Classify text using Google NLP
        document = language_v1.Document(
            content=page_text,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        client = language_v1.LanguageServiceClient()
        response = client.classify_text(request={"document": document})

        # 3️⃣ Check categories
        for category in response.categories:
            if "Education" in category.name:
                return jsonify({"status": "ALLOWED", "url": url})

        return jsonify({"status": "BLOCKED"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "ERROR"}), 500


@app.route("/log", methods=["POST"])
def log_activity():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing body"}), 400
    db.reference("logs").push(data)
    return jsonify({"message": "Logged"}), 201

@app.route("/library", methods=["GET"])
def library():
    books = [
        {"title": "Machine Learning Basics", "author": "Andrew Ng"},
        {"title": "Cloud Computing", "author": "Google"},
        {"title": "Data Structures", "author": "CLRS"}
    ]
    return jsonify({"books": books})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
