import os
import pickle

import neat
import msm_model
import numpy as np
import utils

runs_per_net = 3

def make_env(action_discretization_cnt=None):
    return msm_model.MSM_Environment(setpoint_limits=(0.003, 0.012),
                                     #force_limits=(1, 10),
                                     simulation_time=0.05,
                                     )


# Use the NN network phenotype and the discrete actuator force function.
def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    fitness_list = []
    env = msm_model.MSMSimPool.get_instance(make_env)

    for i in range(runs_per_net):
        obs, _ = env.reset()
        done = False
        total_reward = 0
        while not done:
            obs = np.expand_dims(obs, axis=0)
            prediction = net.activate(obs[0, :])
            obs, reward, terminated, truncated, info = env.step(prediction[0])
            done = terminated or truncated
            total_reward += reward
        mean_run_reward = total_reward / env.cur_step  # normalizing reward in case of variable training duration
        fitness_list.append(mean_run_reward)

    msm_model.MSMSimPool.release_instance(env)
    fitness = np.min(fitness_list)

    # The genome's fitness is its worst performance across all runs.
    return float(fitness)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run(folder_name, new_training, checkpoint_name=""):
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    if new_training:
        pop = neat.Population(config)
    else:
        pop = neat.Checkpointer.restore_checkpoint(os.path.join(save_folder_name, checkpoint_name))
        #config.species_set_config.max_stagnation = 200
        #pop.config = config  # this line does not allow normal intializtion and training. It results in error after two or three generations

    model_save_prefix = os.path.join(folder_name, "checkpoint-")
    checkpointer = neat.Checkpointer(generation_interval=10, filename_prefix=model_save_prefix)

    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(False))
    pop.add_reporter(checkpointer)

    pe = neat.ParallelEvaluator(8, eval_genome)  # multiprocessing.cpu_count()
    winner = pop.run(pe.evaluate)

    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)

    # visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
    # visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")
    #
    # node_names = {-1: 'x', -2: 'dx', -3: 'theta', -4: 'dtheta', 0: 'control'}
    # visualize.draw_net(config, winner, True, node_names=node_names)
    #
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward.gv")
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)


if __name__ == '__main__':
    save_folder_name = utils.NEAT_FOLDER
    new_training = False
    run(save_folder_name, new_training, checkpoint_name="checkpoint-1286")




"""
#   --- GPU NEAT --- (requires jitable function of environment

from tensorneat.pipeline import Pipeline
from tensorneat.algorithm.neat import NEAT
from tensorneat.genome import DefaultGenome, BiasNode

from tensorneat.common import ACT, AGG
import msm_model

# Define the pipeline
pipeline = Pipeline(
    algorithm=NEAT(
        pop_size=1000,
        species_size=20,
        survival_threshold=0.1,
        compatibility_threshold=1.0,
        genome=DefaultGenome(
            num_inputs=60,  # TODO make dependent on Environment parameters
            num_outputs=1,
            max_nodes=1000,
            init_hidden_layers=(),
            node_gene=BiasNode(
                activation_options=ACT.tanh,
                aggregation_options=AGG.sum,
            ),
            output_transform=ACT.tanh,
        ),
    ),
    problem=msm_model.MSM_Environment(randomize_setpoint=False),
    seed=42,
    generation_limit=100,
    fitness_target=-1,
)

# Initialize state
state = pipeline.setup()

# Run until termination
state, best = pipeline.auto_run(state)

print('state\n', state)
print('best')
"""