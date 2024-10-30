from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Optional
import sqlite3
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model globally
print("Loading model...")
base_model_id = "meta-llama/Llama-3.2-1B-Instruct"
adapter_path = "../sql-assistant-final"

tokenizer = AutoTokenizer.from_pretrained(base_model_id)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="auto",
    torch_dtype=torch.float16,
)
model = PeftModel.from_pretrained(model, adapter_path)
print("Model loaded!")

class Query(BaseModel):
    question: str

class SQLQuery(BaseModel):
    query: str

def generate_sql(question: str) -> str:
    prompt = f"""<s>[INST] <<SYS>>
You are a helpful SQL assistant. Convert the following question to SQL.
<</SYS>>

Question: {question}

Write the SQL query to answer this question. [/INST]
"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True,
        top_p=0.95,
        top_k=50,
        repetition_penalty=1.1
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    try:
        response = response.split("[/INST]")[1].strip()
    except:
        response = response
    
    return response

def execute_sql_query(query: str) -> list:
    try:
        conn = sqlite3.connect('sample.db')
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert results to list of dicts
        return [dict(zip(columns, row)) for row in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query")
async def process_query(query: Query):
    try:
        sql_query = generate_sql(query.question)
        return {"sql_query": sql_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-query")
async def execute_query(query: SQLQuery):
    try:
        results = execute_sql_query(query.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 