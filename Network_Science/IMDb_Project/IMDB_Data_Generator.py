#python -m pip install bs4
#python -m pip install isoduration
#python -m pip install NwalaTextUtils
#python -m pip install PyMovieDb



def make_dir_df():
  """
  Reads in the director dataset and creates a list of the director IDs. 

            Parameters:
                    None

            Returns:
                    Director dataframe
  """

  # import necessary packages
  import pandas as pd
  import numpy as np
  
  # read director csv file from url
  url = 'https://raw.githubusercontent.com/anwala/teaching-network-science/main/spring-2023/homework/hw5-group/group-project-topic-01/100_film_directors.csv'
  df = pd.read_csv(url)

  # use 'for' loop to iterate over each director's uri and append their ID to a list
  imdb_uri = []
  for i in df['IMDb_URI']:
    imdb_uri.append(i[-10:][:-1])

  # assign the list as a new column in the dataframe 
  df['URI'] = imdb_uri

  return df

def create_dir_folders(path, df):
  """
  Creates folders in a given file path for each of the directors' IDs.

            Parameters:
                    path (string): File path in which to create the folders
                    df (dataframe): Dataframe containing director IDs

            Returns:
                    None
  """

  # import necessary packages
  import os

  # iterate over the director IDs
  for i in df['URI']:
    newpath = path + i
    # set path as working directory
    os.chdir(path)
    # check if no folder exists for ID
    if not os.path.exists(newpath):
        # create folder for the ID
        os.makedirs(newpath)
  
def create_dir_info(path, df, uri):
  """
  Creates JSON file in director's folder containing name, sex, ethnicity/race, and labels of the director.

            Parameters:
                    path (string): File path containing director folders
                    df (dataframe): Dataframe containing director IDs
                    uri (string): ID of director to create JSON for

            Returns:
                    None
  """

  # import necessary packages
  import os

  # set director's folder as working directory
  path = path + uri
  os.chdir(path)

  # create empty dictionary
  dir_inf_dict = {}
  # assign director's name to key "Name" using the format "FirstName LastName"
  dir_inf_dict['Name'] = df[df['URI']==uri]['FirstName'].values[0] + ' ' + df[df['URI']==uri]['LastName'].values[0]
  # assign director's sex to key "Sex"
  dir_inf_dict['Sex'] = df[df['URI']==uri]['Sex'].values[0]
  # assign director's ethinicity/rate to key "Ethnicity_Race"
  dir_inf_dict['Ethnicity_Race'] = df[df['URI']==uri]['Ethnicity_Race'].values[0]
  # assign director's labels to key "Labels"
  dir_inf_dict['Labels'] = df[df['URI']==uri]['Labels'].values[0]

  # dump dictionary into JSON file in the working directory
  with open('dir_info.json', 'w') as fp:
    json.dump(dir_inf_dict, fp)

def create_movie_folders(path, uri):
  """
  Creates folders in a given file path for the directors' movies.

            Parameters:
                    path (string): File path of working directory containing director folders
                    uri (string): ID of director to create movies folder for

            Returns:
                    None
  """

  # import necessary packages
  import os

  # create string for movies folder path
  newpath = path + uri + '/movies'
  # set path as directory
  os.chdir(path)
  # check if no movies folder exists
  if not os.path.exists(newpath):
      # create movies folder
      os.makedirs(newpath)

def isolate_mov_uri(mov_info):
  """
  Takes a movie URI and returns the isolated IMDb movie ID

            Parameters:
                    mov_info (dictionary): Dictionary of information regarding one movie in a director's catalogue

            Returns:
                    uri (string): Isolated IMDb movie ID
  """

  # character strings that comes before and after movie ID
  start = 'title/'
  end = '/?ref'

  # use start and end variables to isolate the movie ID and assign it to return variable
  uri = mov_info['uri'][mov_info['uri'].find(start)+len(start):mov_info['uri'].rfind(end)]
  return uri

def isolate_crew_uri(member):
  """
  Takes a crew member URI and returns their isolated ID

            Parameters:
                    member (dictionary): Dictionary of information regarding a crew member

            Returns:
                    uri (string): Isolated IMDb crew member ID
  """

  # character strings that comes before and after crew member ID
  start = 'name/'
  end = '/?ref'

  # use start and end variables to isolate the crew member ID and assign it to return variable
  uri = member.get('link')[member.get('link').find(start)+len(start):member.get('link').rfind(end)]
  return uri

