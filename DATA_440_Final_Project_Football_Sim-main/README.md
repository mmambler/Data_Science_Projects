# Gridiron Guru: Offensive Playcalling Simulator

The Gridiron Guru: Offensive Playcalling Simulator gives you the opportunity to take on the role of an NFL Offensive Coordinator, making decisions that affect the number of yards you gain, how many points you score, and whether or not your team wins a game against a realistic NFL defense. On each play you are given the choice to either run, pass, punt, or kick a field goal, and based on what you choose an outcome will be generated from real-world NFL play distributions and probabilities. Think you have what it takes? Visit the link below to test out the simulator yourself and strive for dominance on the NFL gridiron!

## Streamlit Link:
To play the game and test out the simulation yourself, visit the following link:
https://gridiron-guru-football-sim.streamlit.app

## Data Source:
- Pro Football Focus (PFF) Ultimate
- Passing and Rushing Data Feeds
- NFL play-by-play data from 2013-2022
- SQLite database generated in football_db.py
- the SQLite database, .csv files, and an ERD are located in the 'data' folder

## Simulator Features
- Choose whether to kick or receive to start the game
- Buttons with the following choices: rush, pass, punt, try a field goal
- After each choice the field position and line to gain are updated, as well as the game state
- Each play results in a random clock runoff
- If the drive results in points, the score is updated and displayed in the header
- Failure comes with consequences in the way of improved likelihood of the CPU scoring after turnovers or missed kicks
- Playcalling decisions also come with the chance of interceptions, sacks, fumbles, incompletions, etc.
- After halftime, depending whether the user chose kick or receive to start, the opposite will occur
- At game end, the final score will be decided and a winner declared
- A restart button is displayed in the header that allows the user to begin a new game whenever they so choose

## A Note on Calculations
For the yards gained on a given run/pass play, a real-world outcome is sampled from all plays of the same type under the same down and distance from NFL games during the 2013 to 2022 seasons. Any other generated game results such as turnovers, incompletions, made field goals, CPU scoring, etc. are based on league-average probabilities for each individual event. These calculations were put in place in an attempt to make the outcomes as realistic as possible.

## Limitation Warning
Due to Streamlits inherent limitations, continuing to repetitively press buttons as the the app is calculating an initial button press can cause the entire streamlit app to crash/get stuck in a running state. This will break the simulator and require it to be redeployed. Should this ever happen, please reach out to the developer at mmambler@wm.edu to resolve this issue.
