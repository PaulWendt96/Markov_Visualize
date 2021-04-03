import json
from markov import MarkovModel, State, Transition, make_gif

with open("markov_json.json") as markov_json:
    markov_json = json.load(markov_json)


def json_to_markov(markov_json):
    state_dict = {}
    transition_dict = {}

    markov = markov_json['model']['markov']
    markov_model_start_state = markov_json['model']['start']


    for start_state, transition in markov.items():
        state = start_state[len("state_"):]
        state_dict[state] = (State(name=state))

    # Add transitions to transition_dict
    for start_state, transitions in markov.items():
        start_state_transition_list = []
        inner_transitions = {start_state[len("state_"):]: start_state_transition_list}
        for transition, probability in transitions.items():
            start_node = state_dict[transition]
            end_node = start_state[len("state_"):]
            start_state_transition_list += [Transition(state_dict[start_state[len("state_"):]], state_dict[transition], probability)]
        transition_dict[start_state[len("state_"):]] = start_state_transition_list

    # Add transition objects to states
    for state_name, state_transitions in transition_dict.items():
        state = state_dict[state_name]
        state.add_transitions(state_transitions)

    return MarkovModel(list(state_dict.values()), state_dict["Active"])

def json_to_gif(markov_json, *args, **kwargs):
    model = json_to_markov(markov_json)
    make_gif(model, *args, **kwargs)

#m = json_to_markov(markov_json)
json_to_gif(markov_json)
#make_gif(m, "GIF_from_markov_json", 5, 10)