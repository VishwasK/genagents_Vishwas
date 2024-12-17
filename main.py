
from flask import Flask, render_template, request, jsonify
import os
from simulation_engine.global_methods import *
from genagents.genagents import GenerativeAgent

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
            agent_path = "agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae"
            if not os.path.exists(f"{agent_path}/scratch.json"):
                return jsonify({"error": "Agent data not found"}), 404
            agent = GenerativeAgent(agent_path)
            print("Agent initialized successfully")
        
        message = request.json.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        history = request.json.get('history', [])
        try:
            response = agent.utterance(history + [["User", message]])
            if not response:
                return jsonify({"error": "No response generated"}), 500
            return jsonify({"response": response})
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return jsonify({"error": "Failed to generate response"}), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
