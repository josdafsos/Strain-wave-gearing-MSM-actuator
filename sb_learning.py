import numpy as np
from torch.utils.checkpoint import checkpoint

import msm_model
from sb3_contrib import RecurrentPPO, ARS
from stable_baselines3 import PPO, SAC, DQN, TD3
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecMonitor
from stable_baselines3.common import results_plotter
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
import os
import mujoco_viewer
import torch
from datetime import datetime
import matplotlib.pyplot as plt
import gymnasium as gym


import utils


class RewardLoggerCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self):
        return True
        rewards = self.training_env.get_attr("total_reward")
        if rewards:
            print(f"Episode Rewards: {rewards}")
        return True



def make_env():
    global reward_log_list, log_dir
    # if Monitor class is used, access environment via env.get_env()
    # return gym.make('CartPole-v1')
    return msm_model.MSM_Environment(simulation_time=0.03, setpoint_limits=(0.006, 0.010), action_discretization_cnt=20)
    # return Monitor(msm_model.MSM_Environment(randomize_setpoint=True), log_dir)

def plot_rewards_history(vec_env):
    min_len = 0
    reward_matrix = vec_env.get_attr("episode_reward_list")
    for i in range(len(reward_matrix)):  # need to equalize sizes of the vector
        min_len = min(min_len, len(reward_matrix[i]))
    for i in range(len(reward_matrix)):
        reward_matrix[i] = reward_matrix[i][-min_len:]
    rewards = np.transpose(np.array(reward_matrix))
    mean_rewards = np.mean(rewards, axis=1)
    mean_rewards = mean_rewards[1:]
    reward_steps = [i for i in range(len(mean_rewards))]

    plt.figure(figsize=(10, 5))
    plt.plot(reward_steps, mean_rewards)
    plt.xlabel("Episodes x Number of Cores")
    plt.ylabel("Average reward per episode set")
    plt.title("Reward history")
    plt.grid()
    plt.show()

def get_dqn_model(model_name, vec_env, device, learning_rate):
    policy_kwargs = dict(
        net_arch=[256, 256],  # hidden layers with VALUE neurons each
        # activation_fn=torch.nn.ReLU
        activation_fn=torch.nn.ELU
    )

    if model_name == "":
        print("creating new DQN model")
        model = DQN("MlpPolicy",
                    vec_env,
                    device=device,
                    learning_rate=learning_rate,
                    policy_kwargs=policy_kwargs,
                    gradient_steps=-1,  #-1,  # suggested by Ming, default 1
                    batch_size=256,
                    verbose=1,)
    else:
        print("Loading DQN model for training")
        custom_objects = {'learning_rate': learning_rate}
        model = DQN.load(os.path.join('sb_neural_networks', 'dqn', model_name), vec_env, custom_objects=custom_objects)
        model.set_env(vec_env)
    return model

def get_ppo_model(model_name, vec_env, device, learning_rate):
    policy_kwargs = dict(
        net_arch=dict(pi=[256, 256],
                      vf=[256]),  # hidden layers with VALUE neurons each
        # activation_fn=torch.nn.ReLU
        activation_fn=torch.nn.ELU
    )

    if model_name == "":
        print("creating new PPO model")
        model = PPO("MlpPolicy",
                   vec_env,
                   device=device,
                   learning_rate=learning_rate,
                   policy_kwargs=policy_kwargs,
                   batch_size=256,
                   n_steps=4096,
                   verbose=1)
    else:
        print("Loading PPO model for training")
        custom_objects = {'learning_rate': learning_rate}
        model = PPO.load(os.path.join('sb_neural_networks', 'ppo', model_name), vec_env, custom_objects=custom_objects)
        model.set_env(vec_env)
    return model

def get_sac_model(model_name, vec_env, device, learning_rate):
    policy_kwargs = dict(
        net_arch=dict(pi=[256, 256],
                      # vf=[256]),
                      qf=[256]),  # hidden layers with VALUE neurons each
        # activation_fn=torch.nn.ReLU
        activation_fn=torch.nn.ELU
    )
    if model_name == "":
        print("creating new SAC model")
        model = SAC("MlpPolicy",
                    vec_env,
                    device=device,
                    learning_rate=learning_rate,
                    policy_kwargs=policy_kwargs,
                    batch_size=64,
                    verbose=1)
    else:
        print("Loading SAC model for training")
        custom_objects = {'learning_rate': learning_rate}
        model = TD3.load(os.path.join('sb_neural_networks', 'td3', model_name), vec_env, custom_objects=custom_objects)
        model.set_env(vec_env)
    return model

