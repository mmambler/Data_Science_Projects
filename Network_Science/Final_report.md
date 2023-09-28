## Final Report
### IMDB Analytics
### 5/13/2023

---

## Introduction

Hollywood is a very interesting phenomonenon in it of itself - it remains one of the most important cultural exports of the United States, it is contantly reported on by media, and it has influenced other movie industries all over the world. Actors are often the most notable people in Hollywood as they are the ones that are on screen for everyone to see. We have discussed the network of actors and actresses that work in Hollywood in our course, and we have seen that this network is quite interconnected through our study of the "6 Degrees of Kevin Bacon."

The network of directors and the crew members that they work with is a much less studied phenomenon. Crew members are essential to the production of television and film, and they are often overlooked when viewing a movie. This project aims to create a network of film directors and the crew members they have worked with in their career. The purpose of this project is to gain insight into this network and make inferences about various sub-groups of directors, like minorities, women, and renowned directors. This is accomplished through four subtasks: data extraction, network generation, visualization, and analysis.

--- 


## Phase 1: Data Extraction
### Mac Ambler

First and foremost, the goal with our data extraction was to gather all the necessary data for each of the one hundred directors to be able to properly analyze the research questions. 

In order to accomplish this, we set out originally to create a large, nested dictionary containing every director, each of their feature-length films, and all of the crew for each of these films, stored in one JSON file. Upon execution, however, it became clear that this was not the most efficient method. The resulting dataset was unnecessarily large, took a long time to extract, wasn't failure tolerant, and was more difficult to work with in the subsequent project subtasks. For this reason, we decided to attempt a new strategy, composed of nested file folders and individual JSON files for each feature film. The final structure was as follows:



> Working Directory

>> Director Folders

>>> Director Information JSON

>>> Movies Folder

>>>> Individual Movie JSONs Containing Crew Information

To begin extracting the data, the first step was to read in the dataset of the top 101 directors on IMDb as a Pandas dataframe and create a column containing the isolated director IDs from the directors' IMDb page URIs. This was accomplished with the user-built function "make_dir_df()". 

Next, we iterated over the director dataframe and created folders within the working directory named after each of the directors' IMDb ID. In these folders, we created JSON files containing information on each of the directors, including their name, sex, race/ethnicity, and any additional labels (H for top 25 most renowned, and Q for LGBTQ+). This is the code used to create a dictionary with the directors' information and dump it into a JSON file, which is part of the user-built function "create_dir_info()".

```{python}
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
```
The next step was to create a folder in each of the directors' folders to house all the JSON files for each of their feature-length movies. This was the final nested folder to create before we would extract the crew data for each and every movie, storing it in the form of a JSON file with the same name as the movie title. These JSON files were comprised of nested dictionaries with the following structure:

> Movie ID

> Movie Title

> Roles

>> Role Description

>>> Crew Member ID
 
>>>> Crew Member Name

Building these JSON files was accomplished utilizing the user-built function "create_movie_jsons()". The function takes the file path for the working directory and a director ID as inputs. First, the function uses the provided "get_full_credits_for_director()" to scrape the director's entire filmography from IMDb and iterates over each credited project.

```{python}

    # iterate over each movie in the director's credits
    for mov_info in imdb_scraper.get_full_credits_for_director(uri).get('credits'):

```
Then, for each of these projects, it checks whether the JSON file already exists and checks whether it is a feature film using the provided "is_feature_film_v2()" function. If it passes both of these requirements, a dictionary is created and populated with the movie ID, title, and an empty dictionary for the crew roles.


```{python}
  # create empty dictionary for movie information
  indiv_mov_dict = {}
  # populate the dictionary with the movie ID, title, and an empty dictionary 
  for crew roles
    indiv_mov_dict['uri'] = isolate_mov_uri(mov_info)
    indiv_mov_dict['title'] = mov_info['title']
    indiv_mov_dict['roles'] = {}
```
In order to populate the roles dictionary, we iterated over each of the credits gathered from the provided "get_full_crew_for_movie()" function.

```{python}
    # iterate over the crew credits
    for credit in imdb_scraper.get_full_crew_for_movie(indiv_mov_dict['uri']).get('full_credits'):

```

