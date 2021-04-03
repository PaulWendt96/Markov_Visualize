from __future__ import annotations
from abc import abstractmethod
from collections import Counter
import os
from random import random
from subprocess import Popen, PIPE, STDOUT, call, run
from typing import List, Callable, Tuple
from math import log
from copy import deepcopy

from tempdir import make_temporary_directory

class Validator():

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value, obj)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value, obj):
        pass


class Transition():

    def __init__(self, start_state, end_state, probability):
        self.start_state = start_state
        self.end_state = end_state
        self.probability = probability
        self.animation_attrs = {}
        self.add_initial_animation_attrs()

    @property
    def p(self, *args, **kwargs):
        return self.probability

    def add_initial_animation_attrs(self):
        self.animation_attrs['label'] = '"{}"'.format(self.p)

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.start_state,
                                       self.end_state,
                                       self.probability)


class ValidateTransitions(Validator):

    search_for_repeat_node = 1000

    def __set__(self, obj, value):
        self.validate(value, obj)
        setattr(obj, self.private_name, value)

    def _validate_probs_sum_to_less_than_one(self, probs: List[float],
                                             states: List[State]) -> None:
        if sum(probs) > 1:
            raise ValueError("Error -- Sum of transition probabilities is > 1")

    def _validate_no_negative_probs(self, probs: List[float],
                                    states: List[State]) -> None:
        for probability, state in zip(probs, states):
            if probability <= 0:
                raise ValueError("Error -- Transition probability from node "
                                 "'{}' is '{}'; all transition probabilties "
                                 "must be > 0".format(state, probability))

    def _validate_no_repeat_nodes(self, probs: List[float],
                                  states: List[State]) -> None:
        num_states = len(states)
        num_unique_states = len(set([state.name for state in states]))
        if num_unique_states != num_states:
            if num_states <= self.search_for_repeat_node:
                states = Counter(states)
                offending_states = [state.name for state, freq
                                    in states.items() if freq > 1]
                raise ValueError("Error -- the following transition states "
                                 "are represented multiple times: "
                                 "{}".format(', '.join(offending_states)))
            else:
                raise ValueError("Error -- at least one transition state is "
                                 "represented multiple times (as this state "
                                 "has > '{}' transitions, we do not search for "
                                 "the offending node; this functionality can be "
                                 "changed by changing the 'search_for_repeat_nodes' "
                                 "variable in the 'ValidateTransitions' "
                                 "class)".format(self.search_for_repeat_node))

    def _validate_self_not_in_nodes(self, probs: List[float],
                                    states: List[State], obj: State) -> None:
        if obj in states:
            raise ValueError("Error -- a state cannot have an "
                             "explicit transition to itself")

    def validate(self, transitions: List[Transition], obj: State) -> None:
        probs = [transition.p for transition in transitions]
        states = [transition.end_state for transition in transitions]
        self._validate_probs_sum_to_less_than_one(probs, states)
        self._validate_no_negative_probs(probs, states)
        self._validate_no_repeat_nodes(probs, states)
        self._validate_self_not_in_nodes(probs, states, obj)


class StateUpdate():

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        obj.history.append(value.name)
        obj.t += 1
        setattr(obj, self.private_name, value)


class State():

    transitions = ValidateTransitions()

    def __init__(self, name: str, action: Callable=None,
                 transitions: List[Transition]=None):

        if transitions is None:
            transitions = []
        self.name = name
        self.action = action
        self.transitions = transitions
        self.animation_attrs = {}

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.name, self.action,
                                       self.transitions)

    def __str__(self):
        return 'State {}'.format(self.name)

    def __eq__(self, state):
        return isinstance(state, self.__class__) and state.name == self.name

    @property
    def num_transitions(self):
        return len(self.transitions)

    def add_transition(self, transition: Transition):
        self.transitions = self.transitions + [transition]

    def add_transition_from_prob(self, new_state: State, initial_prob: float):
        transition = Transition(self, new_state, initial_prob)
        self.transitions = self.transitions + [transition]

    def add_transitions(self, transitions: List[Transition]):
        for transition in transitions:
            self.add_transition(transition)

    def add_transitions_from_prob(self, transitions: List[Tuple[State, float]]):
        for new_state, prob in transitions:
            self.add_transition_from_prob(new_state, prob)

