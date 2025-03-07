import os
import pickle

import neat
from simple_pid import PID
from stable_baselines3 import SAC
#import visualize
import msm_model
import mujoco_viewer
import neat_training
import utils
import time

import matplotlib.pyplot as plt

def make_env():
    return msm_model.MSM_Environment(randomize_setpoint=False)

def show_plots(environment, enable_plots):
    if not enable_plots:
        return
    environment.environment.plot_rack_instant_velocity()
    environment.environment.plot_rack_average_velocity()
    environment.environment.plot_control_value()

def run_sim(model, predict_func, render_environment):
    env = make_env()
    obs, _ = env.reset()

    if render_environment:
        viewer = mujoco_viewer.MujocoViewer(env.environment.model, env.environment.data)
        viewer.cam.azimuth = 180
        viewer.cam.distance = 0.005
    while True:  # viewer.is_alive:
        vel = env.environment.simulation_data["rack_vel"]
        control_error = vel[-1] - env.velocity_setpoint
        # print(f"control error: {control_error}")
        action = predict_func(model, env, obs)
        # prediction = 1
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
        if render_environment:
            viewer.render()

    if render_environment:
        viewer.close()

    return env


def run_neat(model_name, render_environment=True, enable_plots=False):
    print("running neat")
    save_prefix = 'neatsave_'
    save_prefix_len = len(save_prefix) - 1

    if len(model_name) < save_prefix_len or model_name[:save_prefix_len] != save_prefix[:-1]:
        save_name = os.path.join(utils.NEAT_FOLDER, save_prefix + model_name)
        pop = neat.Checkpointer.restore_checkpoint(os.path.join(utils.NEAT_FOLDER, model_name))
        pe = neat.ParallelEvaluator(8, neat_training.eval_genome)
        winner = pop.run(pe.evaluate, 1)
        with open(save_name, 'wb') as f:
            pickle.dump(winner, f)
    else:
        save_name = os.path.join(utils.NEAT_FOLDER, model_name)
        with open(save_name, 'rb') as f:
            winner = pickle.load(f)


    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # print(winner)
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    def predict_func(model, env, obs):
        action = model.activate(obs)
        action = action[0]
        return action

    env = run_sim(net, predict_func, render_environment)
    show_plots(env, enable_plots)

    # visualize.draw_net(config, winner, True, node_names=node_names)
    #
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward.gv")
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)
    return env


def run_pid(model_name, render_environment=True, enable_plots=False):
    print("running pid")
    pid = PID(6, 20000, 8e-5)  # PID(6, 20000, 8e-5)
    pid.sample_time = utils.NN_WORKING_PERIOD
    pid.proportional_on_measurement = False
    pid.differential_on_measurement = False
    def predict_func(model, env, obs):
        vel = env.environment.simulation_data["rack_vel"][-1]
        control_error = vel - env.velocity_setpoint
        # print(f"control error: {control_error}")
        action = model(control_error, dt=utils.NN_WORKING_PERIOD)
        return action

    env = run_sim(pid, predict_func, render_environment)

    show_plots(env, enable_plots)

    return env


def run_sac(model_name, render_environment=True, enable_plots=False):
    print("running sac")
    model = SAC.load(os.path.join('sb_neural_networks', model_name))

    def predict_func(model, env, obs):
        action, _states = model.predict(obs)
        return action

    env = run_sim(model, predict_func, render_environment)
    show_plots(env, enable_plots)

    return env

if __name__ == '__main__':
    # network types: # "neat" "sac" "ppo" "pid"
    networks = []  # list of tuples with (network type, filename)
    networks.append(("neat", "checkpoint-6490_fitness_around_8500_stepoint_[0_007__0_009]"))
    # networks.append(("sac", "1000000_network_03_07_25_"))
    #networks.append(("pid", ""))

    network_dict = {
        "neat": run_neat,
        "pid": run_pid,
        "sac": run_sac,
    }
    processed_environments = []
    execution_time = time.time()
    for network in networks:
        processed_environments.append(network_dict[network[0]](network[1],
                                                               render_environment=True,
                                                               enable_plots=True))
    execution_time = time.time() - execution_time
    print(f"All simulations completed in {execution_time} seconds")

    plt.figure(figsize=(8, 4))
    for i in range(len(networks)):
        time_vec = processed_environments[i].environment.simulation_data["time"][1:]
        instant_vel_vec = processed_environments[i].environment.simulation_data["rack_vel"][1:]
        desired_vel_vec = processed_environments[i].environment.simulation_data["velocity_setpoint"][1:]
        # Plot results
        plt.plot(time_vec, instant_vel_vec, label=networks[i][0] + " Rack Velocity, m/s")
        if len(desired_vel_vec) > utils.sequence_length and i == 0:
            plt.plot(time_vec, desired_vel_vec, label="Desired Velocity, m/s")
    plt.xlabel("Time (s)")
    plt.ylabel("Instant Velocity")
    plt.title("Instant velocity Over Time")
    plt.legend()
    plt.grid()
    plt.show()
