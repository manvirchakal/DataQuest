from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import sqlite3
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
from peft import PeftModel

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and tokenizer
print("Loading model...")

base_model_id = "meta-llama/Llama-3.2-1B-Instruct"
adapter_path = "../sql-assistant-final"

# Load base model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="auto",
    torch_dtype=torch.float16,
)

# Add PEFT adapter loading
model = PeftModel.from_pretrained(model, adapter_path)
print("Model loaded!")

# Database schema
SCHEMA = """
TABLE STRUCTURES:

1. project
   - id: INTEGER PRIMARY KEY
   - name: TEXT (e.g., "AI Chatbot", "Data Analytics Platform")
   - description: TEXT
   - company: TEXT (e.g., "TechCorp", "DataCo")

2. student
   - sid: INTEGER PRIMARY KEY
   - team: INTEGER (1-8)
   - entry_count: INTEGER
   - total_time: FLOAT
   - team_rating: FLOAT (range: 0-5)
   - project: INTEGER → project.id
   - name: TEXT
   - phone_number: TEXT
   - email: TEXT

3. time_entry
   - id: INTEGER PRIMARY KEY
   - author: INTEGER → student.sid
   - time_spent: INTEGER (minutes)
   - comments: JSON {"Accomplished": "", "Roadblocks": "", "Plans": ""}
   - created: DATETIME
   - updated: DATETIME

4. faculty
   - fid: INTEGER PRIMARY KEY
   - team: INTEGER (1-8)
   - project: INTEGER → project.id
   - name: TEXT (e.g., "Dr. Alice Thompson")
   - phone_number: TEXT
   - email: TEXT

5. review_prompt
   - pid: INTEGER PRIMARY KEY
   - title: TEXT (e.g., "Technical Skills", "Communication")
   - prompt: TEXT
   - weight: FLOAT (range: 0-1)

6. peer_review
   - rid: INTEGER PRIMARY KEY
   - author: INTEGER → student.sid
   - recipient: INTEGER → student.sid
   - prompt: INTEGER → review_prompt.pid
   - comments: TEXT
   - created: DATETIME
   - updated: DATETIME
"""

class Query(BaseModel):
    question: str
    previous_error: Optional[str] = None
    previous_query: Optional[str] = None

def clean_response(response: str) -> str:
    try:
        print("Starting cleaning...")
        # Take everything after the last [/INST] tag
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
            if ";" in response:
                response = response.split(";")[0].strip() + ";"
            
        print(f"Cleaned response: {response}")
        return response
        
    except Exception as e:
        print(f"Error in clean_response: {str(e)}")
        return response.strip()

def generate_sql(question: str, previous_error: Optional[str] = None, previous_query: Optional[str] = None) -> str:
    if previous_error and previous_query:
        base_prompt = f"""[INST]Fix this SQL query:

Previous query: {previous_query}
Error: {previous_error}

CRITICAL: Output only the fixed SQL query.[/INST]"""
    else:
        base_prompt = f"""[INST]Write one SQL query for this question: {question}

Examples of good queries:
1. "List all students in team 3"
   SELECT name FROM student WHERE team = 3;

2. "Show all projects"
   SELECT name FROM project;

3. "Show students and their projects"
   SELECT s.name, p.name FROM student s JOIN project p ON s.project = p.id;

Schema:
{SCHEMA}

Important:
- Write exactly one SQL query
- End with semicolon
- Use lowercase keywords
- Use exact column names[/INST]"""

    inputs = tokenizer(base_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=1.5,
        do_sample=False,
        num_return_sequences=1,
        repetition_penalty=2.0,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Raw response: {response}")
    return response.split("[/INST]")[-1].strip()

@app.post("/query")
async def process_query(query: Query):
    try:
        sql_query = generate_sql(
            query.question,
            query.previous_error,
            query.previous_query
        )
        return {"sql_query": sql_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-query")
async def execute_query(query: dict):
    try:
        # Print query for debugging
        print(f"Executing query: {query['query']}")
        
        conn = sqlite3.connect('sample.db')
        cursor = conn.cursor()
        cursor.execute(query["query"])
        results = cursor.fetchall()
        conn.close()
        return {"results": results}
    except sqlite3.Error as e:
        print(f"SQLite error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"SQLite error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))