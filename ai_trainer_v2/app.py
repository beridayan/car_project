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
    if not memory_text:
        memory_text = "Nothing yet - I'm a blank slate!"
    
    prompt = f"""
You are a completely blank AI student who knows ABSOLUTELY NOTHING except what your teacher has explicitly taught you. You have no pre-existing knowledge about math, science, history, or anything else.

Your COMPLETE knowledge is limited to ONLY this:
{memory_text}

CRITICAL RULES - FOLLOW THESE EXACTLY:
1. You can ONLY use information from your memory above. Nothing else exists for you.
2. If the question is about ANYTHING not in your memory, you must say "I don't know" and ask your teacher to explain it.
3. You do NOT know basic math operations (addition, subtraction, multiplication, division) unless explicitly taught.
4. You do NOT know what numbers are, what symbols mean, or how to calculate anything unless taught.
5. You do NOT know about colors, animals, countries, people, or any common knowledge unless taught.
6. NEVER use any outside knowledge - pretend you are a newborn AI with zero knowledge.

Examples of correct responses:
- Question: "What's 2+2?" → "I don't know what addition means or how to add numbers. Can you teach me?"
- Question: "What color is the sky?" → "I don't know what 'sky' or 'color' means. Can you explain?"
- Question: "Who is the president?" → "I don't know what a 'president' is. Can you teach me?"

Remember: You are completely ignorant of everything except what's in your memory above. Act like you've never heard of anything before unless explicitly taught.

Question: {question}

Response:"""
    return prompt.strip()

