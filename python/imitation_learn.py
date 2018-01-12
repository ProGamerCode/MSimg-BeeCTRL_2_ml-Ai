# # Unity ML Agents
# ## Imitation Learning (Parallel Behavioral Cloning)

import numpy as np
import tensorflow as tf
import os

from docopt import docopt
from ppo.models import save_model, export_graph
from unityagents import UnityEnvironment

_USAGE = '''
Usage:
  ppo (<env>) [options] 

Options:
  --help                     Show this message.
  --batch-size=<n>           How many experiences per gradient descent update step [default: 64].
  --epoch-batches=<n>        How many batches per epoch. [default: 25].
  --fast                     Whether to run the game at training speed [default: False].
  --hidden-units=<n>         Number of units in hidden layer [default: 128].
  --keep-checkpoints=<n>     How many model checkpoints to keep [default: 5].
  --learning-rate=<rate>     Model learning rate [default: 1e-4].
  --load                     Whether to load the model or randomly initialize [default: False].
  --max-steps=<n>            Maximum number of steps to run environment [default: 5e3].
  --num-layers=<n>           Number of hidden layers between state/observation and outputs [default: 2].
  --run-path=<path>          The sub-directory name for model and summary statistics [default: ppo].
  --save-freq=<n>            Frequency at which to save model [default: 50000].
  --train                    Whether to train model, or only run inference [default: False].
  --worker-id=<n>            Number to add to communication port (5005). Used for multi-environment [default: 0].
'''

options = docopt(_USAGE)
print(options)

env_name = options['<env>']
max_steps = int(options['--max-steps'])
batch_size = int(options['--batch-size'])
train_model = bool(options['--train'])
hidden_units = int(options['--hidden-units'])
learning_rate = float(options['--learning-rate'])
batches_per_epoch = int(options['--epoch-batches'])
load_model = bool(options['--load'])
model_path = './models/{}'.format(str(options['--run-path']))
keep_checkpoints = int(options['--keep-checkpoints'])
save_freq = int(options['--save-freq'])
num_layers = int(options['--num-layers'])
fast_simulation = bool(options['--fast'])


class ImitationNN(object):
    def __init__(self, state_size, action_size, h_size, lr, action_type, n_layers):
        self.state = tf.placeholder(shape=[None, state_size], dtype=tf.float32, name="state")
        hidden = tf.layers.dense(self.state, h_size, activation=tf.nn.elu)
        for i in range(n_layers):
            hidden = tf.layers.dense(hidden, h_size, activation=tf.nn.elu)
        hidden_drop = tf.layers.dropout(hidden, 0.5)
        self.output = tf.layers.dense(hidden_drop, action_size, activation=None)

        if action_type == "discrete":
            self.action_probs = tf.nn.softmax(self.output)
            self.sample_action = tf.multinomial(self.output, 1, name="action")
            self.true_action = tf.placeholder(shape=[None], dtype=tf.int32)
            self.action_oh = tf.one_hot(self.true_action, action_size)
            self.loss = tf.reduce_sum(-tf.log(self.action_probs + 1e-10) * self.action_oh)

            self.action_percent = tf.reduce_mean(tf.cast(
                tf.equal(tf.cast(tf.argmax(self.action_probs, axis=1), tf.int32), self.sample_action), tf.float32))
        else:
            self.sample_action = tf.identity(self.output, name="action")
            self.true_action = tf.placeholder(shape=[None, action_size], dtype=tf.float32)
            self.loss = tf.reduce_sum(tf.squared_difference(self.true_action, self.sample_action))

        optimizer = tf.train.AdamOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)


if not os.path.exists(model_path):
    os.makedirs(model_path)

env = UnityEnvironment(file_name=env_name)
print(str(env))

brain_dict = env.reset(train_mode=fast_simulation)
E = brain_dict['BrainE']
P = brain_dict['BrainP']
brain_parameters = env.brains['BrainE']
s_size = brain_parameters.state_space_size * brain_parameters.stacked_states
a_size = brain_parameters.action_space_size

tf.reset_default_graph()

network = ImitationNN(s_size, a_size, hidden_units, learning_rate, brain_parameters.action_space_type, num_layers)

sess = tf.InteractiveSession()
init = tf.global_variables_initializer()
saver = tf.train.Saver(max_to_keep=keep_checkpoints)

losses = []
percentages = []

sess.run(init)

expert_states = np.zeros([0, s_size])
expert_states = np.append(expert_states, P.states, axis=0)
expert_actions = np.zeros([0, 1])

rewards = 0
steps = 0
while steps < max_steps:
    agent_action = sess.run(network.sample_action, feed_dict={network.state: E.states})
    brains_1 = env.step(agent_action[0])
    E_1 = brains_1['BrainE']
    P_1 = brains_1['BrainP']
    expert_actions = np.append(expert_actions, P_1.previous_actions, axis=0)
    rewards += E_1.rewards[0]
    if len(expert_actions) > 1 and train_model:
        s = np.arange(len(expert_states))
        np.random.shuffle(s)
        shuffle_states = expert_states[s]
        shuffle_actions = expert_actions[s]
        batch_losses = []
        for j in range(min(len(expert_states) // batch_size, batches_per_epoch)):
            batch_states = shuffle_states[j * batch_size:(j + 1) * batch_size]
            batch_actions = shuffle_actions[j * batch_size:(j + 1) * batch_size]
            if brain_parameters.action_space_type == "discrete":
                feed_dict = {network.state: batch_states, network.true_action: np.reshape(batch_actions, -1)}
            else:
                feed_dict = {network.state: batch_states, network.true_action: batch_actions}
            loss, _ = sess.run([network.loss, network.update], feed_dict=feed_dict)
            batch_losses.append(loss)
        if len(batch_losses) > 0:
            losses.append(np.mean(batch_losses))
        else:
            losses.append(0)
    expert_states = np.append(expert_states, P.states, axis=0)
    E = E_1
    P = P_1
    steps += 1
    if steps % save_freq == 0 and steps != 0 and train_model:
        save_model(sess, model_path=model_path, steps=steps, saver=saver)
if steps != 0 and train_model:
    save_model(sess, model_path=model_path, steps=steps, saver=saver)

env.close()
graph_name = (env_name.strip()
      .replace('.app', '').replace('.exe', '').replace('.x86_64', '').replace('.x86', ''))
graph_name = os.path.basename(os.path.normpath(graph_name))
export_graph(model_path, graph_name, target_nodes="action")
