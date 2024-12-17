
import os
import json
import psycopg2
from psycopg2.extras import Json
from pathlib import Path

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def import_agents():
    conn = get_db_connection()
    cur = conn.cursor()
    
    base_path = Path(__file__).parent.parent / 'agent_bank/populations/gss_agents'
    
    for agent_dir in base_path.iterdir():
        if agent_dir.is_dir():
            meta_file = agent_dir / 'meta.json'
            scratch_file = agent_dir / 'scratch.json'
            
            if meta_file.exists() and scratch_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                with open(scratch_file) as f:
                    data = json.load(f)
                
                cur.execute("""
                    INSERT INTO agents (id, first_name, last_name, age, sex, 
                                      ethnicity, race, political_views, education,
                                      occupation, religion, city, state, data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                    data = EXCLUDED.data
                """, (
                    meta['id'],
                    data.get('first_name'),
                    data.get('last_name'), 
                    data.get('age'),
                    data.get('sex'),
                    data.get('ethnicity'),
                    data.get('race'),
                    data.get('political_views'),
                    data.get('highest_degree_received'),
                    data.get('work_status'),
                    data.get('religion'),
                    data.get('city'),
                    data.get('state'),
                    Json(data)
                ))
    
    conn.commit()
    cur.close()
    conn.close()

def search_agents(**criteria):
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT id, first_name, last_name, age, sex, race, occupation, religion, data FROM agents WHERE 1=1"
    params = []
    
    if 'age' in criteria:
        query += " AND age = %s"
        params.append(int(criteria['age']))
    if 'sex' in criteria:
        query += " AND LOWER(sex) = LOWER(%s)"
        params.append(str(criteria['sex']))
    if 'race' in criteria:
        query += " AND LOWER(race) = LOWER(%s)"
        params.append(str(criteria['race']))
    if 'religion' in criteria:
        query += " AND LOWER(religion) = LOWER(%s)"
        params.append(str(criteria['religion']))
    if 'occupation' in criteria:
        query += " AND LOWER(occupation) = LOWER(%s)"
        params.append(str(criteria['occupation']))
        
    cur.execute(query, params)
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results

def search_agents_dialogue(age=None, sex=None, race=None, religion=None, occupation=None):
    criteria = {}
    if age:
        criteria['age'] = age
    if sex:
        criteria['sex'] = sex
    if race:
        criteria['race'] = race  
    if religion:
        criteria['religion'] = religion
    if occupation:
        criteria['occupation'] = occupation
    return search_agents(**criteria)