def get_td3_model(model_name, vec_env, device, learning_rate):
    policy_kwargs = dict(
        net_arch=dict(pi=[256,],
                      # vf=[256]),
                      qf=[128,]),  # hidden layers with VALUE neurons each
        # activation_fn=torch.nn.ReLU
        activation_fn=torch.nn.ELU
    )
    if model_name == "":
        print("creating new TD3 model")
        model = TD3("MlpPolicy",
                    vec_env,
                    device=device,
                    learning_rate=learning_rate,
                    policy_kwargs=policy_kwargs,
                    batch_size=1024,
                    verbose=1)
    else:
        print("Loading TD3 model for training")
        custom_objects = {'learning_rate': learning_rate}
        model = TD3.load(os.path.join('sb_neural_networks', 'td3', model_name), vec_env, custom_objects=custom_objects)
        model.set_env(vec_env)
    return model

if __name__ == '__main__':

    # TODO try TD3 (or an older version DDPG)
    # TODO try TRPO
    # TODO at a new tooth engagement, there is an unrealistic oscillations. Try to adjust sim parameters to avoid this effect

    model_name = ""  # leave empty if a new model must be trained
    model_name = "fitness_12_8_test_set_8_dqn_32_obs_4000_Hz_freq_4000000_network_03_19_25"
    model_type = "dqn"  # sac, ppo,

    model_dict = {
        "sac": get_sac_model,  # difficult to train, possible to reach controllability with relatively high error
        "ppo": get_ppo_model,
        "dqn": get_dqn_model,  # dqn (can control with relatively high error)
        "td3": get_td3_model,  # td3 (does not learn)
    }

    if hasattr(torch, 'accelerator') and torch.accelerator.is_available():
        device = torch.accelerator.current_accelerator().type
    else:
        device = 'cpu'
    #device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
    print(f"Current device: {device}")

    log_dir = 'logs'
    learning_rate = 1e-4  # 1e-9 not yet tested; 1e-8 not working well
    # TODO add action noise to parametrs if it is possible with a policy

    env = make_env()

    # Vectorized environment setup
    num_envs = 200  # Number of parallel environments
    vec_env = SubprocVecEnv([make_env for _ in range(num_envs)])  # Or use DummyVecEnv([make_env])
    vec_env = VecMonitor(vec_env)
    timesteps = int(1e7)
    if num_envs == 1:
        vec_env = env
    """
    if model_name == "":
        # model = RecurrentPPO("MlpLstmPolicy", vec_env, learning_rate=1e-3, verbose=1)  # instead use normal PPO with frame stacking
        # model = ARS("MlpPolicy", vec_env, device=device,learning_rate=learning_rate, policy_kwargs=policy_kwargs, verbose=1)
    """

    model = model_dict[model_type](model_name, vec_env, device, learning_rate)

    obs_cnt = env.total_obs_cnt
    checkpoint_callback = CheckpointCallback(
        save_freq=int(2e4),
        save_path='./sb_neural_networks/' + model_type + '/',  # './sb_neural_networks/3_512_layers_with_5_sets/'
        name_prefix=f"{model_type}_{obs_cnt}_obs_{utils.NN_WORKING_FREQUENCY}_Hz_freq"
    )

    # Train the agent
    print(model.policy)
    model.learn(total_timesteps=timesteps,
                progress_bar=True,
                callback=checkpoint_callback,
                reset_num_timesteps=False
                #callback=RewardLoggerCallback()
                )
    # Save the agent
    if model_name == "":
        model_name = f"{model_type}_{obs_cnt}_obs_{utils.NN_WORKING_FREQUENCY}_Hz_freq_{timesteps}_network_" + datetime.now().strftime("%D_").replace("/", "_")
    else:
        model_name = model_name + "_new"
    model.save(os.path.join('sb_neural_networks', model_type, model_name))

    plot_rewards_history(vec_env)
    print(model.policy)


    # print(utils.reward_list)
    # msm_model.MSM_Environment.plot_expected_reward_history(utils.reward_list)


