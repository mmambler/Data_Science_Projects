# NLP Final Project - Mac Ambler

## S.C.R.I.P.T. - Screenplay Scharacter Recognition and Interactive Prediction Tool

Streamlit Link: https://script-nlp-final.streamlit.app/

Data:
- Scraped using using the "Movie-Script-Database" tool by GitHub user Aveek-Saha
- Scraped data can be found in the "script_scraping" folder within the "data" folder
- Data was preprocessed using the code in the "data_processing" folder
- Final processed data can be found in "processed_char_dialogue.csv" within the "data" folder

Modeling:
- All modeling code can be found in "Modeling.ipynb" in the root folder
- Final LinearSVC model was pickled and saved in the root folder as "char_class_model.pkl"

Streamlit Implementation:
- Main Streamlit code can be found in "S.C.R.I.P.T..py" in the root folder
- Code for the character list page of the app is found in the "pages" folder
- "prediction.py" file contains functions that gather predictions from the pickled model given a user input
- All package imports for Streamlit can be found in "requirements.txt"
- User does not need to import these themselves, the Streamlit app does this automatically
