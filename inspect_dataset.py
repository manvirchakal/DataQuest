from datasets import load_dataset

def inspect_spider_dataset():
    # Load the dataset
    dataset = load_dataset("xlangai/spider")
    
    # Get a few examples from the training set
    print("=== Dataset Info ===")
    print(dataset)
    print("\n=== Column Names ===")
    print(dataset['train'].column_names)
    
    # Print a few examples
    print("\n=== Sample Entries ===")
    for i in range(3):  # Show first 3 entries
        print(f"\nEntry {i+1}:")
        print("Question:", dataset['train'][i]['question'])
        print("Query:", dataset['train'][i]['query'])
        
        # Show the formatted version too
        formatted = f"""<s>[INST] <<SYS>>
You are a helpful SQL assistant. Convert the following question to SQL.
<</SYS>>

Question: {dataset['train'][i]['question']}

Write the SQL query to answer this question. [/INST]

{dataset['train'][i]['query']} </s>"""
        
        print("\nFormatted version:")
        print(formatted)
        print("\n" + "="*80)

if __name__ == "__main__":
    inspect_spider_dataset() 