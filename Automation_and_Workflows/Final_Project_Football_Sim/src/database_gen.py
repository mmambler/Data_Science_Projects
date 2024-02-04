from __future__ import annotations

import sqlite3
import pandas as pd
import numpy as np
from Pre_Processing import pre_processing as PP
import sql_queries as SQ
from traceback import print_exc as pe
from IPython.display import clear_output
import time

sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))

class DB():
    '''
    This is a class for accessing and building a SQLite database of FCS play-by-play data from Pro Football Focus (PFF).

    If accessing database, class only requires the name of the database (provided the db is in the working directory).
    '''
    
    def __init__(self,
                 name: str,
                 path: str = None,
                 input_lim: int = None,
                 add_data: bool = False,
                 table_type: str = None,
                 g_drop: bool = False,
                 any_drop: bool = False
                ):
      
      self.__path = path
      self.__name = name
      self.__add_data = add_data
      self.__table_type = table_type
      self.__g_drop = g_drop
      self.__any_drop = any_drop
      self.__input_lim = input_lim
      
      self.__validate_inputs()
      
      if self.__any_drop:
        self.__build_tables()
        self.__fill_tables()
      elif self.__add_data:
        self.__fill_tables()
        return
      else:
        return
      
    def __validate_inputs(self):
        '''
        Validates a number of the inputs passed to the class to ensure they will not cause errors.
        '''
        print('Validating Inputs...')

        if (self.__add_data is False) and (self.__table_type is not None):
            raise ValueError("'table_type' specified while 'add_data' is False")
      
        if (self.__add_data is True) and (self.__table_type is None):
            raise ValueError("Must specify 'table_type' while 'add_data' is True")
        
        if (self.__any_drop is False) and (self.__g_drop is True):
            raise ValueError("Can't drop games table while any_drop is set to False")
        
        clear_output(wait=True)
        print('Inputs Validated!')

        return
   
    def __load_df(self):
      '''
      Reads .csv file into a Pandas dataframe, and returns the dataframe.
      '''
      df = pd.read_csv(self.__path)
      return df
    
    def __connect(self):
        '''
        Connects to database under the name provided to the class.
        '''
        conn = sqlite3.connect(self.__name)
        curs = conn.cursor()

        curs.execute("PRAGMA foreign_keys=ON;")

        return conn, curs
    
    def __build_tables(self):
       '''
       Builds tables in the SQLite database for Games, Runs, Passes, and Run Concepts

       Conditional on drop conditions passed to the class.
       '''
       clear_output(wait=True)
       print('Building Tables...')

       conn, curs = self.__connect()
       curs.execute("PRAGMA foreign_keys=ON;")

       if self.__any_drop:
            if self.__g_drop == False:
                if self.__table_type.lower() == 'pass':
                        curs.execute("DROP TABLE IF EXISTS tPass;")
                if self.__table_type.lower() == 'rush':
                        curs.execute("DROP TABLE IF EXISTS tRunConcept;")
                        curs.execute("DROP TABLE IF EXISTS tRush;")
            if self.__g_drop:
                curs.execute("DROP TABLE IF EXISTS tPass;")
                curs.execute("DROP TABLE IF EXISTS tRunConcept;")
                curs.execute("DROP TABLE IF EXISTS tRush;")
                curs.execute("DROP TABLE IF EXISTS tGame;")
       
       if self.__g_drop:
            sql = SQ.SQL_G_BUILD
            curs.execute(sql)

       if self.__table_type.lower() == 'pass':
            sql = SQ.SQL_P_BUILD
            curs.execute(sql)

       if self.__table_type.lower() == 'rush':
            sql = SQ.SQL_R_BUILD
            curs.execute(sql)

            sql = SQ.SQL_RC_BUILD
            curs.execute(sql)

       conn.close()

       clear_output(wait=True)
       print('Tables Built!')

       return True
    
    def __preprocess(self):
        '''
        Removes plays with duplicate play IDs and utilizes Pre_Processing.py to prepare the data for entry into the database.
        '''
        df = self.__load_df()

        clear_output(wait=True)
        print('Checking for Duplicate Plays...')

        df.drop_duplicates(subset='play_id', keep=False, inplace=True)
        
        clear_output(wait=True)
        print('Any Duplicate Plays Removed!')

        clear_output(wait=True)
        print('Preprocessing Data...')
        
        df = df[df['yards'].notna()]

        Pre_Proc = PP()
        clean_df = Pre_Proc.pre_processing(data=df)

        clear_output(wait=True)
        print('Data Preprocessed!')

        if self.__input_lim == None:
            self.__input_lim = len(clean_df)

        return clean_df

    def __fill_tables(self):
        '''
        Fills the pre-built tables with the data frome the provided .csv file.

        For each row, the function checks if the play or game already exists in the database before adding it.
        '''
        import traceback
        conn, curs = self.__connect()

        df = self.__preprocess()

        row_input_lim = 0

        try:
            for i, row in enumerate(df.to_dict(orient='records')):
                if row_input_lim < self.__input_lim:
                    # Check if Game exists
                    x = pd.read_sql(SQ.SQL_CHECK_GAME, conn, params=row)
                    if len(x) == 0:
                        # Insert the record if it did not
                        curs.execute(SQ.SQL_INSERT_TGAME, row)
                    
                    if self.__table_type.lower() == 'pass':
                        # Check if Pass exists
                        x = pd.read_sql(SQ.SQL_CHECK_PASS, conn, params=row)
                        if len(x) == 0:
                            # Insert the record if it did not
                            curs.execute(SQ.SQL_INSERT_TPASS, row)
                            row_input_lim += 1
                        
                            clear_output(wait=True)
                            print('Filling Tables:', row_input_lim/self.__input_lim)

                    if self.__table_type.lower() == 'rush':
                        # Check if Rush exists
                        x = pd.read_sql(SQ.SQL_CHECK_RUSH, conn, params=row)
                        if len(x) == 0:
                            # Insert the record if it did not
                            curs.execute(SQ.SQL_INSERT_TRUSH, row)
                            row_input_lim += 1

                            clear_output(wait=True)
                            print('Filling Tables:', row_input_lim/self.__input_lim)

                        # Check if RunConcept exists
                        x = pd.read_sql(SQ.SQL_CHECK_RUNCONCEPT, conn, params=row)
                        if len(x) == 0:
                            # Insert the record if it did not
                            curs.execute(SQ.SQL_INSERT_TRUNCONCEPT, row)
                            

            conn.commit()

        except Exception:
            # Undo all changes since the last commit
            conn.rollback()
            print('Error at row:', i, '\n')
            print(row)
            # Print the exception information
            traceback.print_exc()

        conn.close()

        return

    def get_tPass(self):
        '''
        Returns the tPass table from the provided database as a Pandas dataframe
        '''
        conn, __ = self.__connect()

        sql = "SELECT * FROM tPass;"
        df = pd.read_sql(sql, conn)

        conn.close()
        return df
    
    def get_tGame(self):
        '''
        Returns the tGame table from the provided database as a Pandas dataframe
        '''
        conn, __ = self.__connect()

        sql = "SELECT * FROM tGame;"
        df = pd.read_sql(sql, conn)

        conn.close()
        return df
    
    def get_tRush(self):
        '''
        Returns the tRush table from the provided database as a Pandas dataframe
        '''
        conn, __ = self.__connect()

        sql = "SELECT * FROM tRush;"
        df = pd.read_sql(sql, conn)

        conn.close()
        return df
    
    def get_tRunConcept(self):
        '''
        Returns the tRunConcept table from the provided database as a Pandas dataframe
        '''
        conn, __ = self.__connect()

        sql = "SELECT * FROM tRunConcept;"
        df = pd.read_sql(sql, conn)

        conn.close()
        return df