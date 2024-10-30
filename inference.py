import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def load_model():
    # Load base model and tokenizer
    base_model_id = "meta-llama/Llama-3.2-1B-Instruct"
    adapter_path = "./sql-assistant-final"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_id)
    
    # Load base model with same 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    
    # Load adapter weights
    model = PeftModel.from_pretrained(model, adapter_path)
    
    return model, tokenizer

def generate_sql(question, model, tokenizer):
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
    
    # Clean up the response
    try:
        # Remove the original prompt
        response = response.split("[/INST]")[1].strip()
        
        # Remove any remaining special tokens or markers
        response = response.split("</s>")[0].strip()
        response = response.split("</sql>")[0].strip()
        response = response.split("</INST>")[0].strip()
        
        # Remove any SQL or instruction markers
        response = response.replace("SQL:", "").strip()
        response = response.replace("Query:", "").strip()
        
    except:
        pass
        
    return response

def main():
    print("Loading model...")
    model, tokenizer = load_model()
    print("Model loaded! Ready for questions.")
    
    while True:
        # Get user input
        question = input("\nEnter your question (or 'quit' to exit): ")
        
        if question.lower() == 'quit':
            break
            
        try:
            # Generate SQL
            sql = generate_sql(question, model, tokenizer)
            print("\nGenerated SQL Query:")
            print("-" * 50)
            print(sql)
            print("-" * 50)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
