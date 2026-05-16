import pandas as pd
from database import engine
import models
from sqlalchemy.orm import Session
import datetime

# Find user
try:
    users = pd.read_sql('select id, email from auth.users', engine)
    print("Users found:")
    print(users)
    
    if len(users) > 0:
        user_id = str(users.iloc[0]['id'])
        print(f"Using user_id: {user_id}")
        
        session = Session(bind=engine)
        
        # Create Test if not exists
        test = session.query(models.Test).filter(models.Test.id == 1).first()
        if not test:
            test = models.Test(
                id=1,
                title="JEE Physics Mock Test",
                test_type="Mock",
                duration_minutes=180
            )
            session.add(test)
            session.commit()
            print("Created test with ID 1.")
            
        # Create dummy attempt
        attempt = models.TestAttempt(
            user_id=user_id,
            test_id=1,
            score=75,
            status='Completed',
            start_time=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            end_time=datetime.datetime.utcnow() - datetime.timedelta(hours=23)
        )
        session.add(attempt)
        
        # Create another one
        attempt2 = models.TestAttempt(
            user_id=user_id,
            test_id=1,
            score=85,
            status='Completed',
            start_time=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
            end_time=datetime.datetime.utcnow() - datetime.timedelta(hours=4)
        )
        session.add(attempt2)
        
        session.commit()
        print("Successfully created 2 dummy attempts.")
        session.close()
    else:
        print("No users found in auth.users.")
except Exception as e:
    print(f"Error: {e}")
