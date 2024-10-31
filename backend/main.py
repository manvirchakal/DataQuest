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
adapter_path = "../sql-assistant-final-verbose-prompts"

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

1. Projects
   - project_id: INTEGER PRIMARY KEY
   - name: TEXT NOT NULL
   - department: TEXT NOT NULL
   - budget: INTEGER NOT NULL

2. Teams
   - team_id: INTEGER PRIMARY KEY
   - name: TEXT NOT NULL

3. Students
   - student_id: INTEGER PRIMARY KEY
   - name: TEXT NOT NULL
   - team_id: INTEGER NOT NULL (references Teams.team_id)
   - project_id: INTEGER (references Projects.project_id)
   - grade: FLOAT DEFAULT 0.0
   - enrollment_date: DATE NOT NULL

4. TimeEntries
   - entry_id: INTEGER PRIMARY KEY
   - student_id: INTEGER NOT NULL (references Students.student_id)
   - hours: INTEGER NOT NULL
   - task_date: DATE NOT NULL
   - task_type: TEXT NOT NULL
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
        base_prompt = f"""[INST]

Write one SQL query for this question: {question}

CRITICAL: Output only the SQL query.
[/INST]"""

    inputs = tokenizer(base_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        temperature=0.1,
        do_sample=True,
        num_return_sequences=1,
        repetition_penalty=1.2,
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