class MarkovModel():

    current_state = StateUpdate()

    def __init__(self, states: List[State], start_state: State):
        self.states = states
        self.t = 0                         # updates dynamically on setting self.current_state
        self.history = []                  # updates dynamically on setting self.current_state
        self.current_state = start_state
        self.initial_state_formats(self.current_state)   # put initial node in blue
        self.animation_attrs = {'label': 'START', 'labelloc': 't', 'fontsize': 30}


    def initial_state_formats(self, initial_state):
        ''' formats for the initial state (e.g. starting state before model starts running) '''
        initial_state.animation_attrs['style'] = 'filled'
        initial_state.animation_attrs['color'] = 'blue'

    def model_actions_on_transition(self):
        self.animation_attrs['label'] = '{}'.format(len(self.history) - 1)

    def state_actions_on_transition(self, state):
        state.animation_attrs['style'] = 'filled'
        state.animation_attrs['color'] = 'red'

    def transition_actions_on_transition(self, transition):
        transition.animation_attrs['style'] = 'bold'

    def update_animation(self, transition):
        self.model_actions_on_transition()
        self.state_actions_on_transition(self.current_state)
        if transition is not None:
            self.transition_actions_on_transition(transition)

    def transition(self, transition):
        old_state = self.current_state
        if transition:
            assert transition.start_state == old_state
            self.current_state = transition.end_state
        else:
            self.current_state = old_state
        self.update_animation(transition)


    @property
    def list_of_transitions(self):
        transitions = []
        for state in self.states:
            for transition in state.transitions:
                transitions.append(transition)
        return transitions


    def _parse_state(self, state):
        return state.name

    def _parse_state_attrs(self, state):
        ''' whitespace is not significant in DOT, so it is ok if we insert an extra space when no animation attrs present'''
        format_string = ' '.join(['[{}]'.format(self._parse_attr(k, v)) for k, v in state.animation_attrs.items()])

        # cleanup animation attribute dictionary
        state.animation_attrs = {}
        return format_string

    def _parse_states(self):
        state_string = ' ;'.join(['\n"{}"{}'.format(self._parse_state(state), self._parse_state_attrs(state)) for state in self.states])
        return state_string + ' ;'

    def _parse_transition_attrs(self, transition):
        ''' whitespace is not significant in DOT, so it is ok if we insert an extra space when no animation attrs present'''
        format_string = ' '.join(['[{}]'.format(self._parse_attr(k, v)) for k, v in transition.animation_attrs.items()])
        # cleanup animation attribute dictionary
        try:
            label = transition.animation_attrs['label']
            transition.animation_attrs = {'label': label}
        except KeyError:
            transition.animation_attrs = {}
        return format_string


    def _parse_transition(self, transition):
        start_state = transition.start_state
        end_state = transition.end_state
        transition_string = '"{}" -> "{}" {}'.format(start_state.name, end_state.name, self._parse_transition_attrs(transition))
        return transition_string

    def _parse_transitions(self):
        transition_string = ' ;'.join(['\n' + self._parse_transition(transition) for transition in self.list_of_transitions])
        return transition_string + ' ;\n'

    def _parse_markov(self):
        return '{}{}'.format(self._parse_states(), self._parse_transitions())

    def _parse_attr(self, key, value):
        return '{}={}'.format(key, value)

    def _parse_model_attrs(self):
        ''' whitespace is not significant in DOT, so it is ok if we insert an extra space when no animation attrs present'''
        return ' '.join([self._parse_attr(k, v) + ';' for k, v in self.animation_attrs.items()])


    def to_digraph_string(self):
        ''' have markov model represent itself in DOT form. See www.graphviz.org/doc/info.lang.html '''
        return 'digraph G {{{} {}}}'.format(self._parse_model_attrs(), self._parse_markov())

    def encoder(self):
        return self.to_digraph_string().encode()


    def probs(self):
        rand_result = random()
        cumulative_prob = 0
        for transition in self.current_state.transitions:
            cumulative_prob += transition.p
            if cumulative_prob > rand_result:
                self.transition(transition)
                return
        self.transition(None) # if we reach the end, no change


def save_file_generic(string):
    def f(file_name):
        with open(file_name, 'w+') as file:
            file.write(string)
    return f

def save_file_gv(markov_graph, size=320): # size isn't in the right place, but it doesn't matter for now
    ''' saves a markov graph's state to provided file_path. file_path, when provided, should be the
    full path to the file that we want to create (in this case, path to a .png file) '''
    def f(file_path):
        with open(file_path, 'w+') as out:
            pipe = Popen(['dot', '-Gsize=1,1!', '-Gdpi={}'.format(size), '-T', 'png'], stdout=out, stdin=PIPE, stderr=None)
            pipe.communicate(input=markov_graph.encoder())
        markov_graph.probs()    # TODO: fix this. terribly hacky. works better if we can ensure that markov_graph is a copy of some underlying graph
    return f


def make_gif(markov_graph, basename='giffy', state_changes_per_second=1, iterations=100):
    '''
    create GIF from underlying markov graph. file names are padded in order to
    satisfy ffmpeg formatting. see:

    https://www.unix.stackexchange.com/questions24014/creating-a-gif-animation-from-png-files

    do note that the underlying markov_graph is copied in order to perform the animations.
    '''
    tempdir_name = 'sampledir' # TODO: need better naming heuristic
    delay = (1/state_changes_per_second)*100
    padding = int(log(iterations, 10)) + 1
    with make_temporary_directory(os.getcwd(), tempdir_name, remove_if_already_exists=True) as path:
        graph_saver = save_file_gv(deepcopy(markov_graph))
        file_paths = []
        for i, _ in enumerate(range(iterations)):
            iteration = i + 1
            file_name = '{}{}.png'.format(''.join(['0' for _ in range(padding - int(log(iteration, 10)) - 1)]), iteration)
            file_paths.append(file_name)
            graph_saver(os.path.join(path, file_name))

        #command = 'ffmpeg -r {} -i {}%0{}d.png -vf scale=860:1000 {}'.format(state_changes_per_second, tempdir_name + '\\', padding, basename + '.gif')
        command = 'magick -delay {} {} {}'.format(delay, tempdir_name + '\\' + '*.png', basename + '.gif')
        run(command)


def strings_to_text_in_temporary_directory(strings):
    ''' test function for make_temporary_directory(). creates len(strings) text
    files in a temporary directory'''
    with make_temporary_directory(os.getcwd(), 'sampledir') as path:
        savers = [save_file_generic(string) for string in strings]
        i = 0
        for saver in savers:
            file_name = 'sample_{}.txt'.format(i)
            saver(os.path.join(path, file_name))
            i = i + 1