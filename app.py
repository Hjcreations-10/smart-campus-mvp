from flask import Flask, request, jsonify, render_template
import os
import firebase_admin
from firebase_admin import credentials, db
from google.cloud import language_v1

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

        document = language_v1.Document(
            content=data["url"],
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        client = language_v1.LanguageServiceClient()
        response = client.classify_text(request={"document": document})

        for category in response.categories:
            if "Education" in category.name:
                return jsonify({"status": "ALLOWED"})

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
