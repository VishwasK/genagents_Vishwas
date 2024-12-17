
from flask import Flask, render_template, request, jsonify
from genagents.genagents import GenerativeAgent
import os, json
import traceback

app = Flask(__name__)
agent = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_agents():
    data = request.get_json()
    age = data.get('age')
    sex = data.get('sex')
    race = data.get('race')
    
    results = []
    
    # Search in GSS agents directory
    gss_agents_dir = "agent_bank/populations/gss_agents"
    for agent_dir in os.listdir(gss_agents_dir):
        scratch_path = os.path.join(gss_agents_dir, agent_dir, "scratch.json")
        if os.path.exists(scratch_path):
            with open(scratch_path) as f:
                agent_data = json.load(f)
                if all([
                    not age or str(agent_data.get('age')) == str(age),
                    not sex or agent_data.get('sex', '').lower() == sex.lower(),
                    not race or agent_data.get('race', '').lower() == race.lower()
                ]):
                    meta_path = os.path.join(gss_agents_dir, agent_dir, "meta.json")
                    with open(meta_path) as mf:
                        meta = json.load(mf)
                        results.append({
                            'id': meta.get('id'),
                            'first_name': agent_data.get('first_name'),
                            'last_name': agent_data.get('last_name'),
                            'age': agent_data.get('age'),
                            'sex': agent_data.get('sex'),
                            'race': agent_data.get('race')
                        })
    
    # Search in single_agent directory
    single_agent_dir = "agent_bank/populations/single_agent"
    for agent_dir in os.listdir(single_agent_dir):
        scratch_path = os.path.join(single_agent_dir, agent_dir, "scratch.json")
        if os.path.exists(scratch_path):
            with open(scratch_path) as f:
                agent_data = json.load(f)
                if all([
                    not age or str(agent_data.get('age')) == str(age),
                    not sex or agent_data.get('sex', '').lower() == sex.lower(),
                    not race or agent_data.get('race', '').lower() == race.lower()
                ]):
                    results.append({
                        'id': agent_dir,
                        'first_name': agent_data.get('first_name'),
                        'last_name': agent_data.get('last_name'),
                        'age': agent_data.get('age'),
                        'sex': agent_data.get('sex'),
                        'race': agent_data.get('race')
                    })
    
    return jsonify(results)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        agent_id = data.get('agent_id', '01fd7d2a-0357-4c1b-9f3e-8eade2d537ae')
        
        global agent
        
        # Check in both directories
        agent_path = f"agent_bank/populations/single_agent/{agent_id}"
        if not os.path.exists(agent_path):
            agent_path = f"agent_bank/populations/gss_agents/{agent_id}"
            if not os.path.exists(agent_path):
                return jsonify({"error": f"Agent directory not found"}), 404

        if agent is None or getattr(agent, 'id', None) != agent_id:
            print("Initializing agent...")
            try:
                agent = GenerativeAgent(agent_path)
                print("Agent initialized successfully")
            except Exception as init_error:
                return jsonify({"error": f"Failed to initialize agent: {str(init_error)}"}), 500

        try:
            dialogue = [["User", message]]
            response = agent.utterance(dialogue, {})
            
            if isinstance(response, str):
                return jsonify({"response": response}), 200
            else:
                return jsonify({"response": "I apologize, but I'm having trouble understanding. Could you please rephrase?"}), 200
            
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
