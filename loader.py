from utils import *


print(get_player_profile("scores.json","lotis"))

def write_new_score(score, player_name):
        try:
            ind, data_scores = get_player_ind("scores.json",player_name)
        except ValueError:
            ind, data_scores = create_player_profile("scores.json",player_name), -1
        all_content = read_json("scores.json")
        categories = list(data_scores.keys())[1:] # NOTE: en caso de añadir nuevos campos modfiicar los indices!
        scores = list(data_scores.values())[1:]
        scores = [int(score) for score in scores]
        scores.append(score)
        scores.sort(reverse=True)
        for category, score in zip(categories,scores):
            data_scores[category] = str(score)
        all_content[ind] = data_scores
        write_json(all_content,"scores.json")


write_new_score(5,"pepe3")
#create_player_profile("scores.json","julieta")

