
from flask import Flask, render_template, request, jsonify
from genagents.genagents import GenerativeAgent
import os

app = Flask(__name__)
agent = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        global agent
        if agent is None:
            print("Initializing agent...")
            # Using the example agent provided in the repository
            agent_path = "agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae"
            
            if not os.path.exists(agent_path):
                return jsonify({"error": "Agent directory not found"}), 404
                
            if not os.path.exists(f"{agent_path}/scratch.json"):
                return jsonify({"error": "Agent data not found"}), 404
                
            agent = GenerativeAgent(agent_path)
            print("Agent initialized successfully")

        message = request.json.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Simple dialogue format as per documentation
        dialogue = [["User", message]]
        response = agent.utterance(dialogue)
        print(f"Received response: {response}")

        return jsonify({"response": response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
