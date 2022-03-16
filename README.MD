Stonks is a very simple data aggregator that gets you daily, weekly, and monthly stock information.

In order to run this program what you need to do is first clone the program onto your local machine either through ssh or by manually downloading all the files.

From there do the following steps:
    
    1. CD into your stonks directory
    
    2. Run the following commands to get the database set up:
        cd backend
        python3 db.py
    
    3. After you run the top command, your database should be set up and ready to be used by the web app, now start up the server by running the following command in the same  directory you are in
        uvicorn server:app --reload

    4. Finally open up a new terminal window, cd into stonks directory and run the following commands to get the frontend to start running
        cd web
        npm start

That's it! The app should be up and running now with no issues!