We used a user generated function called "check_not_cast()" to ensure the role was not some variant of Cast. This role was then used as the title of another dictionary, which was then populated with the IDs of crew members in said role and their names.

```{python}
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

```
Finally, the complete dictionary of the crew for a movie was dumped to a JSON file named after the movie.

```{python}
    # dump complete dictionary into JSON file in working directory
    with open(path1 + '/' + mov_info['title'].replace('/',' ') + '.json', 'w') as fp:
        json.dump(indiv_mov_dict, fp)

```

Additionaly, a number of safeguards were put in place throughout the extraction process to ensure that, if there were any issues that arose, we would be able to spot them and correct them without having to rerun succesful crew extractions. For example, in case the "create_movie_jsons()" function were to fail at the stage where it checks whether the project is a feature film, there is an "else" statement that prints out the project title so we can ensure this was the correct judgement. Also, we instituted a counter mechanism so that as the code extracts each director's filmography it announces which director is being extracted and how many out of the total number have been completed.

We needed to run the code a couple of different times in order to get the complete dataset extracted as there were a number of times that the IMDb query request would timeout. Luckily, though, since we had safe measures in place, each subsequent running of the code got increasingly faster. In the end, we had a complete dataset containing the top 101 directors on IMDb, each of their feature-length films, and the crews that worked on them. We were then able to progress to the next stage of the project, Network Generation.

---

## Phae 2: Network Generation
### Nick Reeder

After getting the extracted data, we processed and built a bipartite network for directors (top nodes) and crew members (bottom nodes). The network was built iteratively by director and was designed to be failure tolerant, testing viability at each director.
The program also generated a CSV file of network statistics for each director to paint a full picture of the network at each stage. At each iteration, the program records the number of nodes, number of edges, and density.

To begin, the code checks that the correct number of items have been given to the program through the PowerShell:
```{python}
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
```

The PowerShell input should read as follows: python Network_generation.py dir_data DNI_LIST.
Where dir_data is the folder containing the director data, and DNI_LIST is an optional list of roles to not include in the network. If this list is not given then by default non-oscar winning crew roles will not be included. Should the user want all roles included, they would simply add an empty list [] in the DNI_LIST position.


