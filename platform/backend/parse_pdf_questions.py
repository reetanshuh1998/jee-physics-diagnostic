import PyPDF2
import re
import json
import os
from database import SessionLocal
import models

dir_path = "/home/reet/jee/jee question/"

def parse_questions_from_file(file_path):
    print(f"Parsing file: {file_path}")
    try:
        reader = PyPDF2.PdfReader(file_path)
        # Combine text from first 10 pages (likely to be Physics)
        text = ""
        for i in range(min(10, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
            
        # Regex pattern
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
                "chapter": "General Physics", # Default
                "topic": "Misc" # Default
            })
            
        print(f"Extracted {len(questions)} questions from {os.path.basename(file_path)}")
        return questions
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def insert_questions(questions):
    db = SessionLocal()
    try:
        count = 0
        for q in questions:
            content = json.dumps({
                "text": q["text"],
                "options": q["options"]
            })
            
            db_question = models.Question(
                content=content,
                correct_answer=q["correct_answer"],
                chapter=q["chapter"],
                topic=q["topic"]
            )
            db.add(db_question)
            count += 1
            
        db.commit()
        print(f"Successfully inserted {count} questions into database.")
        return count
    except Exception as e:
        db.rollback()
        print(f"Error inserting questions: {e}")
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    all_questions = []
    
    # Get all PDF files
    files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
    print(f"Found {len(files)} PDF files.")
    
    for file in files:
        file_path = os.path.join(dir_path, file)
        questions = parse_questions_from_file(file_path)
        all_questions.extend(questions)
        
    print(f"Total questions extracted: {len(all_questions)}")
    
    if len(all_questions) > 0:
        insert_questions(all_questions)
