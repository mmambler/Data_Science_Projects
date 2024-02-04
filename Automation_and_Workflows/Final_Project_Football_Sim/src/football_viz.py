import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
import src.dropdown_lists as dropdown
import streamlit as st
import pandas as pd
import numpy as np

class FBField():
    '''
    Visual representation of a football field
    '''
    XMIN = -10
    XMAX = 110
    YMIN = 0
    YMAX = 53.3

    def __init__(self, hash = None, field_pos = None, distance = None):
        self.hash = hash
        self.field_pos = field_pos
        self.distance = distance

        self.build_field()
        self.add_yard_markers()
        self.place_football(self.hash, self.field_pos)
        self.mark_chains(self.field_pos, self.distance)
        return 
    
    def build_field(self):
        '''
        Draw an empty field
        '''

        self.fig, self.ax = plt.subplots(figsize=(10,5.33))

        self.ax.set_xlim([self.XMIN, self.XMAX])
        self.ax.set_ylim([self.YMIN, self.YMAX])
        
        # went with astroturf, and looked up the RGBA at: https://icolorpalette.com/color/astroturf
        self.ax.set_facecolor([0.404,0.631,0.349,0.5])
        return
    
    def add_yard_markers(self):
        # End zone lines as thick black
        self.ax.plot([0,0],[self.YMIN, self.YMAX], 
                     color='k', 
                     linewidth=2
                     )
        self.ax.plot([100,100],
                     [self.YMIN, self.YMAX], 
                     color='k',
                     linewidth=2
                     )
        
        # Add End zones
        endzone1 = patches.Rectangle((-10, 0),
                                      10, 53.3,
                                      edgecolor='none', 
                                      facecolor='dimgray', 
                                      alpha=1)
        endzone2 = patches.Rectangle((100, 0),
                                      10, 53.3,
                                      edgecolor='none', 
                                      facecolor='dimgray', 
                                      alpha=1)
        self.ax.add_patch(endzone1)
        self.ax.add_patch(endzone2)
        
        # Every 5 yard markers
        for z in range(1,20):
            self.ax.plot([z*5, z*5], 
                         [self.YMIN, self.YMAX], 
                         '-w', 
                         alpha=0.5
                         )
            # Add hashes
            self.ax.plot([(z*5)-.75, (z*5)+.75], 
                         [self.YMIN + 20, self.YMIN + 20], 
                         '-w', 
                         alpha=0.5
                         )
            self.ax.plot([(z*5)-.75, (z*5)+.75], 
                         [self.YMAX - 20, self.YMAX - 20], 
                         '-w', 
                         alpha=0.5
                         )

        # Labels
        self.ax.set_xticks([z*10 for z in range(1,10)])
        self.ax.set_xticklabels([z*10 if z<6 else 100-z*10 for z in range(1,10)])
        self.ax.set_yticks([])

        return

    def place_football(self, 
                       hash = None,
                       field_pos = None
                       ):
        '''
        Places a football image on the field at the indicated hash and field position
        '''
            
        img = 'src/images/football.png'
        football_img = image.imread(img)
        imagebox = OffsetImage(football_img, zoom = 0.05)
        
        if (hash != None) & (field_pos != None):
            hash_dict = {'Left':33.3, 'Center':26.65, 'Right':20}
            ab = AnnotationBbox(imagebox, (dropdown.field_pos_dict[field_pos], hash_dict[hash]), frameon = False)
            self.ax.add_artist(ab)

        return

    def mark_chains(self, 
                    field_pos=None, 
                    distance=None
                    ):
        '''
        Draws lines on the field for LOS and 1st Down
        '''
        
        if (field_pos != None) & (distance != None):
            self.ax.plot([dropdown.field_pos_dict[field_pos], dropdown.field_pos_dict[field_pos]], 
                         [self.YMIN, self.YMAX], 
                         'black', 
                         alpha=0.5
                         )
            self.ax.plot([dropdown.field_pos_dict[field_pos] + distance, dropdown.field_pos_dict[field_pos] + distance], 
                         [self.YMIN, self.YMAX], 
                         'yellow', 
                         alpha=0.5
                         )
        
        return
