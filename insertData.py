from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Wordlewords  # Import Wordlewords database model

# This python file will have the ability to purge the db to only have the bare bones of what we need in the database.
# We should also add more 'table purges', so we don't have unnecessary data in the database.


engine = create_engine('sqlite:///instance/messages.db')
Session = sessionmaker(bind=engine)

# Clear existing data from the Wordlewords table
with Session() as session:
    session.query(Wordlewords).delete()
    session.commit()

# Read the text file
with open('data\\wordleValidWords.txt', 'r') as file:
    words = [line.strip() for line in file]

# Insert each word into the table
with Session() as session:
    for word in words:
        new_word = Wordlewords(word=word)
        session.add(new_word)
    session.commit()