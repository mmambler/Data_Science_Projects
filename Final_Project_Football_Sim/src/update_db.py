from football_db import FootballDB

# Instantiate DB object
DB = FootballDB()

# Build tables (ONLY IF ON PURPOSE) and fill db from data in the 'unloaded' folder
#DB.build_tables(True)
DB.load_new_data()