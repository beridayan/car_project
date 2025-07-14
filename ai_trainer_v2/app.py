import os
import json
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

API_KEY = "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"  # Put your real API key here
client = OpenAI(api_key=API_KEY)

app = Flask(__name__)

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

memory = load_memory()

def build_prompt(question):
    memory_text = "\n".join([f"- {m['concept']}: {m['explanation']}" for m in memory])
    prompt = f"""
You are an AI student learning from a teacher. Here is what you know:

{memory_text}

If you don't know the answer, ask a clarifying question.

Question: {question}
Answer:"""
    return prompt.strip()

@app.route('/')
def index():
    # Simple HTML page with forms and JS to call API
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Trainable AI Student</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 20px auto; }
    textarea, input { width: 100%; padding: 8px; margin: 5px 0; }
    button { padding: 10px 15px; margin: 10px 0; }
    #answer { background: #f0f0f0; padding: 15px; min-height: 50px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>Trainable AI Student</h1>

  <h2>Teach the AI</h2>
  <input id="concept" placeholder="Concept (e.g. 2+2)" />
  <textarea id="explanation" placeholder="Explanation"></textarea>
  <button onclick="teach()">Teach</button>
  <div id="teachResult"></div>

  <hr/>

  <h2>Ask the AI</h2>
  <textarea id="question" placeholder="Ask your question here"></textarea>
  <button onclick="ask()">Ask</button>
  <div id="answer"></div>

  <script>
    async function teach() {
      const concept = document.getElementById('concept').value.trim();
      const explanation = document.getElementById('explanation').value.trim();
      if (!concept || !explanation) {
        alert("Please enter both concept and explanation.");
        return;
      }
      const res = await fetch('/teach', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({concept, explanation})
      });
      const data = await res.json();
      document.getElementById('teachResult').innerText = data.message || data.error;
      document.getElementById('concept').value = '';
      document.getElementById('explanation').value = '';
    }

    async function ask() {
      const question = document.getElementById('question').value.trim();
      if (!question) {
        alert("Please enter a question.");
        return;
      }
      document.getElementById('answer').innerText = "Thinking...";
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
      });
      const data = await res.json();
      document.getElementById('answer').innerText = data.answer || data.error;
    }
  </script>
</body>
</html>
    """)

@app.route('/teach', methods=['POST'])
def teach():
    global memory
    data = request.json
    concept = data.get("concept")
    explanation = data.get("explanation")

    if not concept or not explanation:
        return jsonify({"error": "Missing concept or explanation"}), 400

    memory.append({"concept": concept, "explanation": explanation})
    save_memory(memory)
    return jsonify({"message": f"Learned concept '{concept}'"}), 200

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing question"}), 400

    prompt = build_prompt(question)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
