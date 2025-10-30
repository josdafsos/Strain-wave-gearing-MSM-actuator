"""
    The script is used to test variety of agents controlling MSM strain wave actuator.
    Actuators can be tested against range of forces, range of reference velocities
    and range of reference positions, including complex reference profiles.
    All settings are made in the corresponding section of script entry point at the bottom of the script.
    At the same part of the code, there is also annotation in the comment which agents are currently supported.
    Adjust make_env function for setting up a desired environment.
"""

import os
import pickle

import neat
from simple_pid import PID
from stable_baselines3 import SAC, DQN, PPO
import visualize
import msm_model
import mujoco_viewer
import neat_training
import utils
import time
import numpy as np

import matplotlib.pyplot as plt


def make_env(action_discretization_cnt=None, is_sign_inversed=False, enable_filtering=False):
    global velocity_setpoint, external_force
    return msm_model.MSM_Environment(setpoint_limits=velocity_setpoint,
                                     force_limits=external_force,
                                     simulation_time=0.06,  # 0.06
                                     action_discretization_cnt=action_discretization_cnt,  # for discrete action space
                                     enable_action_filtering=enable_filtering,  # useful for discrete action space
                                     inverse_sign_on_negative_ref=is_sign_inversed,
                                     )


def run_sim(model, predict_func, model_params, render_environment, enable_plots):
    global current_position_controller, position_trajectory, is_position_control  # quick and dirty, sry whoever is working with it


    if model_params["type"] == "dqn":
        env = make_env(action_discretization_cnt=20, is_sign_inversed=True, enable_filtering=False)  # TODO for pure agent comparison filtering was disabled
    else:
        env = make_env()
    obs, _ = env.reset()
    result = {}

    if is_position_control:
        print(f"current position controller: {current_position_controller}")
        pos_pid = PID(current_position_controller["kp"],
                      current_position_controller["ki"],
                      current_position_controller["kd"])  # PID(6, 20000, 8e-5)
        pos_pid.sample_time = utils.NN_WORKING_PERIOD
        pos_pid.proportional_on_measurement = False
        pos_pid.differential_on_measurement = False
        pos_traj_idx = 0

    action = 0
    old_action = 0
    if render_environment:
        viewer = mujoco_viewer.MujocoViewer(env.environment.model, env.environment.data)
        viewer.cam.azimuth = 180
        viewer.cam.distance = 0.005
    while True:  # viewer.is_alive:
        if is_position_control:
            pos = env.environment.simulation_data["rack_pos"][-1]
            control_error = pos - position_trajectory[pos_traj_idx]
            # env setpoint is updated on env.step() call, therefore there is one frame delay for the setpoint to update
            velocity_setpoint = pos_pid(control_error, dt=utils.NN_WORKING_PERIOD)
            if model_params["type"] == "dqn":
                velocity_setpoint = max(min(velocity_setpoint, 0.012), -0.012)  # the model was not trained for too high position reference

            env.velocity_setpoint = velocity_setpoint
            pos_traj_idx += 1
            pos_traj_idx %= len(position_trajectory)  # loop the trajectory

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
    steady_state_idx = int(0.02 * utils.NN_WORKING_FREQUENCY)
    steady_state_vel = env.environment.simulation_data["rack_vel"][steady_state_idx:]
    steady_state_desired_vel = env.environment.simulation_data["velocity_setpoint"][steady_state_idx:]
    control_error = np.sum( ((steady_state_vel - steady_state_desired_vel) * 1000) ** 2) / len(steady_state_vel)
    result["steady velocity mse"] = control_error
    result["steady velocity rmse"] = np.sqrt(control_error)

    transition_vel = env.environment.simulation_data["rack_vel"][:steady_state_idx]
    transition_desired_vel = env.environment.simulation_data["velocity_setpoint"][:steady_state_idx]
    control_error = np.sum( ((transition_vel - transition_desired_vel) * 1000) ** 2) / len(transition_vel)
    result["transition velocity mse"] = control_error
    result["transition velocity rmse"] = np.sqrt(control_error)

    result["rack position"] = env.environment.simulation_data["rack_pos"]

    ratio = len(env.environment.simulation_data["rack_pos"]) / len(position_trajectory)
    if ratio > 1:
        desired_position = list(position_trajectory) * (int(ratio) + 1)
    else:
        desired_position = position_trajectory

    result["rack position"] = env.environment.simulation_data["rack_pos"]
    result["reference position"] = desired_position
    result["time"] = env.environment.simulation_data["time"]
    rack_pos = env.environment.simulation_data["rack_pos"]
    desired_position = desired_position[:len(rack_pos)]
    #steady_rack_pos = rack_pos[1000:]
    #steady_desired_position = desired_position[1000:]

    #steady_position_control_error = np.sum( ((steady_desired_position - steady_rack_pos) * 1000) ** 2) / len(steady_rack_pos)
    #print(f"Steady RMSE for {label} = {np.sqrt(steady_position_control_error)} ")

    if enable_plots:
        env.environment.plot_rack_instant_velocity()
        env.environment.plot_rack_average_velocity()
        env.environment.plot_control_value()
        if is_position_control:
            env.environment.plot_rack_position(desired_position)


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
    if enable_plots:
        visualize.draw_net(config, winner, True) #, node_names=node_names)

        # visualize.draw_net(config, winner, view=True, #node_names=node_names,
        #                    filename="winner-feedforward.gv")
        visualize.draw_net(config, winner, view=True,  #node_names=node_names,
                           filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)
    return env

