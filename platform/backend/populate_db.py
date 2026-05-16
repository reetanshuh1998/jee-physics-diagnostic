from database import SessionLocal
import models

def populate():
    db = SessionLocal()
    
    # Check if questions already exist
    if db.query(models.Question).count() > 0:
        print("Database already has questions. Skipping population.")
        db.close()
        return

    questions = [
        {
            "subject": "Physics",
            "chapter": "Kinematics",
            "topic": "Circular Motion",
            "difficulty": "Medium",
            "content": "A particle is moving in a circle of radius R with constant speed v. The magnitude of average acceleration in half a revolution is:",
            "correct_answer": "1", # Index 1 (2v²/πR)
            "explanation": "Average acceleration = Change in velocity / Time. Change in velocity = 2v. Time = πR/v. So, average acceleration = 2v / (πR/v) = 2v²/πR.",
            "year": 2022
        },
        {
            "subject": "Physics",
            "chapter": "Properties of Matter",
            "topic": "Surface Tension",
            "difficulty": "Medium",
            "content": "The work done in blowing a soap bubble of surface tension T from radius R to 2R is:",
            "correct_answer": "1", # Index 1 (24πR²T)
            "explanation": "Work done = T * ΔA. Soap bubble has 2 surfaces. Initial area = 2 * 4πR² = 8πR². Final area = 2 * 4π(2R)² = 32πR². ΔA = 24πR². Work done = 24πR²T.",
            "year": 2021
        },
        {
            "subject": "Physics",
            "chapter": "Wave Optics",
            "topic": "Interference",
            "difficulty": "Easy",
            "content": "In a Young's double slit experiment, the slit separation is doubled and the distance between the slits and screen is halved. The fringe width becomes:",
            "correct_answer": "0", # Index 0 (one-fourth)
            "explanation": "Fringe width β = λD/d. New fringe width β' = λ(D/2)/(2d) = (1/4) * (λD/d) = β/4.",
            "year": 2023
        },
        {
            "subject": "Physics",
            "chapter": "Electrostatics",
            "topic": "Coulomb's Law",
            "difficulty": "Easy",
            "content": "Two point charges +3µC and +8µC repel each other with a force of 40 N. If a charge of -5µC is added to each of them, then the force between them will become:",
            "correct_answer": "2", # Index 2 (-10 N)
            "explanation": "Initial charges: 3µC and 8µC. Force = k*3*8/r² = 24k/r² = 40 N. New charges: (3-5)=-2µC and (8-5)=3µC. New Force = k*(-2)*3/r² = -6k/r² = -(1/4) * (24k/r²) = -10 N.",
            "year": 2020
        },
        {
            "subject": "Physics",
            "chapter": "Thermodynamics",
            "topic": "Carnot Engine",
            "difficulty": "Hard",
            "content": "A Carnot engine has an efficiency of 1/6. When the temperature of the sink is reduced by 62°C, its efficiency is doubled. The temperatures of the source and the sink are:",
            "correct_answer": "3", # Index 3 (99°C, 37°C)
            "explanation": "η = 1 - T2/T1 = 1/6 => T2/T1 = 5/6. New η' = 1 - (T2-62)/T1 = 1/3. => 1 - T2/T1 + 62/T1 = 1/3 => 1/6 + 62/T1 = 1/3 => 62/T1 = 1/6 => T1 = 372 K = 99°C. T2 = (5/6)*372 = 310 K = 37°C.",
            "year": 2019
        }
    ]

    import json
    
    options_map = {
        "Circular Motion": ["v²/R", "2v²/πR", "v²/2R", "2v²/R"],
        "Surface Tension": ["8πR²T", "24πR²T", "16πR²T", "12πR²T"],
        "Interference": ["one-fourth", "half", "double", "four times"],
        "Coulomb's Law": ["10 N", "20 N", "-10 N", "-20 N"],
        "Carnot Engine": ["99°C, 62°C", "124°C, 62°C", "37°C, 99°C", "99°C, 37°C"]
    }

    for q_data in questions:
        content_data = {
            "text": q_data["content"],
            "options": options_map[q_data["topic"]]
        }
        
        db_question = models.Question(
            subject=q_data["subject"],
            chapter=q_data["chapter"],
            topic=q_data["topic"],
            difficulty=q_data["difficulty"],
            content=json.dumps(content_data),
            correct_answer=q_data["correct_answer"],
            explanation=q_data["explanation"],
            year=q_data["year"]
        )
        db.add(db_question)
    
    db.commit()
    print(f"Successfully inserted {len(questions)} questions.")
    db.close()

if __name__ == "__main__":
    populate()
