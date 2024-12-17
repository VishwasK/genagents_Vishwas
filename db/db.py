
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
    
    query = "SELECT * FROM agents WHERE 1=1"
    params = []
    
    if 'age' in criteria:
        query += " AND age = %s"
        params.append(criteria['age'])
    if 'sex' in criteria:
        query += " AND sex = %s"
        params.append(criteria['sex'])
    if 'race' in criteria:
        query += " AND race = %s"
        params.append(criteria['race'])
    if 'religion' in criteria:
        query += " AND religion = %s"
        params.append(criteria['religion'])
    
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
