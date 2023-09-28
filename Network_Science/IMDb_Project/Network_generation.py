import json
import traceback 
import pandas as pd
from collections import Counter
import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.wiener import is_connected
import timeit


import sys
import os


##### TO DO #####
# ask if customer wants self loops
# add comments


def add_director(network, dir_id, dni, self_loops = False):
  cwd = os.getcwd()
  os.chdir(cwd + '\\' + dir_id)
  cwd = os.getcwd()
  os.chdir(cwd + '\\movies')
  movies = os.listdir(cwd + '\\movies')
  num_movies = len(movies)
  os.chdir(cwd)
  f = open('dir_info.json')
  data = json.load(f)
  print(data['Name'])
  network.add_node(dir_id, bipartite = 0, name = data['Name'], sex = data['Sex'], eth = data['Ethnicity_Race'], label = data['Labels'], number_of_movies = num_movies)
  f.close()
  #print(cwd)
  os.chdir(cwd + '\\movies')
  #print(os.getcwd())
  cwd = os.getcwd()

  list_of_c_ids = [] 
  id_name_dict = {}
  role_list = []


  crew_role_dict = {}

  for movie in movies:
    if movie == '.DS_Store':
        continue
    #print(movie)
    #print(cwd)
    f = open(movie)
    data = json.load(f)
    for role in data['roles']:
      if role not in dni: #if role not in list of those not to include, add add crew ids to listp; otherwise skip.
        role_list.append(role)
        for crew_id in data['roles'][role]:
          list_of_c_ids.append(crew_id)

          id_name_dict[crew_id] = data['roles'][role][crew_id]['name']
          if crew_id in crew_role_dict.keys():
            #print(role)
            crew_role_dict[crew_id].append(role)
          else:
            crew_role_dict[crew_id] = [role]


    f.close()
  #print("movies completed")

  role_count = dict(Counter(role_list))
  #print('roles counted')
  raw_weights = dict(Counter(list_of_c_ids))
  #print('raw weights counted')

  for crew_id in crew_role_dict:
    crew_role_dict[crew_id] =dict(Counter(crew_role_dict[crew_id]))
  
  #print('crew role dict counted')

  #print(crew_role_dict)

  adj_weights = {}
  for crew_id in raw_weights:
    crew_role = max(crew_role_dict[crew_id], key=crew_role_dict[crew_id].get)
    crew_role_count = role_count[crew_role]
    adjusted_weight = crew_role_dict[crew_id][crew_role] / crew_role_count
    adj_weights[crew_id] = adjusted_weight

  for crew_id in adj_weights.keys():
    if crew_id not in network.nodes():
      network.add_node(crew_id, bipartite = 1, name = id_name_dict[crew_id])
  for crew_id in adj_weights:
     network.add_edge(dir_id, crew_id, weight = adj_weights[crew_id], 
                      role = max(crew_role_dict[crew_id], key=crew_role_dict[crew_id].get))
  
  #print('nodes added')
  
  if not self_loops:
    network.remove_edges_from(nx.selfloop_edges(network))

  #if dir_id == 'nm0000876':

  #print('self loops removed')

if __name__ == '__main__':
  if len(sys.argv) < 2:
    # This means the user did not provide the filename to check.
    # Show the correct usage.
    print('Did not detect folder. Please include folder containing director data.')
  else:
    imdb_network = nx.Graph()
    print('File recieved, building netowrk')
    if len(sys.argv) < 3:
      dni = ['Additional Crew', 'Animation Department', 'Art Department', 'Art Direction by', 'Camera and Electrical Department',
             'Cast', 'Casting By', 'Casting Department', 'Costume and Wardrobe Department', 'Editorial Department', 'Location Management',
             'Music Department', 'Produced by',' Production Department', 'Production Management', 'Script and Continuity Department',
             'Second Unit Director or Assistant Director', 'Set Decoration by', 'Stunts', 'Thanks', 'Transportation Department',
              'Visual Effects by']
      print('No roles specified, by default the following roles will not be included', str(dni))
    elif sys.argv[2] == []:      
      print('All roles will be included')
    else:
      dni = sys.argv[2]
      print('Roles chosen not to indlude are:', str(dni))
    path_to_data = sys.argv[1]
    cwd = os.getcwd()
    os.chdir(cwd + '\\' + path_to_data)
    cwd = os.getcwd()
    entries = os.listdir(cwd)


    director_ids = []
    number_nodes = []
    number_edges = []
    density_iter = []
    
    counter = 0
    start = timeit.default_timer()
    print()
    print()
    for folder in entries:
      progress = int(counter/len(entries)*100)
      print('Current progress',  str(progress) + '%')
      start_dir = timeit.default_timer()
      if folder == '.DS_Store':
        continue
      try:
        counter +=1
        print("Attemping to add director_id:", folder)
        add_director(imdb_network, folder, dni)
        to_rem = []
        for neighbor in imdb_network.neighbors(folder):
          if imdb_network.nodes[neighbor]['bipartite'] == imdb_network.nodes[folder]['bipartite']:
            to_rem.append(neighbor)
        for name in to_rem:
          imdb_network.remove_edge(name, folder)
        os.chdir(cwd)
        director_ids.append(folder)
        number_nodes.append(imdb_network.number_of_nodes())
        number_edges.append(imdb_network.number_of_edges())
        density_iter.append(nx.density(imdb_network))
        print('Success')
      except Exception:
        print("Failed to add to add director_id:", folder)
        print(traceback.print_exc())

      stop = timeit.default_timer()
      print('Current runtime: ', stop - start) 
      print('Runtime for director is:', stop - start_dir)
      print()
      print()

    
    print('All directors added')

    iterative_network_statistics = pd.DataFrame(index= range(1,counter+1), data=
                                                {'director_id': director_ids,
                                                'num_nodes' : number_nodes,
                                                'num_edges' : number_edges,
                                                'density': density_iter})
    print('Network Built')
    print('num nodes', imdb_network.number_of_nodes())
    print('num edges', imdb_network.number_of_edges())
    #print(is_connected(imdb_network))

    print('Writing gexf file')
    os.chdir('C:\\Users\\Nick\\desktop\\Network_Sciences')
    cwd = os.getcwd()

    print(iterative_network_statistics)

    #Current perfomance is about O(n^10)

    ###### TO WRITE GEXF and CSV FILE UNCOMMENT BELOW LINE AND CHANGE DIRECTORY AS NEEDED ###########
    #print('Files will be written to:', cwd)
    #nx.write_gexf(imdb_network, cwd + '\\Network_v1.gexf')
    #iterative_network_statistics.to_csv(cwd + '\\iterative_stats.csv')