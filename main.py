
from flask import Flask, render_template, request, jsonify
from simulation_engine.global_methods import *
from genagents.genagents import GenerativeAgent

app = Flask(__name__)
agent = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global agent
    if agent is None:
        agent = GenerativeAgent("agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae")
    
    message = request.json.get('message')
    history = request.json.get('history', [])
    
    response = agent.utterance(history + [["User", message]])
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