Each director is then passed into a function called "add_director(network, dir_id, dni, self_loops = False)", which takes the network, director id (a folder in the dir_data file labeled with the director's name), dni (a list of roles to not include), and a boolean self_loop (defaulted to false, decides whether or not to include self-loops in the network).

The function add_director has four main portions.

First, it adds the director node to the network with labels corresponding to director information. Each node's name is the director id, and it has the following features: name, sex, ethnicity, and label (renowned and LGBTQ+).
```{python}
cwd = os.getcwd()
  os.chdir(cwd + '\\' + dir_id)
  cwd = os.getcwd()
  f = open('dir_info.json')
  data = json.load(f)
  print(data['Name'])
  network.add_node(dir_id, bipartite = 0, name = data['Name'], sex = data['Sex'], eth = data['Ethnicity_Race'], label = data['Labels'])
  f.close()
```


Second, it creates two lists and a dictionary: a list of crew ids, a list of roles, and a dictionary of crew ids: crew names. It will then move through each movie, appending each crew id and role to their respective lists and building a dictionary that links each crew id to that crew member's name. Finally, this portion then makes three counter dictionaries that get the raw count of the number of times a crew member was hired, the count of the number of times that each role was hired for a movie, and the number of times each crew id worked a specific role. Note that this third dictionary is the unique count for that director crew member pair.

This does not count for any roles that are in the Do Not Include list, named dni.
```{python}
list_of_c_ids = [] 
  id_name_dict = {}
  num_movies = len(movies)
  role_list = []


  crew_role_dict = {}

  for movie in movies:
    #print(movie)
    #print(movie)
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

```

Third, it calculates the adjusted weight for each crew member with the following formula:

$\text{weight} = \frac{\text{number of this crew members has worked for this director in their primary role for this director}}{\text{number of movies that this director as employed this role}}$

In words, the weight takes the count of this crew members most commonly worked role and divides by the opportunities that this crew member would have had to work with this director. This normalizes the weighting so that directors with more movies are not overweighted and roles that are not always part of the production process (eg sound department for a silent movie) and not underweighted. 

```{python}
adj_weights = {}
  for crew_id in raw_weights:
    crew_role = max(crew_role_dict[crew_id], key=crew_role_dict[crew_id].get)
    crew_role_count = role_count[crew_role]
    adjusted_weight = crew_role_dict[crew_id][crew_role] / crew_role_count
    adj_weights[crew_id] = adjusted_weight
```

Fourth, it adds the crew nodes and edges to the network. Checking if the node already exists in the network, adding it if not, and adding the edge from the crew node to the director node. Each crew node is named as their IMDB id and has the name as a feature, and each edge has the weight and the primary crew role for that crew-director pair. Finally, if self_loops is false, the network removes all self-loops.

```{python}
for crew_id in adj_weights.keys():
    if crew_id not in network.nodes():
      network.add_node(crew_id, bipartite = 1, name = id_name_dict[crew_id])
  for crew_id in adj_weights:
     network.add_edge(dir_id, crew_id, weight = adj_weights[crew_id], role = max(crew_role_dict[crew_id], key=crew_role_dict[crew_id].get))
  
  #print('nodes added')
  
  if not self_loops:
    network.remove_edges_from(nx.selfloop_edges(network))
```

Once the director is added, the network removes all director-director edges, records the relevant statistics at that iteration, and continues to the next director. 

```{python}
        for neighbor in imdb_network.neighbors(folder):
          if imdb_network.nodes[neighbor]['bipartite'] == imdb_network.nodes[folder]['bipartite']:
            to_rem.append(neighbor)
        for name in to_rem:
          imdb_network.remove_edge(name, folder)
        os.chdir(cwd)
        number_nodes.append(imdb_network.number_of_nodes())
        number_edges.append(imdb_network.number_of_edges())
        density_iter.append(nx.density(imdb_network))
        print('Success')
```

Once the network is built, the program prints the iterative statistics data frame and writes both a gexf file of the network and a CSV file of the iterative statistics.

Below is an example output in the terminal

Current progress 5%  
Attemping to add director_id: nm0000229  
Steven Spielberg  
Success  
Current runtime:  3.3384777000000003  
Runtime for director is: 0.5728507  

--- 

## Phase 3: Network Visualization
### Skyler Seets

After the Network was generated, it was passed through the command line to generate a gexf file that included all of the directors in the database and excluded all unwanted roles. For this network, the complete set of excluded roles were: 'Additional Crew', 'Animation Department', ' Art Department', 'Art Direction by', 'Camera and Electrical Department', 'Cast', 'Casting By', 'Casting Department', 'Costume and Wardrobe Department', 'Editorial Department', 'Location Management', 'Music Department', 'Produced by', 'Production Department', 'Production Management', 'Script and Continuity Department', 'Second Unit Director or Assistant Director', 'Set Decoration by', 'Stunts', 'Thanks', 'Transportation Department', and 'Visual Effects by'.

Then, the gexf file was loaded into Gephi. Because of the nature of the network, with directors being one category and crew members being a separate category, we chose to visualize this network using a bipartite network. In terms of coloring the nodes, all of the crew nodes were colored with a light pink. The director nodes were then colored based on director ethnicity using a fluorescent palette. As discussed earlier, each edge had a label representing the primary role that that crew member had with a specific director. Because of this, we were able to color the edges based on crew roles in order to give an idea of what roles were most prominent within the network. The top three most common crew roles–Sound Department, Makeup Department, and Special Effects by–were each assigned a shade of blue. Only these were colored uniquely because the three roles alone make up over 60% of the edges in the network. The rest of the edges were colored gray to visually represent a broad “other category” (as coloring each uniquely would be visually confusing and each of these roles made up a significantly smaller proportion of the total network). We chose this entire color palette for maximum visibility. The pink and blue are a stark contrast from each other, allowing the nodes to easily be separated from the web of edges. Additionally, the fluorescent hues of the directors allows them to stand out sharply against this background and be distinguished easily.

Beyond colors, the director nodes are also distinguished by shape. While all of the crew nodes are represented by standard circles, the directors are either a square or a triangle, to represent the sex of the director (male and female, respectively). This was done by installing a polygon plug-in to Gephi and re-coding the sex column to the integers of 3 and 4, which correlate to polygon shapes for the nodes. This adds to the interpretability of the network, as not only can the viewer parse the ethnicity of the directors, but also their sex, from just a glance.

Finally, we altered the elements of the base network on size. All of the nodes were given a size from 10 to 120, based on their degree. This allows the most prominent directors to show the largest. Additionally, we weighted the edges based on the weights calculated during the network generation. Once all of these visual elements were decided, we created the network using the ForceAtlas2 layout in Gephi with an additional run to prevent overlap. To add to readability, the edges were given an opacity of 50% and the borders around the nodes were increased from 1 to 2. We did not include any node labels on this network, as it a bit visually overwhelming and masks the ethnicity/sex markings, but they will be included in some of the sub-networks. (See key below the network for exact ethnicity and role colors)

![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_1.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_2.png)

After this first network was created, we then discussed how to use visualizations in our quest to answer the three research questions. We decided to first create two diversity networks–one showing just female directors and one showing only non-white directors--in order to see how these networks compared to the overall. In Gephi, we did this by using the filters tab and using the Mask and equals functions to filter based on gender and ethnicity, respectively. We delve further deeper into the exact differences between these networks and the full one through number analytics, but the visual does allow for some interesting interpretations. First, we can see that the female-only network tends to have less overlap between the crews of different directors, with each director having their own pods. This suggests that female directors may be more likely to work with the same crew members (as they stick mainly to their own pods), in comparison to the overall network. The non-white director network showed a bit more overlap between the crews used by different directors, but it still seems more separated than the overall network, suggesting a similar conclusion.

These networks also allow us to better characterize the diversity within the director network, as, for example, the most prominent female directors have a greater diversity than can be see among male directors. When looking at the entire network, it becomes clear how many white men there are (yellow squares), whereas the female-only network has prominent black and Latina (represented by the colors orange and pink) directors. The non-white director network is, similar to the entire network, mostly made up of male directors, but it doesn't seem to be dominated entirely by one ethnicity.

![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_3.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_4.png)

In order to further explore this question, we also created two additional networks. The first was for renowned directors, and the second was to look at only those nodes that had an edge weight of 0.5 or more. This last network represents only the strongest director-crew relations, where that director has employed that specific person for 50% or more of the times they employed that role. In order to ensure that the director labels could be read, we sized them according to degree, included a white outline, and ensured that they were placed overtop of all of the nodes and edges. The network of renowned directors lets us see that, in comparison to other sub-networks and the overall, there seems to be more variety in the crews used by each director and a lot more overlap between the crews used by different directors (they stick to their own individual bubble of the same crew members). In looking at the high weight network, interestingly, the majority of the edges are gray, rather than blue, meaning that these are less common roles. This makes sense, intuitively, as the top three crew roles are much more widespread and there is a greater variety in who directors employ. These less common roles, whether that be because they are highly specialized and less people tend to do them, or because they are not as widely needed as other roles, tend to have stronger director-crew relations. This is also the most disjointed network we've seen. This also makes intuitive sense, as it represents close relationships between directors and crew members, so it is less likely that different directors are using the same crew members as each other.

![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_5.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_6.png)

Finally, in order to answer the third question, we decided to create three visualizations of particularly interesting nodes–Martin Scorcese, Charles Burnett, and Sterlin Hajaro. These nodes are interesting to observe and compare. For Martin Scorcese, we can see rings of crew members and a lot of them, indicating that he has employed a lot of crew members, with varying degrees of repetition. In comparison, Charles Burnett has employed significantly less crew members, and they are all close in centrality to him. Sterlin Hajaro represents the node that contributed the fewest edges to the overall network

![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_7.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_8.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/visualizations/vis_9.png)


---

## Phase 4: Network Analysis
### Ani Sreekumar

This section primarily seeks to address the research questions for this project.

How widespread is the phenomenon of directors re-using the same crew? Do renowned directors (and women/minority directors) tend to work persistently with the same key collaborators and less recognized directors tend to work with shifting groups of collaborators?
How will you characterize the film-director network? What are the properties (Average shortest path length, triangles aka clustering coefficient, density/sparsity)?
Did you find any interesting nodes/links?
To address these questions, we loaded in the .gexf file that was generated by the network generation python script in order to analyze it using the NetworkX library. We calculate basic properties of the network like the number of nodes and edges in the graph. Our graph contains 42,745 nodes and 85,822 edges.

```{python}
graph = nx.read_gexf('graph.gexf')

#number of nodes and edges
print("Number of nodes: ", graph.number_of_nodes())
print("Number of edges: ", graph.number_of_edges())

```
Beginning with the first research question, we first consider the phrasing of “how widespread the phenomenon of directors re-using the same crew” is. It is difficult to accurately assess how widespread a phenomenon is among Hollywood directors without having more director information to compare our limited data to. However, we can analyze this phenomenon among our 101 directors in order to make general inferences about Hollywood directors.

As mentioned in the Network Generation section, the primary metric of our network to assess the strength of the relationship between a director and their crew is the weights of the edges in the graph. We calculate the average edge weight in the entire graph in order to have a benchmark to compare individual directors to. The average edge weight for the whole graph was 0.32.

```{python}
#get all the edge weights, list comprehension
edge_weights = [data['weight'] for _, _, data in graph.edges(data=True)]
#compute average
average_weight = np.average(edge_weights)

print("Average Edge Weight: ", average_weight)
```

Although without context this number does not tell us the whole story of the network, it suggests that the phenomenon of directors re-using the same crew is not extremely common. An average edge weight of 0.32 suggests that for every 100 times a director employs a particular crew role, they hire the same person 32 times.

To address the research question of how widespread the phenomenon is of directors re-using the same crew, we calculated the average edge weight of each director. Since the weight of each edge connecting a director node to a crew member measures the proportion of directors hiring the same crew members for the same roles, the directors were ordered by their average edge weights to determine which directos hire the same crew members for the same job at the highest proportion.

```{python}
#sorting directors by the average weight of all their edges, get the average of the averages also

director_weights = {}

#do this for each director
for director in graph.nodes():
    # skip crew members
    if graph.nodes[director]['bipartite'] == 1:
        continue
    
    total_weight = 0
    count = 0
    #get edge weights and get the average
    for crew_member in graph.neighbors(director):
        weight = graph.get_edge_data(director, crew_member)['weight']
        total_weight += weight
        count += 1
    
    if count > 0:
        average_weight = total_weight / count
    else:
        average_weight = 0
    
    
    director_weights[director] = average_weight

#lambda function to get the weights for each director and sort it in descending order
directors_sorted_by_weight = [director for director, weight in sorted(director_weights.items(), key=lambda item: item[1], reverse=True)]
# calculate the average of edge weights of directors
average_weight = sum(director_weights.values()) / len(director_weights)

print(f"Average of Average Edge Weight of All Directors: {average_weight}")
#print each director, average edge weight, and their attributes
for director in directors_sorted_by_weight:
    attributes = graph.nodes[director]
    print(f"Director: {attributes['name']}, Average Weight: {director_weights[director]}, Attributes: {attributes}")

```
In order to analyze sub-networks within the graph and address the second portion of the first research question, we separated the director nodes into different groups based on their node attributes. We then followed a similar process as above to compare the edge weights of renowned vs un-renowned directors. The average edge weight of un-renowned directors was 0.31, while the average edge weight of renowned directors was 0.13. We conducted a difference in means test between these two groups and it returned a p value of less than 0.0005, suggesting that renowned and un-renowned directors have a statistically significant difference in their mean edge weight.

```{python}
#t test for renowned vs unrenowned directors

from scipy.stats import ttest_ind

renowned_weights = list(h_director_weights.values())
unrenowned_weights = list(non_h_director_weights.values())

t, p = ttest_ind(renowned_weights, unrenowned_weights, equal_var=False)

print("T-value:", t)
print("P-value:", p)

```

This suggests that un-renowned directors have a greater tendency to hire the same crew members for the same roles when compared to renowned directors. Similar tests were conducted to compare men/women directors and white/minority directors. The test for white/minority directors yielded a p value of 0.07 and the test for men/women directors yielded a p value of 0.11. Although these results are not statistically significant based on a significance level of 0.05, they are generally indicative that there is some small difference in means between these groups.

The results of our analysis suggest that un-renowned directors, female directors, and minority directors tend to work with the same crew members at a higher rate than their renowned, male, and white counterparts.

Below are several visualizations showing the differences in average edge weight for renowned and un-renowned directors, women and men, and white directors and minority directors.

```{python}
colorList = []
#make a color list to pass as an argument
for director in directors_sorted_by_weight:
    # skip crew members
    if graph.nodes[director]['bipartite'] == 1:
        continue
    if graph.nodes[director]['label'] != "H":
        colorList.append("orangered")
    if graph.nodes[director]['label'] == "H":
        colorList.append("lightgreen")

import matplotlib.pyplot as plt

sorted_weights = [director_weights[director] for director in directors_sorted_by_weight]

#bar graph
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(directors_sorted_by_weight, sorted_weights, color=colorList)
ax.set_xlabel('Directors')
ax.set_ylabel('Average Edge Weight')
ax.set_title('Average Edge Weight of Directors')

#legend
handles = [plt.Rectangle((0,0),1,1, color=color) for color in ['lightgreen', 'orangered']]
labels = ['Renowned Directors', 'Un-Renowned Directors']
ax.legend(handles, labels)


ax.set_xticklabels([])
plt.show()
# Save 
fig.savefig('directors_weight.png', dpi=300, bbox_inches='tight')

```
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/figures/graph_1.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/figures/graph_2.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/figures/graph_3.png)

