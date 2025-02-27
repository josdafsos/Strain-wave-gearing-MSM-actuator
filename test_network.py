import os
import pickle

import neat
import msm_model
import mujoco_viewer

def make_env():
    return msm_model.MSM_Environment(randomize_setpoint=False)


def run_neat(model_name):
    env = make_env()
    with open('winner-feedforward', 'rb') as f:
        c = pickle.load(f)

    print('Loaded genome:')
    print(c)
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    net = neat.nn.FeedForwardNetwork.create(c, config)

    viewer = mujoco_viewer.MujocoViewer(env.environment.model, env.environment.data)
    viewer.cam.azimuth = 180
    viewer.cam.distance = 0.005

    obs, _ = env.reset()
    # env.velocity_setpoint = 0.006  # if not set explicitly the default constant setpoint will be used

    while viewer.is_alive:
        action = net.activate(obs[0, :])
        action = action[0]
        obs, reward, terminated, truncated, info = env.step(action)
        viewer.render()
    viewer.close()

    env.environment.plot_rack_instant_velocity()
    env.environment.plot_rack_average_velocity()
    env.environment.plot_control_value()


if __name__ == '__main__':
    network_name = ""
    network_type = "neat"  # "neat" "sac" "ppo"