def preprocess_netwroks(networks):
    """
        Function to standartise existing networks
    """
    for idx, network in enumerate(networks):
        if "postfix" not in network.keys():
            network["postfix"] = ""

def plot_rmse_plots(networks):
    title_font = {'fontsize': 14, 'fontweight': 'bold'}
    label_font = {'fontsize': 14}
    legend_fontsize = 11
    tick_fontsize = 12

    # === Create Figure and Subplots ===
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs = axs.flatten()  # Make indexing easier
    plot_request_list = ["max transition velocity rmse",
                         "transition velocity rmse average force",
                         "max steady velocity rmse",
                         "steady velocity rmse average force",
                         ]
    plot_names_list = ["Transition state max RMSE",
                         "Transition state average RMSE",
                         "Steady state max RMSE",
                         "Steady state average RMSE",
                         ]

    legend_names = [network["type"].upper() + " " + network["postfix"] for idx, network in enumerate(networks)]

    for i in range(len(plot_request_list)):
        for idx, network in enumerate(networks):
            plot_request = plot_request_list[i]

            data_mat = np.array(network[utils.plot_info_dict[plot_request]["data"]])
            x_data = data_mat[:, 0]
            y_data = data_mat[:, 1]

            linestyle = '-'
            if network["type"] == 'pid':
                linestyle = '--'  # dashed line for pid for easier comparison
            plot_label = legend_names[idx]
            axs[i].plot(x_data, y_data, label=plot_label, linestyle=linestyle)

        plot_name = plot_names_list[i]
        axs[i].set_title(plot_name, **title_font)
        axs[i].set_xlabel(utils.plot_info_dict[plot_request]["xlable"], **label_font)
        axs[i].set_ylabel(utils.plot_info_dict[plot_request]["ylable"], **label_font)
        axs[i].tick_params(labelsize=tick_fontsize)
        axs[i].legend(fontsize=legend_fontsize)
        axs[i].set_xlim([1, 11])
        axs[i].grid()

    plt.tight_layout()
    plt.show()