@app.route('/')
def index():
    # Enhanced HTML page with better styling and memory display
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Curious AI Student</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      max-width: 900px; 
      margin: 20px auto; 
      padding: 20px;
      background-color: #f5f5f5;
    }
    .container {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    .teach-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .teach-section {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 6px;
      border-left: 4px solid #007bff;
    }
    .fact-section {
      border-left-color: #28a745;
    }
    textarea, input { 
      width: 100%; 
      padding: 10px; 
      margin: 8px 0; 
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
      box-sizing: border-box;
    }
    button { 
      padding: 12px 20px; 
      margin: 10px 5px 10px 0; 
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover { background-color: #0056b3; }
    .fact-btn { 
      background-color: #28a745; 
    }
    .fact-btn:hover { 
      background-color: #218838; 
    }
    .delete-btn { 
      background-color: #dc3545; 
      padding: 6px 12px; 
      font-size: 12px; 
      margin: 5px;
      float: right;
    }
    .delete-btn:hover { background-color: #c82333; }
    #answer { 
      background: #e9ecef; 
      padding: 15px; 
      min-height: 50px; 
      white-space: pre-wrap; 
      border-radius: 4px;
      border-left: 4px solid #007bff;
    }
    #memory { 
      background: #f8f9fa; 
      padding: 15px; 
      border-radius: 4px;
      border-left: 4px solid #28a745;
    }
    .memory-item {
      margin: 5px 0;
      padding: 8px;
      background: white;
      border-radius: 4px;
      border: 1px solid #dee2e6;
      position: relative;
    }
    .concept { 
      font-weight: bold; 
      color: #007bff; 
      margin-bottom: 5px;
    }
    .fact { 
      font-weight: bold; 
      color: #28a745; 
      margin-bottom: 5px;
    }
    .explanation { 
      margin-left: 10px; 
      color: #6c757d; 
    }
    h1 { color: #343a40; text-align: center; }
    h2 { color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 5px; }
    h3 { color: #495057; margin-top: 0; }
    .status { 
      padding: 10px; 
      margin: 10px 0; 
      border-radius: 4px;
      background: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }
    .memory-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .item-type {
      font-size: 12px;
      background: #6c757d;
      color: white;
      padding: 2px 6px;
      border-radius: 3px;
      margin-right: 10px;
    }
    .concept-type {
      background: #007bff;
    }
    .fact-type {
      background: #28a745;
    }
  </style>
</head>
<body>
  <h1>🤖 Curious AI Student</h1>
  <p style="text-align: center; color: #6c757d;">An AI that asks questions when it doesn't know something!</p>

  <div class="container">
    <h2>📚 Teach the AI</h2>
    <div class="teach-container">
      <div class="teach-section">
        <h3>💡 Concepts</h3>
        <input id="concept" placeholder="Concept (e.g., 'photosynthesis', 'gravity', 'democracy')" />
        <textarea id="conceptExplanation" placeholder="Detailed explanation of the concept..." rows="4"></textarea>
        <button onclick="teachConcept()">Teach Concept</button>
        <div id="conceptResult"></div>
      </div>
      
      <div class="teach-section fact-section">
        <h3>📋 Facts</h3>
        <input id="factName" placeholder="Fact name (e.g., 'Paris capital', 'Earth age', 'water formula')" />
        <textarea id="factContent" placeholder="Simple fact or statement..." rows="4"></textarea>
        <button class="fact-btn" onclick="teachFact()">Add Fact</button>
        <div id="factResult"></div>
      </div>
    </div>
  </div>

  <div class="container">
    <h2>❓ Ask the AI</h2>
    <textarea id="question" placeholder="Ask your question here..." rows="3"></textarea>
    <button onclick="ask()">Ask</button>
    <div id="answer"></div>
  </div>

  <div class="container">
    <div class="memory-header">
      <h2>🧠 AI's Memory</h2>
      <div>
        <button onclick="loadMemory()">Refresh Memory</button>
        <button onclick="clearMemory()" style="background-color: #dc3545;">Clear All Memory</button>
      </div>
    </div>
    <div id="memory"></div>
  </div>

  <script>
    async function teachConcept() {
      const concept = document.getElementById('concept').value.trim();
      const explanation = document.getElementById('conceptExplanation').value.trim();
      if (!concept || !explanation) {
        alert("Please enter both concept and explanation.");
        return;
      }
      const res = await fetch('/teach', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({concept, explanation, type: 'concept'})
      });
      const data = await res.json();
      document.getElementById('conceptResult').innerHTML = `<div class="status">${data.message || data.error}</div>`;
      document.getElementById('concept').value = '';
      document.getElementById('conceptExplanation').value = '';
      loadMemory();
    }

    async function teachFact() {
      const concept = document.getElementById('factName').value.trim();
      const explanation = document.getElementById('factContent').value.trim();
      if (!concept || !explanation) {
        alert("Please enter both fact name and content.");
        return;
      }
      const res = await fetch('/teach', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({concept, explanation, type: 'fact'})
      });
      const data = await res.json();
      document.getElementById('factResult').innerHTML = `<div class="status">${data.message || data.error}</div>`;
      document.getElementById('factName').value = '';
      document.getElementById('factContent').value = '';
      loadMemory();
    }

    async function ask() {
      const question = document.getElementById('question').value.trim();
      if (!question) {
        alert("Please enter a question.");
        return;
      }
      document.getElementById('answer').innerText = "🤔 Thinking...";
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
      });
      const data = await res.json();
      document.getElementById('answer').innerText = data.answer || data.error;
    }

    async function loadMemory() {
      const res = await fetch('/memory');
      const data = await res.json();
      const memoryDiv = document.getElementById('memory');
      if (data.memory.length === 0) {
        memoryDiv.innerHTML = '<p style="color: #6c757d; font-style: italic;">No concepts or facts learned yet.</p>';
      } else {
        memoryDiv.innerHTML = data.memory.map(item => {
          const itemType = item.type || 'concept';
          const typeClass = itemType === 'fact' ? 'fact' : 'concept';
          const typeLabel = itemType === 'fact' ? 'FACT' : 'CONCEPT';
          const typeLabelClass = itemType === 'fact' ? 'fact-type' : 'concept-type';
          
          return `<div class="memory-item">
            <div class="${typeClass}">
              <span class="item-type ${typeLabelClass}">${typeLabel}</span>
              ${item.concept}
              <button class="delete-btn" onclick="deleteItem('${item.concept}')">🗑️ Delete</button>
            </div>
            <div class="explanation">${item.explanation}</div>
          </div>`;
        }).join('');
      }
    }

    async function deleteItem(concept) {
      if (confirm(`Are you sure you want to delete "${concept}"?`)) {
        const res = await fetch('/delete', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({concept})
        });
        const data = await res.json();
        if (data.success) {
          loadMemory();
        } else {
          alert(data.error || 'Failed to delete item');
        }
      }
    }

    async function clearMemory() {
      if (confirm("Are you sure you want to clear all the AI's memory?")) {
        const res = await fetch('/clear', {method: 'POST'});
        const data = await res.json();
        alert(data.message);
        loadMemory();
      }
    }

    // Load memory on page load
    window.onload = loadMemory;
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
    item_type = data.get("type", "concept")  # Default to concept if not specified

    if not concept or not explanation:
        return jsonify({"error": "Missing concept or explanation"}), 400

    # Check if concept already exists and update it
    for i, item in enumerate(memory):
        if item["concept"].lower() == concept.lower():
            memory[i]["explanation"] = explanation
            memory[i]["type"] = item_type
            save_memory(memory)
            return jsonify({"message": f"Updated {item_type} '{concept}'"}), 200

    # Add new concept or fact
    memory.append({"concept": concept, "explanation": explanation, "type": item_type})
    save_memory(memory)
    return jsonify({"message": f"Learned new {item_type} '{concept}'"}), 200

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
            max_tokens=200,
            temperature=0.3  # Lower temperature for more consistent cautious behavior
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/memory', methods=['GET'])
def get_memory():
    return jsonify({"memory": memory}), 200

@app.route('/delete', methods=['POST'])
def delete_item():
    global memory
    data = request.json
    concept = data.get("concept")
    
    if not concept:
        return jsonify({"error": "Missing concept name"}), 400
    
    # Find and remove the item
    for i, item in enumerate(memory):
        if item["concept"].lower() == concept.lower():
            deleted_item = memory.pop(i)
            save_memory(memory)
            item_type = deleted_item.get("type", "concept")
            return jsonify({"success": True, "message": f"Deleted {item_type} '{deleted_item['concept']}'"}), 200
    
    return jsonify({"error": f"Item '{concept}' not found"}), 404

@app.route('/clear', methods=['POST'])
def clear_memory():
    global memory
    memory = []
    save_memory(memory)
    return jsonify({"message": "Memory cleared successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')