from flask import Flask, render_template, request, jsonify
import uuid
from genagents.genagents import GenerativeAgent
from genagents.modules.memory_stream import MemoryStream
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

@app.route('/create-agent', methods=['POST'])
def create_agent():
    try:
        data = request.get_json()
        agent_info = data.get('agent_info', {})
        
        agent_id = str(uuid.uuid4())
        agent_path = f"agent_bank/populations/single_agent/{agent_id}"
        os.makedirs(os.path.join(agent_path, "memory_stream"), exist_ok=True)
        
        # Create new agent without a folder first
        agent = GenerativeAgent()  # Initialize empty agent
        agent.update_scratch(agent_info)
        agent.save(agent_path)  # Save to create initial files
        
        return jsonify({"success": True, "agent_id": agent_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-memory', methods=['POST'])
def add_memory():
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        memory = data.get('memory')
        time_step = data.get('time_step', 1)
        
        # Check in both directories
        agent_path = f"agent_bank/populations/single_agent/{agent_id}"
        if not os.path.exists(agent_path):
            agent_path = f"agent_bank/populations/gss_agents/{agent_id}"
            if not os.path.exists(agent_path):
                return jsonify({"error": "Agent not found"}), 404
            
        # Create memory_stream directory if it doesn't exist
        os.makedirs(os.path.join(agent_path, "memory_stream"), exist_ok=True)
        
        try:
            agent = GenerativeAgent(agent_path)
            agent.remember(memory, time_step=time_step)
            agent.save(agent_path)
            return jsonify({"success": True}), 200
        except Exception as agent_error:
            print(f"Agent memory error: {str(agent_error)}")
            return jsonify({"error": f"Failed to add memory: {str(agent_error)}"}), 500
            
    except Exception as e:
        print(f"Memory addition error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/reflect', methods=['POST'])
def reflect():
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        anchor = data.get('anchor')
        time_step = data.get('time_step', 1)
        
        # Check in both directories
        agent_path = f"agent_bank/populations/single_agent/{agent_id}"
        if not os.path.exists(agent_path):
            agent_path = f"agent_bank/populations/gss_agents/{agent_id}"
            if not os.path.exists(agent_path):
                return jsonify({"error": "Agent not found"}), 404

        # Initialize agent first
        try:
            # Initialize with path directly
            agent = GenerativeAgent(agent_path)
            
            # Validate anchor text
            if not anchor or not isinstance(anchor, str):
                return jsonify({"error": "Invalid anchor text"}), 400
            
            # Generate reflection with proper error handling
            try:
                # Add reflection count parameter
                reflection_count = 1  # Generate one reflection at a time
                agent.memory_stream.reflect(anchor=anchor, reflection_count=reflection_count, time_step=time_step)
                
                # Get the most recent reflection
                reflections = [node for node in agent.memory_stream.seq_nodes if node.node_type == "reflection"]
                reflection_text = reflections[-1].content if reflections else "No reflection generated"
                agent.save(agent_path)
                return jsonify({"reflection": reflection_text}), 200
            except Exception as reflect_error:
                print(f"Reflection generation error: {str(reflect_error)}")
                return jsonify({"error": "Unable to generate reflection"}), 500
            
        except Exception as init_error:
            print(f"Agent initialization error: {str(init_error)}")
            return jsonify({"error": f"Failed to initialize agent: {str(init_error)}"}), 500
            
    except Exception as e:
        print(f"Reflection error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
                # Clean up JSON response if present
                if response.startswith('{"utterance":'):
                    try:
                        import json
                        response = json.loads(response)['utterance']
                    except:
                        pass
                return jsonify({"response": response.strip()}), 200
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