def plot_positions(netwrosk):
    label_fontsize = 30  # for big screen 34
    legend_fontsize = 22  # 26
    tick_fontsize = 24  # 28

    # network[utils.plot_info_dict[plot_request]["data"]]
    labels = ["DQN + PID", "Cascade PID", "Re-trained DQN + PID"]
    plt.figure(figsize=(8, 4))
    for idx, network in enumerate(networks):
        time_vec = network["environment"].environment.simulation_data["time"]
        instant_pos_vec = 1000 * network["environment"].environment.simulation_data["rack_pos"]

        # Plot results
        # cur_network = networks[i % len(networks)]
        if "postfix" in network.keys():
            plot_label = network["type"] + " " + network["postfix"]
        else:
            plot_label = network["type"]
        if idx == 0:
            plt.plot(time_vec, instant_pos_vec, label=labels[idx])  #  linestyle='dotted'
        else:
            plt.plot(time_vec, instant_pos_vec, label=labels[idx])
        if idx % len(networks) == 0:
            desired_pos_vec = 1000 * np.array(network["reference position"])
            min_len = min(len(time_vec), len(desired_pos_vec))
            plt.plot(time_vec[:min_len], desired_pos_vec[:min_len],
                     label="Reference Position")

    plt.xlabel("Time (s)", fontsize=label_fontsize)  #, label_font=label_font)
    plt.ylabel("Rack Position (mm)", fontsize=label_fontsize)  # , label_font=label_font)
    plt.xticks(fontsize=tick_fontsize)
    plt.yticks(fontsize=tick_fontsize)
    plt.title("")
    plt.legend(fontsize=legend_fontsize, loc='lower right')  # 'upper right'
    plt.grid()
    plt.show()

def plot_networks_data(networks, plots=[]):
    """

    :param networks:
    :param plots: options: "steady velocity mse", "steady velocity rmse", "transition velocity mse", "transition velocity rmse"
    :return:
    """

    for plot_request in plots:
        plt.figure(figsize=(8, 4))
        for network in networks:
            #mse_mat = np.array(network["steady velocity rmse"])
            data_mat = np.array(network[utils.plot_info_dict[plot_request]["data"]])
            x_data = data_mat[:, 0]
            y_data = data_mat[:, 1]
            # Plot results
            # cur_network = networks[i % len(networks)]
            if "postfix" in network.keys():
                plot_label = network["type"] + " " + network["postfix"]
            else:
                plot_label = network["type"]
            linestyle = '-'
            if network["type"] == 'pid':
                linestyle = '--'  # dashed line for pid for easier comparison
            plt.plot(x_data, y_data, label=plot_label, linestyle=linestyle)

        plt.xlabel(utils.plot_info_dict[plot_request]["xlable"])
        plt.ylabel(utils.plot_info_dict[plot_request]["ylable"])
        plt.title(utils.plot_info_dict[plot_request]["title"])
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

def plot_rack_position(rack_pos_list, desired_pos_list):
    pass

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

def run_ppo(model_params, render_environment=True, enable_plots=False):
    print("running ppo")
    model_name = model_params["file"]
    model = PPO.load(os.path.join('sb_neural_networks', "ppo", model_name))

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
        action, _states = model.predict(obs, deterministic=True)
        return action

    env = run_sim(model, predict_func, model_params, render_environment, enable_plots)

    return env

def init_network_keys(network):
    network["steady velocity mse"] = []
    network["steady velocity rmse"] = []
    network["transition velocity mse"] = []
    network["transition velocity rmse"] = []
    network["steady velocity rmse average force"] = []
    network["transition velocity rmse average force"] = []
    network["max steady velocity rmse"] = []
    network["max transition velocity rmse"] = []

