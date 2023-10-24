import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    directory = "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # try to implement the search considering the first movie of source
    # all the movies of target  
    source_neighbours = neighbors_for_person(source) # returns [(movie_id, person_id)...)
    #print(source_neighbours)

    path = []  # [(movie_id, person_id), (movie_id, person_id)...(movie_id, target_id)]

    frontier = list()
    
    start = Node(id=source, parent=None, movie_id=None)

    frontier.append(start)

    explored_nodes = set()

    explored_nodes.add(int(source))

    target_node = []

    while frontier: 
        
        # when there is noone to check
        if len(frontier) == 0:
            return None

        parent_node = frontier.pop(0)
        
        neignbours = neighbors_for_person(str(parent_node.id)) # [(movie_id, person_id)...)

        for neigbour in neignbours:

            person_id = int(neigbour[1])
            node_movie_id = int(neigbour[0])

            node = Node(id=person_id, parent=parent_node, movie_id=node_movie_id)
            
            if person_id == int(target):
                path = construct_path(node)
                return path

            if person_id not in explored_nodes:
                if not any(person_id == n.id for n in frontier):
                    frontier.append(node)
                    explored_nodes.add(person_id)
            
                # if a person is processed before, just skip
            else:
                continue
        

    

def construct_path(node):
    
    path = []
    

    while node.parent is not None:

        path.append((str(node.movie_id), str(node.id)))

        node = node.parent

    path.reverse()

    return path
'''        if person.id == int(source):
            path.reverse()   # requires small touch -- nothing is required
            return path

        path.append((person.movie_id, person.id))  # in first (movie, target)'''





def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