These charts serve as helpful tools to visualize the differences in average edge weight for the different subcategories of networks. The charts and statistical tests suggest that un-renowned directors, female directors, and non-white directors tend to re-hire the same crew members at a higher rate than their renowned, male, white counterparts. Since female directors and non-white directors are both minorities in the network of directors, they may prefer to give opportunities to people they see as marginalized in the film industry. This may lead to them re-hiring the same crew members at a higher rate.

Another approach that we took to answer this question was to determine each director's degree divided by the number of movies that they have made. This number gives us an idea of a director's tendency to re-hire the same crew members, since edge weights are not taken into account. This metric is also flawed because directors that work on larger, higher budget films will likely work with more crew members on average than directors working on smaller films. However, it is useful for examining the average number of crew members that a director utilized for each film. This provides insight into the general size of the films the director works on, as well as their tendency to re-hire the same people. In order to accomplish this, we calculated the degree of each director and divided it by the number of movies they have directed from their node attribute. This list was sorted in order and used to create visualizations of the top 10 and bottom 10 degree per movie scores.

```{python}
import matplotlib.pyplot as plt

director_degrees = {}
for director in graph.nodes():
    # skip crew members
    if graph.nodes[director]['bipartite'] == 1:
        continue
    # calculate degree per movie
    num_movies = graph.nodes[director]['number_of_movies']
    if num_movies > 0:
        degree = graph.degree(director)
        degree_per_movie = degree / num_movies
        director_degrees[director] = degree_per_movie

# sort by degree per movie, get top 10
sorted_director_degrees = sorted(director_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
directors_sorted_by_degree = [x[0] for x in sorted_director_degrees]

# create a color list to pass as an argument
colorList = []
for director in directors_sorted_by_degree:
    # skip crew members
    if graph.nodes[director]['bipartite'] == 1:
        continue
    if graph.nodes[director]['eth'] == "W":
        colorList.append("orangered")
    if graph.nodes[director]['eth'] != "W":
        colorList.append("lightgreen")

# list of degrees per movie sorted in the same order as directors_sorted_by_degree
sorted_degrees = [director_degrees[director] for director in directors_sorted_by_degree]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(directors_sorted_by_degree, sorted_degrees, color=colorList)

# set axis labels and title
ax.set_xlabel('Directors')
ax.set_ylabel('Degree per Movie')
ax.set_title('Directors with Highest Degree per Movie Directed ')

#legend
handles = [plt.Rectangle((0,0),1,1, color=color) for color in ['lightgreen', 'orangered']]
labels = ['Not White', 'White']
ax.legend(handles, labels)

ax.set_xticklabels([graph.nodes[director]['name'] for director in directors_sorted_by_degree], rotation=90)

plt.show()
```
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/figures/graph_4.png)
![alt text](https://github.com/NickReeder/data-340-02/blob/main/imdb_analytics/figures/graph_5.png)

To examine the second research question, we calculate various summary statistics for our network.

```{python}
density = nx.density(graph)
print("Density: ", density)

#average shortest path length
avg_shortest_path_length = nx.average_shortest_path_length(graph)
print("Average shortest path length:", avg_shortest_path_length)

#clustering coefficient
cc = nx.average_clustering(graph)
print("Clustering Coefficient: ", cc)


```
The density of our network is 0.000094. This value suggests that the director-crew network is similar to other real world graphs that have density values very close to 0.

The average shortest path length of our network is 3.87, meaning that on average it take 3.87 steps to travel from a director node to a crew node. This is a relatively short average path length when compared to other real world social or collaborative networks. The shortest average path length of the network of Hollywood actors ("6 Degrees of Kevin Bacon") that we studied earlier in this course is 2.99. This suggests that the network of Hollywood actors is more interconnected than our direct-crew member network. This makes sense considering that the number of crew members in Hollywood is much larger than the number of working actors and actresses. 

Since our network is bipartite, the clustering coefficient of the graph is 0 because triangles are not possible in a bipartite network. This is because directors are not connected to other directors and crew members are not connected to other crew members.

Based on these statistics, the network is relatively sparse but also relatively interconnected as the average shortest path length is quite low. The network can be characterized as less interconnected than the network of Hollywood actors. 


To address the third research question, we calculated several other graph properties to find nodes of interest. We calculated the degree centrality of each director node to determine the directors that have worked with the largest percentage of all of the crew members in the network. Martin Scorsese is notable in this network for having a significantly higher degree centrality than any other directors (0.13). The next highest degree centrality value is 0.08. This indicates that Martin Scorsese has worked with the highest number of crew members in the network by a significant margin. Another interesting node is Charles Burnett, as he has the highest average edge weight of all the directors in the network, and he appears in the top five directors in terms of degree centrality. 

```{python}
#degree centrality sorted highest to lowest
#(percent of all crew members that they have worked with at some point)

deg_centrality = nx.degree_centrality(graph)
top_101 = sorted(deg_centrality.items(), key=lambda x: x[1], reverse=True)[:101]

total_deg_cent = sum(node[1] for node in top_101)
avg_deg_cent = total_deg_cent / len(top_101)
print(f"Average degree centrality of Directors: {avg_deg_cent}")


for node in top_101:
  attributes = graph.nodes[node[0]]
  print(f"Attributes of node {node}: {attributes}")

```


---

## Conclusion

This project sought to analyze the relationship between 101 Hollywood directors and the crew members that they have worked with in their careers. The network can be characterized as relatively sparse but still well connected. It is not as well connected as the network of Hollywood actors that have worked in the same films, but it is generally well connected as compared to other social networks. 

Additionally, after discussion among the group, we believe the difference in our conclusions stems from the different approach to weights as well as the bipartite structure removing all director-director connections. By revealing more edges and allowing for crew member career development there was a different data set to work with. 

### References


*   6 Degrees of Kevin Bacon - <https://blogs.ams.org/mathgradblog/2013/11/22/degrees-kevin-bacon/> 
*   Bipartite Networks - Georgios A Pavlopoulos, Panagiota I Kontou, Athanasia Pavlopoulou, Costas Bouyioukos, Evripides Markou, Pantelis G Bagos, Bipartite graphs in systems biology and medicine: a survey of methods and applications, GigaScience, Volume 7, Issue 4, April 2018, giy014, https://doi.org/10.1093/gigascience/giy014


