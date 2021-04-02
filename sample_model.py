from markov import State, MarkovModel, make_gif

# create the markov model
s1 = State('Active', None)
s2 = State('Disabled', None)
s3 = State('Dead', None)
s4 = State('Dirt', None)
s5 = State('Plant', None)
s6 = State('Cheetah', None)
s7 = State('Man', None)
s1.add_transitions_from_prob([(s2, .5), (s3, .02)])
s2.add_transitions_from_prob([(s1, .5), (s3, .03)])
s3.add_transitions_from_prob([(s4, .8), (s5, .07), (s6, .10), (s7, .02)])
s4.add_transition_from_prob(s3, .5)
s5.add_transition_from_prob(s3, .5)
s6.add_transitions_from_prob([(s7, .01), (s5, .2), (s4, .3), (s3, .2)])
s7.add_transition_from_prob(s1, .5)
states = [s1, s2, s3, s4, s5, s6, s7]
markov = MarkovModel(states, s1)

# turn model into GIF
make_gif(markov, basename='giffy', state_changes_per_second=2, states=200)