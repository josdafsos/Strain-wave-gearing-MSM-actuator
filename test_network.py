import os
import pickle

import neat
from simple_pid import PID
from stable_baselines3 import SAC, DQN
#import visualize
import msm_model
import mujoco_viewer
import neat_training
import utils
import time
import numpy as np

import matplotlib.pyplot as plt


def make_env(action_discretization_cnt=None):
    return msm_model.MSM_Environment(setpoint_limits=0.014, simulation_time=0.30, action_discretization_cnt=action_discretization_cnt)


def run_sim(model, predict_func, model_params, render_environment, enable_plots):
    if model_params[0] == "dqn":
        env = make_env(action_discretization_cnt=20)
    else:
        env = make_env()
    obs, _ = env.reset()
    result = {}

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

    if len(model_params) > 2:
        label = model_params[0] + " " + model_params[2]
    else:
        label = model_params[0]
    steady_state_idx = int(0.02 / utils.NN_WORKING_FREQUENCY)
    steady_state_vel = env.environment.simulation_data["rack_vel"][steady_state_idx:]
    steady_state_desired_vel = env.environment.simulation_data["velocity_setpoint"][
                               steady_state_idx:]
    control_error = np.sum((steady_state_vel - steady_state_desired_vel) ** 2)
    print(f"{label} steady state mse {control_error}")
    result["velocity mse"] = control_error

    if enable_plots:
        env.environment.plot_rack_instant_velocity()
        env.environment.plot_rack_average_velocity()
        env.environment.plot_control_value()


    return env, result


def run_neat(model_params, render_environment=True, enable_plots=False):
    print("running neat")
    save_prefix = 'neatsave_'
    save_prefix_len = len(save_prefix) - 1
    model_name = model_params[1]
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

    env = run_sim(net, predict_func, model_params, render_environment, enable_plots)


    # visualize.draw_net(config, winner, True, node_names=node_names)
    #
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward.gv")
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)
    return env


def run_pid(model_params, render_environment=True, enable_plots=False):
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

    env = run_sim(pid, predict_func, model_params, render_environment, enable_plots)

    return env


def run_sac(model_params, render_environment=True, enable_plots=False):
    print("running sac")
    model_name = model_params[1]
    model = SAC.load(os.path.join('sb_neural_networks', "sac", model_name))

    def predict_func(model, env, obs):
        action, _states = model.predict(obs)
        return action

    env = run_sim(model, predict_func, model_params, render_environment, enable_plots)

    return env

def run_dqn(model_params, render_environment=True, enable_plots=False):
    print("running sac")
    model_name = model_params[1]
    model = DQN.load(os.path.join('sb_neural_networks', "dqn", model_name))

    def predict_func(model, env, obs):
        action, _states = model.predict(obs)
        return action

    env = run_sim(model, predict_func, model_params, render_environment, enable_plots)

    return env

if __name__ == '__main__':
    # network types: # "neat" "sac" "ppo" "pid"
    networks = []  # list of tuples with (network type, filename, <optional> name prefix)
    #networks.append(("neat", "neatsave_5kHz_70_obs_4_01_fitness_0_06_seconds_checkpoint-2932", "4.01 fit"))
    networks.append(("neat", "neatsave_5khz_70obs_4_02_fitness_0_06_seconds_checkpoint-2750", "4.02_fit"))
    # networks.append(("sac", "1000000_network_03_07_25_"))
    # networks.append(("dqn", "1000000_network_03_10_25_"))
    networks.append(("pid", ""))
    plot_comparisons = True

    network_dict = {
        "neat": run_neat,
        "pid": run_pid,
        "sac": run_sac,
        "dqn": run_dqn,
    }
    processed_environments, results = [], []
    execution_time = time.time()
    for network in networks:
        processed_env, result = network_dict[network[0]](network,
                                 render_environment=True,
                                 enable_plots=False)
        processed_environments.append(processed_env)
        results.append(result)
    execution_time = time.time() - execution_time
    print(f"All simulations completed in {execution_time} seconds")
    if plot_comparisons:
        plt.figure(figsize=(8, 4))
        for i in range(len(networks)):
            time_vec = processed_environments[i].environment.simulation_data["time"][1:]
            instant_vel_vec = processed_environments[i].environment.simulation_data["rack_vel"][1:]
            desired_vel_vec = processed_environments[i].environment.simulation_data["velocity_setpoint"][1:]
            # Plot results
            if len(networks[i]) > 2:
                plot_label = networks[i][0] + " " + networks[i][2]
            else:
                plot_label = networks[i][0]
            plt.plot(time_vec, instant_vel_vec, label=plot_label + " Rack Velocity, m/s")
            if len(desired_vel_vec) > utils.sequence_length and i == 0:
                plt.plot(time_vec, desired_vel_vec, label="Desired Velocity, m/s")
            steady_state_idx = int(0.02 / utils.NN_WORKING_FREQUENCY)
            steady_state_vel = processed_environments[i].environment.simulation_data["rack_vel"][steady_state_idx:]
            steady_state_desired_vel = processed_environments[i].environment.simulation_data["velocity_setpoint"][steady_state_idx:]
            control_error = np.sum((steady_state_vel - steady_state_desired_vel)**2)
            #print(f"{plot_label} steady state mse {control_error}")
        plt.xlabel("Time (s)")
        plt.ylabel("Instant Velocity")
        plt.title("Instant velocity Over Time")
        plt.legend()
        plt.grid()
        plt.show()
