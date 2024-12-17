from flask import Flask, render_template, request, jsonify
from genagents.genagents import GenerativeAgent
import os
import traceback

app = Flask(__name__)
agent = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        agent_id = data.get('agent_id', '01fd7d2a-0357-4c1b-9f3e-8eade2d537ae')
        
        global agent
        print("Initializing agent...")
        agent_path = f"agent_bank/populations/single_agent/{agent_id}"
            
        if not os.path.exists(agent_path):
            return jsonify({"error": f"Agent directory not found at {agent_path}"}), 404
                
        try:
            agent = GenerativeAgent(agent_path)
            print("Agent initialized successfully")
        except Exception as init_error:
            return jsonify({"error": f"Failed to initialize agent: {str(init_error)}"}), 500

        try:
            dialogue = [["User", message]]
            response = agent.utterance(dialogue)
            
            if not response:
                return jsonify({"response": "I apologize, but I'm having trouble understanding. Could you please rephrase?"}), 200
                
            return jsonify({"response": response})
            
        except Exception as dialogue_error:
            print(f"Dialogue error: {str(dialogue_error)}")
            return jsonify({"response": "I apologize, but I'm having trouble processing your request right now."}), 200
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)