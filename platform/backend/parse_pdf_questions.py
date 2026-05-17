import PyPDF2
import re
import json
import os
from supabase import create_client, Client

SUPABASE_URL = "https://druruykbefdlbmbvrglb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRydXJ1eWtiZWZkbGJtYnZyZ2xiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NjI3ODAsImV4cCI6MjA5NDUzODc4MH0.GIMvJQ4_w5G3WjEvaOZGLvX122iT78H1HfaWtsQMqWw"

dir_path = "/home/reet/jee/jee question/"

def parse_questions_from_file(file_path):
    print(f"Parsing file: {file_path}")
    try:
        reader = PyPDF2.PdfReader(file_path)
        text = ""
        for i in range(min(10, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
            
        pattern = r"Q\.(\d+)\s+(.*?)\s+\(1\)\s+(.*?)\s+\(2\)\s+(.*?)\s+\(3\)\s+(.*?)\s+\(4\)\s+(.*?)\s+Ans\.\s+\[(\d+)\]"
        
        matches = re.finditer(pattern, text, re.DOTALL)
        
        questions = []
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            opt1 = match.group(3).strip()
            opt2 = match.group(4).strip()
            opt3 = match.group(5).strip()
            opt4 = match.group(6).strip()
            ans = match.group(7)
            
            questions.append({
                "text": q_text,
                "options": [opt1, opt2, opt3, opt4],
                "correct_answer": str(int(ans) - 1),
                "chapter": "General Physics",
                "topic": "Misc"
            })
            
        print(f"Extracted {len(questions)} questions from {os.path.basename(file_path)}")
        return questions
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def insert_questions(questions):
    print("Connecting to Supabase API...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    supabase_data = []
    for q in questions:
        content = json.dumps({
            "text": q["text"],
            "options": q["options"]
        })
        supabase_data.append({
            "content": content,
            "correct_answer": q["correct_answer"],
            "chapter": q["chapter"],
            "topic": q["topic"],
            "subject": "Physics"
        })
        
    try:
        # Insert in chunks of 100 to be safe
        chunk_size = 100
        count = 0
        for i in range(0, len(supabase_data), chunk_size):
            chunk = supabase_data[i:i+chunk_size]
            response = supabase.table('questions').insert(chunk).execute()
            count += len(chunk)
            print(f"Inserted {count}/{len(supabase_data)} questions...")
            
        print(f"Successfully inserted {count} questions into Supabase Cloud.")
    except Exception as e:
        print(f"Error inserting questions via API: {e}")

if __name__ == "__main__":
    all_questions = []
    
    files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
    print(f"Found {len(files)} PDF files.")
    
    for file in files:
        file_path = os.path.join(dir_path, file)
        questions = parse_questions_from_file(file_path)
        all_questions.extend(questions)
        
    print(f"Total questions extracted: {len(all_questions)}")
    
    if len(all_questions) > 0:
        insert_questions(all_questions)
