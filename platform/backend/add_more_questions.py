import json
from database import engine, SessionLocal
import models

def add_questions():
    db = SessionLocal()
    
    questions_data = [
      {
        "subject": "Physics",
        "chapter": "Electrostatics",
        "topic": "Motion of a Charged Particle in an Electric Field",
        "difficulty": "Medium",
        "content": "An electron is made to enter symmetrically between two parallel and equally but oppositely charged metal plates, each of 10 cm length. The electron emerges out of the electric field region with a horizontal component of velocity $10^6$ m/s. If the magnitude of the electric field between the plates is 9.1 V/cm, then the vertical component of velocity of electron is (mass of electron $= 9.1 \\times 10^{-31}$ kg and charge of electron $= 1.6 \\times 10^{-19}$ C)",
        "options": ["0", "$1 \\times 10^6$ m/s", "$1.6 \\times 10^6$ m/s", "$1.6 \\times 10^4$ m/s"],
        "correct_answer": 2, # 'c'
        "year": 2025
      },
      {
        "subject": "Physics",
        "chapter": "Current Electricity",
        "topic": "Cells in Parallel",
        "difficulty": "Easy",
        "content": "Given below are two statements : Statement-I : The equivalent emf of two nonideal batteries connected in parallel is smaller than either of the two emfs. Statement-II : The equivalent internal resistance of two nonideal batteries connected in parallel is smaller than the internal resistance of either of the two batteries. In the light of the above statements, choose the correct answer from the options given below.",
        "options": ["Both Statement-I and Statement-II are false", "Statement-I is false but Statement-II is true", "Both Statement-I and Statement-II are true", "Statement-I is true but Statement-II is false"],
        "correct_answer": 1, # 'b'
        "year": 2025
      },
      {
        "subject": "Physics",
        "chapter": "Rotational Motion",
        "topic": "Moment of Inertia",
        "difficulty": "Medium",
        "content": "A uniform circular disc of radius 'R' and mass 'M' is rotating about an axis perpendicular to its plane and passing through its centre. A small circular part of radius R/2 is removed from the original disc as shown in the figure. Find the moment of inertia of the remaining part of the original disc about the axis as given above. (Figure shows a large disc of radius R with a smaller disc of radius R/2 removed, the smaller disc's center is R/2 from the center of the larger disc, along a radius).",
        "options": ["$\\frac{1}{2} MR^2$", "$\\frac{3}{8} MR^2$", "$\\frac{13}{32} MR^2$", "$\\frac{15}{32} MR^2$"],
        "correct_answer": 3, # 'd'
        "year": 2025
      },
      {
        "subject": "Physics",
        "chapter": "Thermodynamics",
        "topic": "Calorimetry",
        "difficulty": "Medium",
        "content": "An amount of ice of mass $10^{-3}$ kg and temperature -10°C is transformed to vapour of temperature 110°C by applying heat. The total amount of work required for this conversion is, (Take, specific heat of ice = $2100 Jkg^{-1} K^{-1}$, specific heat of water = $4180 Jkg^{-1} K^{-1}$, specific heat of steam = $1920 Jkg^{-1} K^{-1}$, Latent heat of ice = $3.35 \\times 10^5 Jkg^{-1}$ and Latent heat of steam = $2.25 \\times 10^6 Jkg^{-1}$)",
        "options": ["3043 J", "3024 J", "3003 J", "3022 J"],
        "correct_answer": 0, # 'a'
        "year": 2025
      },
      {
        "subject": "Physics",
        "chapter": "Dual Nature of Radiation and Matter",
        "topic": "De Broglie Wavelength",
        "difficulty": "Medium",
        "content": "An electron in the ground state of the hydrogen atom has the orbital radius of $5.3 \\times 10^{-11}$ m while that for the electron in third excited state is $8.48 \\times 10^{-10}$ m. The ratio of the de Broglie wavelengths of electron in the excited state to that in the ground state is",
        "options": ["3", "16", "9", "4"],
        "correct_answer": 3, # 'd'
        "year": 2025
      }
    ]

    for q in questions_data:
        content = json.dumps({
            "text": q["content"],
            "options": q["options"]
        })
        
        db_question = models.Question(
            subject=q["subject"],
            chapter=q["chapter"],
            topic=q["topic"],
            difficulty=q["difficulty"],
            content=content,
            correct_answer=str(q["correct_answer"]),
            year=q["year"]
        )
        db.add(db_question)
    
    db.commit()
    print(f"Successfully added {len(questions_data)} questions.")
    db.close()

if __name__ == "__main__":
    add_questions()
