import json
from markov import MarkovModel, State, Transition, make_gif

def json_to_markov(markov_json):
    state_dict = {}
    transition_dict = {}
    markov = markov_json['model']['markov']
    remove_prefix = lambda state_name_with_prefix: state_name_with_prefix[len("state_"):]

    for start_state, transition in markov.items():
        state = remove_prefix(start_state)
        state_dict[state] = (State(name=state))

    # Add transitions to transition_dict
    for start_state, transitions in markov.items():
        start_state_transition_list = []
        for transition, probability in transitions.items():
            start_state_transition_list += [Transition(state_dict[remove_prefix(start_state)], state_dict[transition], probability)]
        transition_dict[remove_prefix(start_state)] = start_state_transition_list

    # Add transition objects to states
    for state_name, state_transitions in transition_dict.items():
        state = state_dict[state_name]
        state.add_transitions(state_transitions)

    return MarkovModel(list(state_dict.values()), state_dict["Active"])

def json_to_gif(markov_json, *args, **kwargs):
    model = json_to_markov(markov_json)
    make_gif(model, *args, **kwargs)