def check_not_cast(credit):
  """
  Checks whether crew member's role is some variation of 'Cast'

            Parameters:
                    credit (dictionary): Dictionary of information regarding an individual movie credit

            Returns:
                    None
  """

  # Check whether the role of the credit is a variation 'Cast'
  if ((credit.get('role') != 'Cast') and (credit.get('role') != 'Cast (in credits order)') and (credit.get('role') != 'Cast (in credits order) complete, awaiting verification') and (credit.get('role') != 'Cast (in credits order) verified as complete') and (credit.get('role') != 'Cast complete, awaiting verification')):
    return True

def create_movie_jsons(path, uri):
  """
  Creates JSON file in director's movies folder containing information 
    about a particular movie, the crew that worked on it, and their roles.

            Parameters:
                    path (string): File path containing director folders
                    uri (string): ID of director to create JSON for

            Returns:
                    None
  """

  # import necessary packages
  import os

  # check that the director has IMDb credits
  if imdb_scraper.get_full_credits_for_director(uri).get('credits') is not None:
    # iterate over each movie in the director's credits
    for mov_info in imdb_scraper.get_full_credits_for_director(uri).get('credits'):
      
      # establish path for working directory
      path1 = path + uri + '/movies'
      # create path string for individual movie JSON
      json_path = path1 + '/' + mov_info['title'] + '.json'
      # set the working directory
      os.chdir(path1)

      # check to ensure JSON file doesn't already exist
      if not os.path.exists(json_path):
        # check that the movie is a feature length film
        if imdb_scraper.is_feature_film_v2(isolate_mov_uri(mov_info)) == True:
          # create empty dictionary for movie information
          indiv_mov_dict = {}
          # populate the dictionary with the movie ID, title, and an empty dictionary for crew roles
          indiv_mov_dict['uri'] = isolate_mov_uri(mov_info)
          indiv_mov_dict['title'] = mov_info['title']

          indiv_mov_dict['roles'] = {}
          # check that crew credits exist for the movie
          if imdb_scraper.get_full_crew_for_movie(indiv_mov_dict['uri']).get('full_credits') is not None:
            # iterate over the crew credits
            for credit in imdb_scraper.get_full_crew_for_movie(indiv_mov_dict['uri']).get('full_credits'):
              # check to ensure the crew member role is not a variant of cast
              if check_not_cast(credit) == True:
                # create empty dictionary for that role
                indiv_mov_dict['roles'][credit.get('role')] = {}
                # check that individual crew members exist for the role
                if credit.get('crew') is not None:
                  # iterate over each crew member in the role
                  for member in credit.get('crew'):
                    # create dictionary titled the crew member's ID and populate it with their name
                    indiv_mov_dict['roles'][credit.get('role')][isolate_crew_uri(member)] = {}
                    indiv_mov_dict['roles'][credit.get('role')][isolate_crew_uri(member)]['name'] = member.get('name')

          # dump complete dictionary into JSON file in working directory
          with open(path1 + '/' + mov_info['title'].replace('/',' ') + '.json', 'w') as fp:
            json.dump(indiv_mov_dict, fp)

        # if didn't pass feature film check, print the credit info
        else:
          print(mov_info['uri'], mov_info['title'])

#######################################################################

# import the 'imp' package for loading the imdb_scraper.py file
import imp

# load imdb_scraper and import json & pandas
py_file_path = str(input('Input file path for imdb_scraper.py file: '))
imdb_scraper = imp.load_source('imdb_scraper', py_file_path)
import json
import pandas as pd

# create director dataframe
df = make_dir_df()

# establish path of working directory and create director folders in this directory
# path = '/Users/macambler/Desktop/dir_data/'
path = str(input('Input file path of working directory in which to build the dataset: '))
create_dir_folders(path=path, df=df)

# create empty list for the director IDs
dir_uris = []
# iterate over the director IDs in the dataframe and append them to the list
for i in df['URI']:
  dir_uris.append(i)

# establish a counter and total number to track progress of data extraction
counter = 1
total = len(dir_uris)

# iterate over the director IDs
# for each:
    # create a json of director info
    # create a folder for the movies
    # create a json containing movie info and crew
    # print extraction progress
for uri in dir_uris:
  print("Extracting Director: ", uri)
  create_dir_info(path=path, df=df, uri=uri)
  create_movie_folders(path=path, df=df, uri=uri)
  create_movie_jsons(path=path, uri=uri)
  print("Completed Directors: ", counter, ' out of ', total)
  counter+=1





