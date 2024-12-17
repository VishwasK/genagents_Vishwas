
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
            agent_path = "agent_bank/populations/single_agent/software_engineer"
            
            if not os.path.exists(agent_path):
                return jsonify({"error": f"Agent directory not found at {agent_path}"}), 404
                
            if not os.path.exists(f"{agent_path}/scratch.json"):
                return jsonify({"error": f"Agent data (scratch.json) not found in {agent_path}"}), 404
                
            try:
                agent = GenerativeAgent(agent_path)
                print("Agent initialized successfully")
            except Exception as init_error:
                return jsonify({"error": f"Failed to initialize agent: {str(init_error)}"}), 500

        message = request.json.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400

        try:
            dialogue = [["User", message]]
            response = agent.utterance(dialogue)
            
            if not isinstance(response, str):
                return jsonify({"error": "Invalid response format from agent"}), 500
                
            return jsonify({"response": response})
            
        except Exception as dialogue_error:
            return jsonify({"error": f"Failed to process dialogue: {str(dialogue_error)}"}), 500
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
