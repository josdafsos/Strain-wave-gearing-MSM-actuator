import numpy as np
from torch.utils.checkpoint import checkpoint

import msm_model
from sb3_contrib import RecurrentPPO, ARS
from stable_baselines3 import PPO, SAC
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecMonitor
from stable_baselines3.common import results_plotter
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
import os
import mujoco_viewer
import torch
from datetime import datetime
import matplotlib.pyplot as plt


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

checkpoint_callback = CheckpointCallback(
    save_freq=int(5e4),
    save_path='./sb_neural_networks/3_512_layers_with_5_sets/',
    name_prefix='3_512_layers'
)

def make_env():
    global reward_log_list, log_dir
    # if Monitor class is used, access environment via env.get_env()
    return msm_model.MSM_Environment(randomize_setpoint=False)
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


if __name__ == '__main__':

    # TODO try TD3 (or an older version DDPG)

    model_name = ""  # leave empty if a new model must be trained
    #model_name = "FIRST_SUCCESS_SAC_7500000_steps_0_08_setpoint"
    if hasattr(torch, 'accelerator') and torch.accelerator.is_available():
        device = torch.accelerator.current_accelerator().type
    else:
        device = 'cpu'
    #device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
    print(f"Current device: {device}")

    log_dir = 'logs'
    learning_rate = 1e-9  # 1e-9 not yet tested; 1e-8 not working well
    # TODO add action noise to parametrs if it is possible with PPO


    # path = os.path.join('sb_neural_networks', 'sb_neural_network')
    # env = msm_model.MSM_Environment()  # randomize_setpoint=False
    env = make_env()

    policy_kwargs = dict(
#        net_arch=dict(pi=[512, 512, 512],
#                      vf=[512, 512, 512]),  # hidden layers with VALUE neurons each
        net_arch=dict(pi=[256, 256],
                      # vf=[256]),
                      qf=[256]),  # hidden layers with VALUE neurons each  # TODO try one hidden layer for critic
        #activation_fn=torch.nn.ReLU
        activation_fn = torch.nn.ELU
    )


    # Vectorized environment setup
    num_envs = 30  # Number of parallel environments
    vec_env = SubprocVecEnv([make_env for _ in range(num_envs)])  # Or use DummyVecEnv([make_env])
    vec_env = VecMonitor(vec_env)
    timesteps = int(3e6)
    if num_envs == 1:
        vec_env = env

    if model_name == "":
        print("creating new model")
        # model = RecurrentPPO("MlpLstmPolicy", vec_env, learning_rate=1e-3, verbose=1)  # instead use normal PPO with frame stacking
        # model = ARS("MlpPolicy",
        #             vec_env,
        #             device=device,
        #             learning_rate=learning_rate,
        #             #1policy_kwargs=policy_kwargs,
        #             verbose=1)
        #model = PPO("MlpPolicy",
        #            vec_env,
        #            device=device,
        #            learning_rate=learning_rate,
        #            policy_kwargs=policy_kwargs,
        #            batch_size=256,
        #            n_steps=4096,
        #            verbose=1)
        model = SAC("MlpPolicy",
                    vec_env,
                    device=device,
                    learning_rate=learning_rate,
                    policy_kwargs=policy_kwargs,
                    batch_size=64,
                    verbose=1)
    else:
        print("Loading model for training")
        custom_objects = {'learning_rate': learning_rate}
        # model = PPO.load(os.path.join('sb_neural_networks', model_name), custom_objects=custom_objects)
        model = SAC.load(os.path.join('sb_neural_networks', model_name), vec_env, custom_objects=custom_objects)
        model.set_env(vec_env)

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
        model_name = f"{timesteps}_network_" + datetime.now().strftime("%D_").replace("/", "_")
    else:
        model_name = model_name + "_new"
    model.save(os.path.join('sb_neural_networks', model_name))

    plot_rewards_history(vec_env)
    print(model.policy)


    # print(utils.reward_list)
    # msm_model.MSM_Environment.plot_expected_reward_history(utils.reward_list)