def run_all_networks(networks, velocity_range, force_range):
    global external_force, velocity_setpoint, position_controllers_list, is_position_control, current_position_controller
    # --- protected part ---
    network_dict = {
        "neat": run_neat,
        "pid": run_pid,
        "sac": run_sac,
        "dqn": run_dqn,
        "ppo": run_ppo,
    }
    processed_environments, results = [], []
    execution_time = time.time()

    if isinstance(velocity_range, float) or len(velocity_range) == 2 or is_position_control:
        velocity_setpoint = velocity_range
        for network in networks:

            # search for the matching controller
            for pos_controller in position_controllers_list:
                if pos_controller["id"] == network["id"]:
                    current_position_controller = pos_controller

                    break
            processed_env, result = network_dict[network["type"]](network,
                                     render_environment=render_environment,
                                     enable_plots=enable_individual_plots)
            processed_environments.append(processed_env)
            results.append(result)
            network["environment"] = processed_env
            network["reference position"] = result["reference position"]
    else:
        if isinstance(force_range, float):
            force_range = [force_range]
        for velocity in velocity_range:
            velocity_setpoint = velocity   # converting to mm/s
            for network in networks:
                if not "steady velocity mse" in network.keys():
                    init_network_keys(network)
                if not "environment" in network.keys():
                    network["environment"] = []
                transition_rmse_sum = 0
                steady_rmse_sum = 0
                max_transition_rmse = 0
                max_steady_rmse = 0

                for force in force_range:
                    external_force = force
                    processed_env, result = network_dict[network["type"]](network,
                                             render_environment=render_environment,
                                             enable_plots=enable_individual_plots)
                    processed_environments.append(processed_env)
                    network["environment"].append(processed_env)
                    results.append(result)
                    mm_velocity = velocity * 1000  # converting to mm/s
                    network["reference position"] = result["reference position"]
                    network["steady velocity mse"].append((mm_velocity, result["steady velocity mse"]))
                    network["steady velocity rmse"].append((mm_velocity, result["steady velocity rmse"]))
                    network["transition velocity mse"].append((mm_velocity, result["transition velocity mse"]))
                    network["transition velocity rmse"].append((mm_velocity, result["transition velocity rmse"]))
                    transition_rmse_sum += result["transition velocity rmse"]
                    steady_rmse_sum += result["steady velocity rmse"]
                    max_transition_rmse = max(max_transition_rmse, result["transition velocity rmse"])
                    max_steady_rmse = max(max_steady_rmse, result["steady velocity rmse"])

                network["transition velocity rmse average force"].append((mm_velocity, transition_rmse_sum / len(force_range)))
                network["steady velocity rmse average force"].append((mm_velocity, steady_rmse_sum / len(force_range)))
                network["max steady velocity rmse"].append((mm_velocity, max_steady_rmse))
                network["max transition velocity rmse"].append((mm_velocity, max_transition_rmse))

    execution_time = time.time() - execution_time
    print(f"All simulations completed in {execution_time} seconds")


