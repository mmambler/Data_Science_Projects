
from __future__ import annotations

import streamlit as st
import numpy as np
import random
from src.football_viz import FBField
from src.football_db import FootballDB
import src.dropdown_lists as dropdown

class FBApp:

    def __init__(self):

        self.field = FBField()
        self.db = FootballDB()

        self.initialize_session_state()
        self.load_tables_from_db()
        self.build_page()
        self.streamlit_defaults()
        return
    
    def build_page(self):
        
        # Diplay title & author credit
        st.header("Gridiron Guru: Offensive Playcalling Simulator")
        _,_,col,_,_ = st.columns(5)
        with col:
            st.write('By: Mac Ambler')

        st.write('')

        # Display all necessary game state information
        col1, col2, col3 = st.columns(3)
        with col1:
            # display user score
            st.subheader('USER: ' + str(st.session_state.USER_SCORE))
        with col2:
            # display play clock
            if (st.session_state.PREV_QUART == 2) and (st.session_state.QUARTER == 3):
                st.subheader('Play Clock: 15:00')
            elif st.session_state.QUARTER <= 4:
                st.subheader('Play Clock: ' + str(st.session_state.MINUTES) + ':' + f"{st.session_state.SECONDS:02}")
            else:
                st.subheader('Play Clock: 0:00')
        with col3:
            # display cpu score
            col_1, col_2 = st.columns(2)
            with col_2:
                st.subheader('CPU: ' + str(st.session_state.CPU_SCORE))

        col1, col2, col3 = st.columns(3)
        with col1:
            # display button to restart the game
            st.button('RESTART GAME', on_click=self.reset_game)
        with col2:
            # diplay quarter
            if st.session_state.QUARTER <= 4:
                st.subheader('Quarter: ' + str(st.session_state.QUARTER))
            else:
                st.subheader('FINAL')
        with col3:
            col_1, col_2 = st.columns(2)
            with col_2:
                # display down and distance
                if st.session_state.DOWN == 1:
                    st.subheader(str(st.session_state.DOWN) + 'st & ' + str(st.session_state.DISTANCE))
                elif st.session_state.DOWN == 2:
                    st.subheader(str(st.session_state.DOWN) + 'nd & ' + str(st.session_state.DISTANCE))
                elif st.session_state.DOWN == 3:
                    st.subheader(str(st.session_state.DOWN) + 'rd & ' + str(st.session_state.DISTANCE))
                elif st.session_state.DOWN == 4:
                    st.subheader(str(st.session_state.DOWN) + 'th & ' + str(st.session_state.DISTANCE))
        
        # generate field visualization from football_viz.py
        self.field = FBField(hash = st.session_state.HASH, 
                             field_pos=st.session_state.FIELD_POS, 
                             distance=st.session_state.DISTANCE)
        
        # diplay field visualization
        st.pyplot(self.field.fig)

        st.write('')

        # display drive results as centered as possible under streamlit's limitations
        if st.session_state.RESULT == 'TOUCHDOWN!':
            _,col,_ = st.columns([2.4,3,1])
            with col:
                if st.session_state.RESULT != '':
                    st.subheader(st.session_state.RESULT)
        else:
            if st.session_state.RESULT != '':
                if (st.session_state.RESULT == 'FG MISSED') or (st.session_state.RESULT == 'FG IS GOOD!'):
                    _,col,_ = st.columns([2.7,3,1])
                    with col:
                        st.subheader(st.session_state.RESULT)
                elif st.session_state.RESULT == 'FUMBLE':
                    _,col,_ = st.columns([2.9,3,1])
                    with col:
                        st.subheader(st.session_state.RESULT)
                elif st.session_state.RESULT == 'INTERCEPTION':
                    _,col,_ = st.columns([2.3,3,1])
                    with col:
                        st.subheader(st.session_state.RESULT)
                else:
                    _,col,_ = st.columns([1.7,3,1])
                    with col:
                        st.subheader(st.session_state.RESULT)

        st.write('')

        # if it is the start of the game, display buttons to choose whether to kick or receive first
        if st.session_state.GAME_START:
            _,_,_,col1, col2,_,_,_ = st.columns([1,1,1,1,1.5,1,1,1])
            with col1:
                if st.button('KICK'):
                    self.reset_drive_adv()
                    st.session_state.GAME_START = False
                    st.session_state.RECEIVE_BOOL = False
                    st.rerun()
            with col2:
                if st.button('RECEIVE'):
                    st.session_state.GAME_START = False
                    st.session_state.RECEIVE_BOOL = True
                    st.rerun()

        # if not start of game
        else:
            # check if it's halftime
            if (st.session_state.PREV_QUART == 2) and (st.session_state.QUARTER == 3):

                st.session_state.PREV_QUART = 3
                st.session_state.MINUTES = 15
                st.session_state.SECONDS = 0
                st.session_state.DOWN = 1
                st.session_state.DISTANCE = 10
                st.session_state.FIELD_POS = -25

                _,col,_ = st.columns([2.5,3,1])
                with col:
                    # display that its halftime
                    st.subheader('HALFTIME')
                _,_,_,col,_,_,_ = st.columns(7)
                with col:
                    # display button to start 2nd half
                    if st.button('Begin 2nd Half'):
                        if st.session_state.RECEIVE_BOOL:
                            self.reset_drive_adv()
                            st.session_state.RESULT = ''
                            st.rerun()
                        else:
                            st.session_state.RESULT = ''
                            st.rerun()
            
            # if not halftime or beginning of game, display playcall choices
            else:
                if st.session_state.QUARTER <= 4:
                    self.display_playcall_choices()
                
                # if end of the game
                else:
                    #display final score
                    _,col,_ = st.columns([1.4,3,1])
                    with col:
                        st.subheader('Final Score - User: ' + str(st.session_state.USER_SCORE) + '    CPU: ' + str(st.session_state.CPU_SCORE))

                    # display result of the game
                    _,_,col,_,_ = st.columns(5)
                    with col:
                        if st.session_state.USER_SCORE > st.session_state.CPU_SCORE:
                            st.subheader('YOU WIN!')
                        elif st.session_state.USER_SCORE == st.session_state.CPU_SCORE:
                            st.subheader('YOU TIE!')
                        else:
                            st.subheader('YOU LOSE')

        return
    
    def display_playcall_choices(self):
        '''
        Displays the buttons necessary for calling a play and executes the necessary functions associated with each
        '''

        # if not at end of drive, present buttons for making a playcall
        if (st.session_state.RESULT not in dropdown.drive_end_list_adv) & (st.session_state.RESULT not in dropdown.drive_end_list_disadv):
            _,_,_,col1, col2,_,_,_ = st.columns(8)
            with col1:
                rush_button = st.button('RUSH', on_click=self.rush_master_update)
            with col2:
                pass_button = st.button('PASS', on_click=self.pass_master_update)
                    
            _,_,_,col1, col2,_,_,_ = st.columns(8)
            with col1:
                punt_button = st.button('PUNT', on_click=self.punt_update)
            with col2:
                FG_button = st.button('TRY FG', on_click=self.fg_update)
                
        # if drive ended neutral/advantageously, present advantageous cpu sim button 
        if st.session_state.RESULT in dropdown.drive_end_list_adv:
            _,_,_,col,_,_,_ = st.columns(7)
            with col:
                sim_drive_button = st.button('Sim CPU Drive', on_click=self.reset_drive_adv)
        
        # if drive ended disadvantageously, present disadvantageous cpu sim button 
        if st.session_state.RESULT in dropdown.drive_end_list_disadv:
            _,_,_,col,_,_,_ = st.columns(7)
            with col:
                sim_drive_button = st.button('Sim CPU Drive', on_click=self.reset_drive_disadv)

        return
    
    def reset_game(self):
        '''
        Resets the game to the initial state
        '''

        st.session_state.MINUTES = 15
        st.session_state.SECONDS = 0
        st.session_state.USER_SCORE = 0
        st.session_state.CPU_SCORE = 0
        st.session_state.QUARTER = 1
        st.session_state.DOWN = 1
        st.session_state.DISTANCE = 10
        st.session_state.FIELD_POS = -25
        st.session_state.RESULT = ''
        st.session_state.GAME_START = True
        st.session_state.PREV_QUART = 1
        st.session_state.RECEIVE_BOOL = False
    
        return
    
    def reset_drive_adv(self):
        '''
        Resets the drive after advantageous or neutral outcome (TD, FG, Punt)
        '''

        # CPU drive clock runoff
        runoff = -1*int(round(np.random.normal(180,30), 0))
        temp_sec = st.session_state.SECONDS + runoff
        if temp_sec < 0:
            while (st.session_state.MINUTES > 0) and (temp_sec < 0):
                st.session_state.MINUTES = st.session_state.MINUTES-1
                st.session_state.SECONDS = 60 + temp_sec
                temp_sec += 60
            while (st.session_state.MINUTES == 0) and (temp_sec < 0):
                st.session_state.MINUTES = 15
                st.session_state.SECONDS = 0
                st.session_state.PREV_QUART = st.session_state.QUARTER
                st.session_state.QUARTER += 1
                while (st.session_state.MINUTES > 0) and (temp_sec < 0):
                    st.session_state.MINUTES = st.session_state.MINUTES-1
                    st.session_state.SECONDS = 60 + temp_sec
                    temp_sec += 60
        else:
            st.session_state.SECONDS = temp_sec

        #CPU drive result
        rand_num = random.random()
        if rand_num < 0.22:
            st.session_state.CPU_SCORE += 7
            st.session_state.RESULT = 'CPU DRIVE RESULT: TD'
        elif 0.22 <= rand_num < 0.38:
            st.session_state.CPU_SCORE += 3
            st.session_state.RESULT = 'CPU DRIVE RESULT: FG'
        else:
            st.session_state.RESULT = 'CPU DRIVE RESULT: PUNT'
        
        # Reset session state
        st.session_state.DOWN = 1
        st.session_state.DISTANCE = 10
        st.session_state.FIELD_POS = -25
    
        return
    
    def reset_drive_disadv(self):
        '''
        Resets the drive after disadvantageous outcome (TOD, Interception, Fumble, Missed FG)

        This function is the same as for advantageous/neutral outcomes
        except the likelihood of a CPU score is increased by 15%.
        '''

        # CPU drive clock runoff
        runoff = -1*int(round(np.random.normal(180,30), 0))
        temp_sec = st.session_state.SECONDS + runoff
        if temp_sec < 0:
            while (st.session_state.MINUTES > 0) and (temp_sec < 0):
                st.session_state.MINUTES = st.session_state.MINUTES-1
                st.session_state.SECONDS = 60 + temp_sec
                temp_sec += 60
            while (st.session_state.MINUTES == 0) and (temp_sec < 0):
                st.session_state.MINUTES = 15
                st.session_state.SECONDS = 0
                st.session_state.PREV_QUART = st.session_state.QUARTER
                st.session_state.QUARTER += 1
                while (st.session_state.MINUTES > 0) and (temp_sec < 0):
                    st.session_state.MINUTES = st.session_state.MINUTES-1
                    st.session_state.SECONDS = 60 + temp_sec
                    temp_sec += 60
        else:
            st.session_state.SECONDS = temp_sec

        #CPU drive result
        rand_num = random.random()
        if rand_num < 0.37:
            st.session_state.CPU_SCORE += 7
            st.session_state.RESULT = 'CPU DRIVE RESULT: TD'
        elif 0.22 <= rand_num < 0.53:
            st.session_state.CPU_SCORE += 3
            st.session_state.RESULT = 'CPU DRIVE RESULT: FG'
        else:
            st.session_state.RESULT = 'CPU DRIVE RESULT: PUNT'
        
        # Reset session state
        st.session_state.DOWN = 1
        st.session_state.DISTANCE = 10
        st.session_state.FIELD_POS = -25
    
        return
    
    def punt_update(self):
        '''
        Updates game state following a user punt
        '''

        st.session_state.RESULT = 'THE USER PUNTED'
        self.update_game()
        
        return
    
    def fg_update(self):
        '''
        Updates game state after user field goal
        '''

        # generates random number between 0 and 1
        rand_num = random.random()

        # if 20 yard fg or less, 100% make
        if dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 97:
            st.session_state.USER_SCORE += 3
            st.session_state.RESULT = 'FG IS GOOD!'
            self.update_game()

        # if fg between 20 and 25 yards, 99% make
        elif 97 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 92:
            if rand_num < 0.99:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()

        # if fg between 25 and 30 yards, 96% make
        elif 92 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 87:
            if rand_num < 0.96:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if fg between 30 and 35 yards, 94% make
        elif 87 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 82:
            if rand_num < 0.94:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if fg between 35 and 40 yards, 88% make
        elif 82 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 77:
            if rand_num < 0.88:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if fg between 40 and 45 yards, 79% make
        elif 77 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 72:
            if rand_num < 0.79:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if fg between 45 and 50 yards, 71% make
        elif 72 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 67:
            if rand_num < 0.71:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if fg between 50 and 55 yards, 63% make
        elif 67 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 62:
            if rand_num < 0.63:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if fg between 55 and 60 yards, 52% make
        elif 62 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 57:
            if rand_num < 0.52:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()

        # if fg between 60 and 65 yards, 36% make
        elif 57 > dropdown.field_pos_dict[st.session_state.FIELD_POS] >= 52:
            if rand_num < 0.36:
                st.session_state.USER_SCORE += 3
                st.session_state.RESULT = 'FG IS GOOD!'
                self.update_game()
            else:
                st.session_state.RESULT = 'FG MISSED'
                self.update_game()
        
        # if further than 65 yards, 0% make
        else:
            st.session_state.RESULT = 'FG MISSED'
            self.update_game()

        return
    
    def rush_master_update(self):
        '''
        Runs all functions to occur on rush button click
        '''

        self.update_position_rush()
        self.update_game()
        return
    
    def update_position_rush(self):
        
        # Generates a random number between 0 and 1
        rand_num = random.random()

        # 1% of the time, playcall results in a fumble
        if rand_num <= 0.01:
            # Fumble
            st.session_state.RESULT = 'FUMBLE'
            st.session_state.DOWN = 1
            st.session_state.DISTANCE = 10
            st.session_state.FIELD_POS = -25
            return
        
        # 99% of the time, playcall results in successful rush
        else:
            # samples from distribution of rushes in the database
            df = self.tRush
            filter_df = df[(df['down']==st.session_state.DOWN) & (df['distance']==st.session_state.DISTANCE)]
            yards_gained = filter_df['yards_gained'].sample().iloc[0]
            dist_temp = st.session_state.DISTANCE - yards_gained
            # if didn't reach line to gain
            if dist_temp > 0:
                # if it wasn't 4th down, moves the ball and updates game state
                if st.session_state.DOWN < 4:
                    st.session_state.DISTANCE = dist_temp
                    st.session_state.DOWN += 1
                    field_pos_temp = dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained
                    st.session_state.FIELD_POS = dropdown.field_pos_dict_reverse[field_pos_temp]
                    st.session_state.RESULT = 'RUSHED FOR ' + str(yards_gained) + ' YARDS!'
                # if it was 4th down, results in a turnover on downs
                else:
                    st.session_state.RESULT = 'TURNOVER ON DOWNS'
                    st.session_state.DOWN = 1
                    st.session_state.DISTANCE = 10
                    st.session_state.FIELD_POS = -25
            # if reached line to gain
            else:
                # if further than 10 yards from the end zone, update game state normally
                if (dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained) <= 89:
                    st.session_state.DOWN = 1
                    st.session_state.DISTANCE = 10
                    field_pos_temp = dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained
                    st.session_state.FIELD_POS = dropdown.field_pos_dict_reverse[field_pos_temp]
                    st.session_state.RESULT = 'RUSHED FOR ' + str(yards_gained) + ' YARDS!'
                # if new ball placement in end zone, score touchdown
                elif (dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained) > 99:
                    st.session_state.USER_SCORE += 7
                    st.session_state.RESULT = 'TOUCHDOWN!'
                    st.session_state.DOWN = 1
                    st.session_state.DISTANCE = 10
                    st.session_state.FIELD_POS = -25
                # if within 10 yards of end zone, update game state to 1st & Goal
                else: 
                    st.session_state.DOWN = 1
                    field_pos_temp = dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained
                    st.session_state.DISTANCE = 100 - field_pos_temp
                    st.session_state.FIELD_POS = dropdown.field_pos_dict_reverse[field_pos_temp]
                    st.session_state.RESULT = 'RUSHED FOR ' + str(yards_gained) + ' YARDS!'

        return
    
    def pass_master_update(self):
        '''
        Runs all functions to occur on pass button click
        '''

        self.update_position_pass()
        self.update_game()
        return
    
    def update_position_pass(self):
        '''
        Function that generates the outcome of the user choosing 'pass' and updates the game state
        '''

        # Generates a random number between 0 and 1
        rand_num = random.random()

        # 1% of the time, playcall results in a fumble
        if rand_num <= 0.01:
            # Fumble
            st.session_state.RESULT = 'FUMBLE'
            st.session_state.DOWN = 1
            st.session_state.DISTANCE = 10
            st.session_state.FIELD_POS = -25
            return

        # 3% of the time, playcall results in an interception
        elif rand_num <= 0.04:
            # Interception
            st.session_state.RESULT = 'INTERCEPTION'
            st.session_state.DOWN = 1
            st.session_state.DISTANCE = 10
            st.session_state.FIELD_POS = -25
            return

        # 7% of the time, playcall results in a sack
        elif rand_num <= 0.11:
            # Sack
            yards_gained = -1*int(round(np.random.normal(7,2),0))
            st.session_state.SACK_BOOL = True

        # 54% of the time, playcall results in a complete pass
        elif rand_num <= 0.65:
            # Completed Pass
            # Samples from distribution of passes in the database
            df = self.tPass
            filter_df = df[(df['down']==st.session_state.DOWN) & (df['distance']==st.session_state.DISTANCE)]
            yards_gained = filter_df['yards_gained'].sample().iloc[0]

        # 35% of the time, playcall results in incomplete pass
        else:
            # Incomplete Pass
            yards_gained = 0

        # depending on result, temporary variable is made by subtracting the yards gained from the yards to the 1st down
        dist_temp = st.session_state.DISTANCE - yards_gained
        # if didn't reach line to gain
        if dist_temp > 0:
            # if it wasn't 4th down, moves the ball and updates game state
            if st.session_state.DOWN < 4:
                st.session_state.DISTANCE = dist_temp
                st.session_state.DOWN += 1
                field_pos_temp = dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained
                st.session_state.FIELD_POS = dropdown.field_pos_dict_reverse[field_pos_temp]
                if st.session_state.SACK_BOOL:
                    st.session_state.RESULT = 'SACKED FOR ' + str(yards_gained) + ' YARDS'
                    st.session_state.SACK_BOOL = False
                else:
                    st.session_state.RESULT = 'PASSED FOR ' + str(yards_gained) + ' YARDS!'
            # if it was 4th down, results in a turnover on downs
            else:
                st.session_state.RESULT = 'TURNOVER ON DOWNS'
                st.session_state.DOWN = 1
                st.session_state.DISTANCE = 10
                st.session_state.FIELD_POS = -25
        # if reached line to gain
        else:
            # if further than 10 yards from the end zone, update game state normally
            if (dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained) <= 89:
                st.session_state.DOWN = 1
                st.session_state.DISTANCE = 10
                field_pos_temp = dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained
                st.session_state.FIELD_POS = dropdown.field_pos_dict_reverse[field_pos_temp]
                st.session_state.RESULT = 'PASSED FOR ' + str(yards_gained) + ' YARDS!'
            # if new ball placement in end zone, score touchdown
            elif (dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained) > 99:
                st.session_state.RESULT = 'TOUCHDOWN!'
                st.session_state.USER_SCORE += 7
                st.session_state.DOWN = 1
                st.session_state.DISTANCE = 10
                st.session_state.FIELD_POS = -25
            # if within 10 yards of end zone, update game state to 1st & Goal
            else: 
                st.session_state.DOWN = 1
                field_pos_temp = dropdown.field_pos_dict[st.session_state.FIELD_POS] + yards_gained
                st.session_state.DISTANCE = 100 - field_pos_temp
                st.session_state.FIELD_POS = dropdown.field_pos_dict_reverse[field_pos_temp]
                st.session_state.RESULT = 'PASSED FOR ' + str(yards_gained) + ' YARDS!'

        return
    
    
    def update_game(self):
        '''
        Updates the game situation after play called
        This mostly entails running off a randomly sampled amount of playclock
        and then changing the game state if it changes the number of minutes or the quarter
        '''

        runoff = -1*int(round(np.random.normal(20,5), 0))
        temp_sec = st.session_state.SECONDS + runoff
        if (st.session_state.MINUTES > 0) and (temp_sec < 0):
            st.session_state.MINUTES = st.session_state.MINUTES-1
            st.session_state.SECONDS = 60 + temp_sec
        elif (st.session_state.MINUTES == 0) and (temp_sec < 0):
            st.session_state.MINUTES = 15
            st.session_state.SECONDS = 0
            st.session_state.PREV_QUART = st.session_state.QUARTER
            st.session_state.QUARTER += 1
        else:
            st.session_state.SECONDS = temp_sec
        
        return
    
    def load_tables_from_db(self):
        '''
        Initialize all dataframes from database
        '''

        self.tGame = self.db.get_tGame()
        self.tPass = self.db.get_tPass()
        self.tRush = self.db.get_tRush()
        self.tRunConcept = self.db.get_tRunConcept()
        
        return
    
    def initialize_session_state(self):
        '''
        Initializes session state variables if they don't already exist
        '''

        if 'MINUTES' not in st.session_state:
            st.session_state.MINUTES = 15
        if 'SECONDS' not in st.session_state:
            st.session_state.SECONDS = 0
        if 'USER_SCORE' not in st.session_state:
            st.session_state.USER_SCORE = 0
        if 'CPU_SCORE' not in st.session_state:
            st.session_state.CPU_SCORE = 0
        if 'QUARTER' not in st.session_state:
            st.session_state.QUARTER = 1
        if 'DOWN' not in st.session_state:
            st.session_state.DOWN = 1
        if 'DISTANCE' not in st.session_state:
            st.session_state.DISTANCE = 10
        if 'FIELD_POS' not in st.session_state:
            st.session_state.FIELD_POS = -25
        if 'HASH' not in st.session_state:
            st.session_state.HASH = 'Center'
        if 'RESULT' not in st.session_state:
            st.session_state.RESULT = ''
        if 'TOD_BOOL' not in st.session_state:
            st.session_state.SACK_BOOL = False
        if 'GAME_START' not in st.session_state:
            st.session_state.GAME_START = True
        if 'PREV_QUART' not in st.session_state:
            st.session_state.PREV_QUART = 1
        if 'RECEIVE_BOOL' not in st.session_state:
            st.session_state.RECEIVE_BOOL = False
        
        st.session_state.SACK_BOOL = False

        return
    
    def streamlit_defaults(self):
        '''
        Remove some auto-generated stuff by streamlit
        '''

        hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
        return
      
if __name__ == '__main__':
    FBApp()