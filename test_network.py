import os
import pickle

import neat
from simple_pid import PID
from stable_baselines3 import SAC, DQN
import visualize
import msm_model
import mujoco_viewer
import neat_training
import utils
import time
import numpy as np

import matplotlib.pyplot as plt


def make_env(action_discretization_cnt=None):
    global velocity_setpoint
    return msm_model.MSM_Environment(setpoint_limits=velocity_setpoint, simulation_time=0.30, action_discretization_cnt=action_discretization_cnt)


def run_sim(model, predict_func, model_params, render_environment, enable_plots):
    if model_params["type"] == "dqn":
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
            if not viewer.is_alive:
                break
            viewer.render()

    if render_environment:
        viewer.close()

    if "postfix" in model_params.keys():
        label = model_params["type"] + " " + model_params["postfix"]
    else:
        label = model_params["type"]
    steady_state_idx = int(0.02 / utils.NN_WORKING_FREQUENCY)
    steady_state_vel = env.environment.simulation_data["rack_vel"][steady_state_idx:]
    steady_state_desired_vel = env.environment.simulation_data["velocity_setpoint"][
                               steady_state_idx:]
    control_error = np.sum((steady_state_vel - steady_state_desired_vel) ** 2) / len(steady_state_vel)
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
    model_name = model_params["file"]
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
    # node_names = {-5: 'links', -4: 'halblinks', -3: 'vorne', -2: 'halbrechts', -1: 'rechts', 0: 'nach links',
    #               1: 'nach rechts'}  # this is just an example of node naming

    visualize.draw_net(config, winner, True) #, node_names=node_names)

    # visualize.draw_net(config, winner, view=True, #node_names=node_names,
    #                    filename="winner-feedforward.gv")
    visualize.draw_net(config, winner, view=True, #node_names=node_names,
                       filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)
    return env


def plot_velocity_mse(networks):
    plt.figure(figsize=(8, 4))
    for network in networks:
        mse_mat = np.array(network["velocity mse"])
        velocity = mse_mat[:, 0]
        mse = mse_mat[:, 1]
        # Plot results
        # cur_network = networks[i % len(networks)]
        if "postfix" in network.keys():
            plot_label = network["type"] + " " + network["postfix"]
        else:
            plot_label = network["type"]
        plt.plot(velocity, mse, label=plot_label)

    plt.xlabel("Desired velocity m/s")
    plt.ylabel("Velocity MSE (m/s)^2")
    plt.title("Velocity MSE vs desired velocity")
    plt.legend()
    plt.grid()
    plt.show()

def plot_velocity_tracking(processed_environments):
    plt.figure(figsize=(8, 4))
    for i in range(len(processed_environments)):
        time_vec = processed_environments[i].environment.simulation_data["time"][1:]
        instant_vel_vec = processed_environments[i].environment.simulation_data["rack_vel"][1:]
        desired_vel_vec = processed_environments[i].environment.simulation_data["velocity_setpoint"][1:]
        # Plot results
        cur_network = networks[i % len(networks)]
        if "postfix" in cur_network.keys():
            plot_label = cur_network["type"] + " " + cur_network["postfix"]
        else:
            plot_label = cur_network["type"]
        plt.plot(time_vec, instant_vel_vec, label=plot_label)
        if len(desired_vel_vec) > utils.sequence_length and i % len(networks) == 0:
            plt.plot(time_vec, desired_vel_vec, label="Desired Velocity, m/s")
    plt.xlabel("Time (s)")
    plt.ylabel("Instant Rack Velocity, m/s ")
    plt.title("Instant Velocity Over Time")
    plt.legend()
    plt.grid()
    plt.show()

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
    model_name = model_params["file"]
    model = SAC.load(os.path.join('sb_neural_networks', "sac", model_name))

    def predict_func(model, env, obs):
        action, _states = model.predict(obs)
        return action

    env = run_sim(model, predict_func, model_params, render_environment, enable_plots)

    return env

def run_dqn(model_params, render_environment=True, enable_plots=False):
    print("running dqn")
    model_name = model_params["file"]
    model = DQN.load(os.path.join('sb_neural_networks', "dqn", model_name))

    def predict_func(model, env, obs):
        action, _states = model.predict(obs)
        return action

    env = run_sim(model, predict_func, model_params, render_environment, enable_plots)

    return env

if __name__ == '__main__':
    # network types: # "neat" "sac" "ppo" "pid"
    networks = []  # list of tuples with (network type, filename, <optional> name prefix)
    networks.append({"type": "neat", "file": "neatsave_5kHz_70_obs_4_01_fitness_0_06_seconds_checkpoint-2932", "postfix": "4.01 fit"})
    #networks.append({"type": "neat", "file": "neatsave_5khz_70obs_4_02_fitness_0_06_seconds_checkpoint-2750", "postfix": "4.02_fit"})
    #networks.append({"type": "neat", "file": "neatsave_4khz_70obs_checkpoint-482_fitness_0_12351", "postfix": "4khz"})
    # 1000000_network_03_12_25_Ming
    # networks.append({"type": "sac", "file": "FIRST_SUCCESS_SAC_7500000_steps_0_08_setpoint"})
    #networks.append({"type": "dqn", "file": "STABLE_0_008_setpoint_1000000_network_03_10_25_", "postfix": "stable"})
    #networks.append({"type": "dqn", "file": "dqn_70_obs_4000_Hz_freq_1000000_network_9_68_fit", "postfix": "new"})
    # networks.append({"type": "dqn", "file": "1000000_network_03_12_25_Ming", "postfix": "new"})
    # networks.append({"type": "pid", "file": ""})
    plot_comparisons = False
    velocity_range = 0.008  # (0.005, 0.010)
    #velocity_range = np.linspace(0.006, 0.010, 3)
    render_environment = False
    enable_individual_plots = False


    # --- protected part ---
    network_dict = {
        "neat": run_neat,
        "pid": run_pid,
        "sac": run_sac,
        "dqn": run_dqn,
    }
    processed_environments, results = [], []
    execution_time = time.time()

    velocity_setpoint = None
    if isinstance(velocity_range, float) or len(velocity_range) == 2:
        velocity_setpoint = velocity_range
        for network in networks:
            processed_env, result = network_dict[network["type"]](network,
                                     render_environment=render_environment,
                                     enable_plots=enable_individual_plots)
            processed_environments.append(processed_env)
            results.append(result)
    else:
        for velocity in velocity_range:
            for network in networks:
                if not "velocity mse" in network.keys():
                    network["velocity mse"] = []
                velocity_setpoint = velocity
                processed_env, result = network_dict[network["type"]](network,
                                         render_environment=render_environment,
                                         enable_plots=enable_individual_plots)
                processed_environments.append(processed_env)
                results.append(result)
                network["velocity mse"].append((velocity, result["velocity mse"]))


    execution_time = time.time() - execution_time
    print(f"All simulations completed in {execution_time} seconds")



    if plot_comparisons:
        # plot_velocity_mse(networks)
        plot_velocity_tracking(processed_environments)

