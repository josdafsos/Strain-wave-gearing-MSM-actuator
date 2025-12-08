**The project contains tools to design and simulate strain wave gearing magnetic shape memory alloy (SWG-MSM) based actuators.**

*In some bright distant future there will be a good documentation for the project, but for now we have what we have.*

<details>
  <summary>"sim_and_control" folder contains scripts to simulate SWG-MSM actuators using MuJoCo or Matlab environments. Also provides tools to develop and test controllers for the actuators.
</summary>

  - msm_model.py - Complete model of the actuator + actuator's environment

  - sb_learning.py - Script to train RL agents using Stable Baselines library

  - test_network.py - Script to test various controllers with the actuator environment.

  - Other tested methods NEAT; evolutionary and other non-gradient based optimization technics.

</details>


<details>
<summary> "experimental_data" folder contains data files and code to proces the data
</summary>

 - To use the experimental data, use process_data.py. Put the IDs (.csv file names without the extension) of the data into corresponding list. 
 - To process new data use preprocess_csv.py. Put the new data into a folder inside "experimental_data", run the script with the selected file prefix.
All .csv files inside the folder will be copied and renamed with prefix going first and then a file index. Also .csv files will be restructured.
Then add .json with the description of each measurement. The measurement can contain data units, scaling, offset, plotting preferences and more, see process_data.py header for more details.

</details>

"microcontroller" folder contains code used for the control PCB and other related software.

The repository was originally created by Ivan Kulagin as a part of PhD research.