if __name__ == '__main__':
    # Note the publication results are made with 60 milliseconds simulation time

    # --- manual settings ---
    load_existing_data = False
    data_to_load = 'ppo_sac_dqn_filtered_pid_80_steps.pickle'
    save_data = False  # if True data obtained during the nun will be saved
    is_position_control = False  # toggles position / velocity control mods, global variable
    plot_comparisons = True  # enables plotting of combined agents data selected at the bottom of the script
    render_environment = False  # enables visualization of the simulation
    enable_individual_plots = False  # separate individual plots will be shown after each experiment for every agent

    # --- agents ---
    # network types: # "neat" "sac" "ppo" "pid"
    networks = []  # list of tuples with (network type, filename, <optional> name prefix)
    position_controllers_list = []
    # networks.append({"type": "neat", "file": "neatsave_4khz_70obs_checkpoint-482_fitness_0_12351", "postfix": "4khz"})  # NOTE: USED in publication
    # test 3 SAC looks better than test 8
    networks.append({"type": "sac", "file": "sac_32_obs_4000_Hz_freq_6000000_network_06_19_25_reward16_4_experiment_3", })  # NOTE: USED IN PUBLICATION
    networks.append({"type": "ppo", "file": "ppo_32_obs_4000_Hz_freq_280000000_network_06_23_25", })  # NOTE: USED IN PUBLICATION

    # NOTE this could be used in the original paper instead of Run 17 DQN
    # networks.append(
    #     {"type": "dqn", "file": "experiment_16_dqn_32_obs_4000_Hz_freq_100000000",
    #      "postfix": "Force optimized, 3x256 layers"})
    # USED IN THE ORIGINAL PAPER:
    # networks.append(
    #     {"type": "dqn", "file": "run_17_dqn_32_obs_4000_Hz_freq_100000000_network_04_10_25_",
    #      "postfix": "Run 17, 3x256 layers"})  # !!!! NOTE in first control publication referred as "variable force trained DQN" !!!!!

    # networks.append(
    #     {"type": "dqn", "file": "semistable_outperformance_dqn_32_obs_4000_Hz_freq_97000000_steps_new_new",
    #      "postfix": "28_03, 3x256 layers", "id": 2})

    networks.append({"type": "pid", "file": "", "id": 1})  # NOTE: USED IN PUBLICATION

    # networks.append(
    #     {"type": "dqn", "file": "zero_vel_best_dqn_32_obs_4000_Hz_freq_158000000_steps",
    #      "postfix": "zero vel, 3x256 layers", "id": 3})
    # networks.append(
    #     {"type": "dqn", "file": "20_zero_vel_best_dqn_32_obs_4000_Hz_freq_97000000_steps_3e6_steps",
    #      "postfix": "zero vel 1e6, 3x256 layers", "id": 4})

    # Note this one is used in the publication as "constant force trained" use it for comparison
    networks.append(
        {"type": "dqn", "file": "run_20_best_dqn_32_obs_4000_Hz_freq_167000000_steps", "id": 4})
    # "postfix": "correct zero vel 1e7, 3x256 layers",  NOTE: USED IN PUBLICATION

    # pid pid, "pid" = 1
    position_controllers_list.append({"type": "position pid", "file": "", "id": 1, "kp": 27, "ki": 0, "kd": 0})  # original 27 0 0
    # dqn pid, "pid" = 2
    position_controllers_list.append({"type": "position pid", "file": "", "id": 2, "kp": 100, "ki": 0, "kd": 0}) # worked well with 40 # in original plot "kp": 100, "ki": 0, "kd": 0
    # zero dqn pid
    position_controllers_list.append({"type": "position pid", "file": "", "id": 3, "kp": 60, "ki": 0, "kd": 0})  # kinda good p50, i2, d1e-4
    # run 20 zero dqn pid
    position_controllers_list.append({"type": "position pid", "file": "", "id": 4, "kp": 100, "ki": 0, "kd": 0})

    # --- reference velocity and position settings ---
    # velocity_range = 0.005  # (0.005, 0.010)
    velocity_range = np.linspace(0.001, 0.011, 3)
    # force_range = -2.0
    force_range = np.linspace(-1, -5, 3)
    position_trajectory = []  # global variable
    x = np.linspace(0, 2*np.pi, 8000)
    y = (np.sin(x) + 1) / 1000
    position_trajectory = [0.001, 0.001]  # y  #
    # --- end of settings ---

    current_position_controller: dict | None = None  # global variable
    velocity_setpoint = None
    external_force = force_range
    data_folder = 'saved data'  # folder to which processed data is saved
    preprocess_netwroks(networks)

    # 'sine_position_dqn_vs_pid.pickle'
    # 'data_vel_1-11_100steps_force_1-5_10steps.pickle'
    # 'pid_only_position_step.pickle'
    # '1mm_step_dqn_vs_pid_0_5seconds.pickle'
    # '1mm_step_dqn_vs_pid_2_seconds.pickle'

    if load_existing_data:
        print("Loading existing data from ", data_to_load)
        with open(os.path.join(data_folder, data_to_load), 'rb') as handle:
            networks = pickle.load(handle)
    else:
        run_all_networks(networks, velocity_range, force_range)
        if save_data:
            with open(os.path.join(data_folder, 'new_training_data.pickle'), 'wb') as handle:
                pickle.dump(networks, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if plot_comparisons:
        plot_rmse_plots(networks)
        # plot_positions(networks)
        # plot_networks_data(networks, plots=[#"steady velocity rmse",
        #                                     #"transition velocity rmse",
        #                                     "steady velocity rmse average force",
        #                                     "transition velocity rmse average force",
        #                                     "max steady velocity rmse",
        #                                     "max transition velocity rmse"])
        # plot_velocity_tracking(processed_environments)

