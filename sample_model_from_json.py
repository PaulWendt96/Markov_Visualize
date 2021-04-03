from parse_markov_json import json_to_gif
import json

with open("markov_json.json", "r") as markov_model_json:
    markov_json = json.load(markov_model_json)

json_to_gif(markov_json, "gif_generated_from_json", 5, 10)
