import pickle

# define function that will return a prediction, given some vectorized text data
def predict(data):
    with open('char_class_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model.predict(data)

# define function that will return predicted probabilities for all characters, given some vectorized text data
def predict_proba(data):
    with open('char_class_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model.predict_proba(data)