# IMPORTANT
We have noticed issues with installing dependencies.
With `Flask-Reuploaded` it installs it's files as `Flask-uploads`, which is a different Flask package. So if you are having issues with: `from flask_uploads import UploadSet, configure_uploads, IMAGES`.
MAKE SURE YOU `pip uninstall Flask-Uploads` and then `pip install Flask-Reuploaded`.

# Description of Application
<b>Applications Description Given to Users:</b>
    ```Riddler's RabbitHole is an engaging and interactive game forum designed to hold a community of puzzle enthusiasts. The platform allows users to create and participate in forum games centered around hints provided in the form of text and images. Each game allows users to solve riddles, puzzles, and challenges by interpreting these clues.
    The primary purpose of Riddler's RabbitHole is to create a collaborative and fun environment where users can both challenge themselves and enjoy the shared hobby. By enabling comments on individual posts, the application encourages communication and discussion among users, enriching the puzzle-solving experience. Even after a post has been marked as solved, users can continue to participate, ensuring that the forum remains dynamic and inclusive. 
    This focus on community interaction and ongoing engagement sets Riddler's RabbitHole apart from other puzzle and riddle platforms. It is not just a place to solve puzzles but a space where users can connect, share insights, and build lasting friendships over a common love for games and challenges.```

<b>Design:</b>
    The design of Riddler's RabbitHole prioritizes simplicity and ease of use, ensuring an enjoyable experience for all users. We have created the interface to include only four essential pages once a User has logged in:

    Leaderboard Page:
        This page displays the rankings of users based on their success in solving puzzles. It creates competition and motivation for users to engage more with the community.

    Display Posts Page:
        Here, users can browse through all the forum games and puzzles posted by the community. The layout is designed for easy navigation, allowing users to quickly find and select puzzles.

    Create Post Page:
        This page enables users to create their own puzzle posts. The interface is user-friendly, guiding them through the process of adding text and image hints, making it simple to contribute new challenges to the forum.

    Post Page:
        When a user selects a puzzle, they are directed to the Post Page. This page displays the puzzle details, including the hints provided. Users can submit their guesses, view others' comments, and participate in discussions, creating a collaborative puzzle-solving experience.

The design of Riddler's RabbitHole focuses on enhancing user experience through simplicity, encouraging participation, and building a community of puzzle enthusiasts.

# Update dependencies to installation file
`pip freeze > requirements.txt`  

# Quick installation
Install python and run the following command
`pip install -r ./requirements.txt`

Packages need from pip:  
Flask			3.0.2  
Flask-Login		0.6.3  
Flask-SQLAlchemy	3.1.1  
SQLAlchemy		2.0.29  
Flask-Session     0.8.0  
Flask-SocketIO     5.3.6  
Flask-SocketIO     5.3.6  
Flask-Reuploaded   1.4.0  

# Getting started
run the following command
`python ./app.py`
and go to:
http://localhost:5000


# Viewing DB
 1. cmd into ./instance/
 2. 'sqlite3 (name of db).db'
 3. '.tables' for list of tables
 4. 'SELECT * FROM (table name);'
