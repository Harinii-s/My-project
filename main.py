import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(__name__)

# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(api_key=API_KEY)

# Change the model here if your Google account/API
# exposes a different current Gemini model.
MODEL_NAME = "gemini-3.8-flash"

# --------------------------------------------------
# Database
# --------------------------------------------------

DATABASE = "edugenie.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            feature TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# Gemini function
# --------------------------------------------------

def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return "Sorry, I could not generate a response."

    except Exception as error:

        print("Gemini API Error:", error)

        return (
            "Sorry, something went wrong while connecting "
            "to Gemini. Please try again."
        )


# --------------------------------------------------
# Save chat
# --------------------------------------------------

def save_chat(question, answer, feature):

    connection = get_db()

    connection.execute(
        """
        INSERT INTO chat_history
        (user_message, ai_response, feature)
        VALUES (?, ?, ?)
        """,
        (question, answer, feature)
    )

    connection.commit()
    connection.close()


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# AI Chat
# --------------------------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:

        return jsonify({
            "success": False,
            "message": "Please enter a question."
        }), 400

    prompt = f"""
You are EduGenie, an educational AI learning assistant.

Your purpose is to help college students learn academic
subjects clearly and responsibly.

Answer the student's question in simple language.

Rules:
1. Explain concepts clearly.
2. Use examples when useful.
3. Break difficult concepts into smaller points.
4. Do not unnecessarily make the answer too long.
5. If the question is academic, use appropriate terminology.
6. If you are uncertain, clearly say so.

Student Question:
{question}
"""

    answer = ask_gemini(prompt)

    save_chat(question, answer, "chat")

    return jsonify({
        "success": True,
        "answer": answer
    })


# --------------------------------------------------
# Generate summary
# --------------------------------------------------

@app.route("/summary", methods=["POST"])
def summary():

    data = request.get_json()

    text = data.get("text", "").strip()

    if not text:

        return jsonify({
            "success": False,
            "message": "Please enter study material."
        }), 400

    prompt = f"""
You are EduGenie, an educational assistant.

Summarize the following study material for a college student.

Requirements:
- Give a short overview.
- Extract important points.
- Use simple language.
- Use bullet points where appropriate.
- Keep important technical terms.
- Do not add unrelated information.

Study Material:
{text}
"""

    answer = ask_gemini(prompt)

    save_chat(text, answer, "summary")

    return jsonify({
        "success": True,
        "answer": answer
    })


# --------------------------------------------------
# Generate quiz
# --------------------------------------------------

@app.route("/quiz", methods=["POST"])
def quiz():

    data = request.get_json()

    topic = data.get("topic", "").strip()

    if not topic:

        return jsonify({
            "success": False,
            "message": "Please enter a topic."
        }), 400

    prompt = f"""
You are EduGenie, an educational quiz generator.

Create 5 multiple-choice questions about:

{topic}

For every question provide:

Question:
A.
B.
C.
D.

Correct Answer:
Explanation:

Make the questions suitable for a college student.
Avoid ambiguous questions.
"""

    answer = ask_gemini(prompt)

    save_chat(topic, answer, "quiz")

    return jsonify({
        "success": True,
        "answer": answer
    })


# --------------------------------------------------
# Generate study notes
# --------------------------------------------------

@app.route("/notes", methods=["POST"])
def notes():

    data = request.get_json()

    topic = data.get("topic", "").strip()

    if not topic:

        return jsonify({
            "success": False,
            "message": "Please enter a topic."
        }), 400

    prompt = f"""
You are EduGenie, a college study-notes assistant.

Create well-structured study notes for:

{topic}

Use this structure:

1. Definition
2. Introduction
3. Important Concepts
4. Key Points
5. Example
6. Advantages
7. Limitations
8. Conclusion

Use simple and understandable language.
"""

    answer = ask_gemini(prompt)

    save_chat(topic, answer, "notes")

    return jsonify({
        "success": True,
        "answer": answer
    })


# --------------------------------------------------
# Chat history
# --------------------------------------------------

@app.route("/history", methods=["GET"])
def history():

    connection = get_db()

    rows = connection.execute(
        """
        SELECT id, user_message, ai_response,
               feature, created_at
        FROM chat_history
        ORDER BY id DESC
        LIMIT 50
        """
    ).fetchall()

    connection.close()

    history_data = []

    for row in rows:

        history_data.append({
            "id": row["id"],
            "question": row["user_message"],
            "answer": row["ai_response"],
            "feature": row["feature"],
            "created_at": row["created_at"]
        })

    return jsonify({
        "success": True,
        "history": history_data
    })


# --------------------------------------------------
# Delete history
# --------------------------------------------------

@app.route("/history/delete", methods=["DELETE"])
def delete_history():
    connection = get_db()

    connection.execute("DELETE FROM chat_history")

    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Chat history deleted."
    })


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )        