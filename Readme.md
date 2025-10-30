*In some bright distant future there will be a good documentation for the project, but for now we have what we have.*

**The project contains tools to design and simulate strain wave gearing magnetic shape memory alloy (SWG-MSM) based actuators.**

<details>
  <summary>"sim_and_control" folder contains scripts to simulate SWG-MSM actuators using MuJoCo or Matlab environments. Also provides tools to develop and test controllers for the actuators.
</summary>

  - msm_model.py - Complete model of the actuator + actuator's environment

  - sb_learning.py - Script to train RL agents using Stable Baselines library

  - test_network.py - Script to test various controllers with the actuator environment.

  - Other tested methods NEAT; evolutionary and other non-gradient based optimization technics.

</details>

"experimental_data" folder contains data files and code to proces the data

"microcontroller" folder contains code used for the control PCB and other related software.