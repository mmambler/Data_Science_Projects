import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from prediction import predict, predict_proba
from character_name_dict import id_to_full_dict

# import character dialogue dataset
df = pd.read_csv('data/processed_char_dialogue.csv')
df.drop(columns=df.columns[0], axis=1, inplace=True)

# filter dataframe to only the top 50 characters by count
table = df.groupby(['character']).count()
table_50 = table.sort_values(by='dialogue', ascending=False).head(50)
df = df[df['character'].isin(table_50.index)].reset_index(drop=True)

# create a dictionary to convert character names to and from ID codes
char_list = df['character'].unique()
class_ids = []
class_to_id_dict = {}
id_to_class_dict = {}
for i, char in enumerate(char_list):
  class_ids.append(i)
  class_to_id_dict[char] = i
  id_to_class_dict[i] = char

# map the values onto this dictionary
df['character'] = df['character'].map(class_to_id_dict)

# define feature and target variables
X, y = df['dialogue'].values, df['character'].values

# vectorize the text with TF-IDF vectorizer, removing stopwords
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5,
                        ngram_range=(1, 2),
                        stop_words='english')

# use vectorizer to fit transform the feature
X = tfidf.fit_transform(X).toarray()

# title of page
st.header('S.C.R.I.P.T. - Screenplay Character Recognition and Interactive Prediction Tool')
st.markdown('''
            The S.C.R.I.P.T. character prediction tool offers you the opportunity to input any piece of text you wish — from speeches, to twitter posts, to even song lyrics — and receive a prediction of the fictional movie character most likely to have spoken that text!
            Predictions result from a Linear Support Vector Classification model trained on the dialogue of 50 movie characters gathered from the Internet Movie Script Database (IMSDb). The 50 characters can be found on the character list page.
            
            Please enter your own text, and try the tool for yourself!
            ''')

# text box to get text input from a user
text_response = [st.text_area('Enter Your Text Here')]

# button that when pressed will pass the text into the model and return a prediction and bar plot
if st.button('Generate Character Prediction'):
    text_vec = tfidf.transform(text_response).toarray()
    result = predict(text_vec)
    st.write('')
    st.write('S.C.R.I.P.T. predicts this text was spoken by:')
    # present highest-probability prediction
    st.write(f"**{id_to_full_dict[result[0]]}**")
    st.write('')
    # display photo of character
    st.image('photos/' + str(result[0]) + '.jpeg', width=300)
    st.write('')

    # use predict_proba to get the probabilities for each character
    results = predict_proba(text_vec)
    data = {'ID':np.arange(50),
            'Prob':results[0]}
    results_df = pd.DataFrame(data = data,  
                    columns = ['ID','Prob'])
    
    # sort the dataframe of probabilities
    results_df_sorted = results_df.sort_values('Prob', ascending=False).reset_index(drop=True)
    for i, id in enumerate(results_df_sorted.ID):
        results_df_sorted.ID[i] = id_to_full_dict[id]
    results_df_sorted = results_df_sorted.head(10)

    # assign the probabilities and IDs as X and Y
    y = results_df_sorted['Prob']
    x = results_df_sorted['ID']

    fig, ax = plt.subplots()

    # Create a horizontal bar chart
    bars = ax.barh(x, y)
    ax.invert_yaxis()

    # Format axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    ax.xaxis.grid(False)
    ax.set_yticklabels(x, fontsize=8)
    ax.set_xlabel('Probability', labelpad=15, color='#333333')

    fig.tight_layout()

    # Present the plot
    st.write(fig)