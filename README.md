# Markov_Visualize at a glance
Create Markov Chain visualizations similar to what is shown below. This project takes a significant amount of inspiration from [GraphvizAnim](https://github.com/mapio/GraphvizAnim). 

<img src=reincarnation.gif alt=Markov GIF/>

## How do I install Markov_Visualize?
```bash
git clone https://www.github.com/PaulWendt96/Markov_Visualize
```
To make a GIF, Markov_Visualize produces a number of PNG images from a given MarkovModel. Markov_Visualize then uses these PNG images to create a GIF using ffmpeg and magick. All PNG images are stored in a temporary directory, which is created when the script begins and removed when the script is finished. Markov_Visualize relies on the [DOT](https://graphviz.org/download/) and [magick](https://imagemagick.org/script/download.php) programs to create GIFs. You will need to install these programs and add them to your PATH if you want Markov_Visualize to work correctly.

## How do I use Markov_Visualize?
Create a Markov model using markov.py, then call ```make_gif``` to make GIF.

```python
from markov import State, MarkovModel, make_gif

# create the markov model
s1 = State('Active')
s2 = State('Disabled')
s3 = State('Dead')
s4 = State('Dirt')
s5 = State('Plant')
s6 = State('Cheetah')
s7 = State('Man')
s1.add_transitions_from_prob([(s2, .5), (s3, .02)])
s2.add_transitions_from_prob([(s1, .5), (s3, .03)])
s3.add_transitions_from_prob([(s4, .8), (s5, .07), (s6, .10), (s7, .02)])
s4.add_transition_from_prob(s3, .5)
s5.add_transition_from_prob(s3, .5)
s6.add_transitions_from_prob([(s7, .01), (s5, .2), (s4, .3), (s3, .2)])
s7.add_transition_from_prob(s1, .5)
states = [s1, s2, s3, s4, s5, s6, s7]
markov = MarkovModel(states=states, start_state=s1)

# turn model into GIF
make_gif(markov, basename='reincarnation', state_changes_per_second=2, iterations=200)
```

You can also make a GIF from a model defined in JSON. 

```python
from parse_markov_json import json_to_gif
import json

with open("markov_json.json", "r") as markov_model_json:
    markov_json = json.load(markov_model_json)
    
json_to_gif(markov_json, "gif_generated_from_json", 5, 10)
```

Add animations to a markov model by changing ```markov.MarkovModel.model_actions_on_transition, markov.MarkovModel.state_actions_on_transition, markov.MarkovModel.transition_actions_on_transition``` methods. Note that animations are calculated from ```animation_attrs``` dictionaries which are associated with the ``` markov.MarkovModel, markov.State, markov.Transition``` objects.


## What are Markov chains?
[Markov chains](https://simple.wikipedia.org/wiki/Markov_chain#:~:text=A%20Markov%20chain%20is%20a,right%20now%20(the%20state).&text=Markov%20chains%20can%20be%20discrete%20or%20continuous.) are stochastic models that connect a series of possible future events with directed transitions. Markov chains are essentially graphs consisting of nodes and directed edges. Each node represents a different state that the Markov chain can be in. Each directed edge represents a potential movement from the current state **state<sub>i</sub>** to the next state **state<sub>i + 1</sub>**. Markov Chains move states base on conditional probability, in which the conditional probability represents the probability that a given directed edge in the graph is taken. Markov Chains are stochastic models, which means that they move randomly based on probabilities. As a result, every call to ```make_gif(markov, basename, state_changes_per_second, iterations)``` will likely result in a slightly different GIF. 

Despite their conceptual simplicity, Markov Models have an enormous variety of real world purposes. Financial models, for example, often rely heavily on [regime switching](https://quant.stackexchange.com/questions/30139/what-is-a-regime-switch) models that model expected asset returns differently based on different states of the economy. Health insurers use markov models to help set premiums by stochastically determining how often policyholders are active or disabled. You can even use markov chains to generate [reasonably good sentences](https://www.kdnuggets.com/2019/11/markov-chains-train-text-generation.html) given a corpus of text to train on. The resulting sentences make syntactic sense, and are similar to what you might expect a rudimentary RNN to produce. 

## What are the primary limitations of Markov_Visualize?
This tool should be used primarily for visualizations. If you're serious about performance, you should consider implementing Markov chains using tools like Numpy. 

The current ```markov.py``` does not allow Markov Chains to have explicit transitions to themselves (this probability is calculated implicitly). This prevents nodes from having arrows to themselves. See [GraphvizAnim](https://github.com/mapio/GraphvizAnim) if you'd like to make GIFs with nodes that can point to themselves.

It is currently difficult to change transitions in the model while it is running. This is because ```make_gif``` makes a copy of the ```MarkovModel``` object before it starts iterating. Copying the provided markov model before turning it into a GIF ensures that the original model is not iterated over without the author explicitly telling it to iterate. There is, however, nothing stopping you from commenting out this copying if you wish to change the model animations dynamically while it is running.

## How do I contribute?
Pull requests are welcome. This is one of my first repositories (and one of my first times using git), so please let me know if there is anything I could include that might be useful in this repository or in future repositories. 
