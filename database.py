import sqlite3
from pathlib import Path
from datetime import datetime

#  database oath
db_path = Path("feedback.db")

def db_init():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        create table if not exists feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            review_text TEXT NOT NULL,
            is_likely BOOLEAN NOT NULL,
            confidence REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_feedback(review_text: str, is_likely: bool, confidence: float):
    """Save user feedback to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        insert into feedback (timestamp, review_text, is_likely, confidence)
        VALUES (?, ?, ?, ?)
        """,
        (datetime.utcnow().isoformat(), review_text, int(is_likely), confidence)
    )
    conn.commit()
    conn.close()
    print(f"Saved feedback: '{review_text[:4]}...' Likely: {is_likely}")

def get_all_feedback():
    """this will fetch all feedback for admin use."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("select * from feedback order by timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]  

# lets test our db
if __name__ == "__main__":
    db_init()
    save_feedback("This service is amazing!", is_likely=True, confidence=0.95)
    save_feedback("Very disappointed.", is_likely=False, confidence=0.88)
    
    print("\nAll feedback in DB:")
    for fb in get_all_feedback():
        print(fb)