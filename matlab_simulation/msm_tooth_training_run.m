function data_vec = msm_tooth_training_run(model_folder_name, sim_folder_path,...
    epsilon, seed)
% script to simulate and get position error of MSM tooth element.
    % epsilon: float [0, 1], defines the ration of random action and the
    % optimal ones. 1 - only random actions, 0 - only optimal actions

    % --- simulation control parameters ---
    external_load = 1; % TODO variable external force
    setpoint = 0.5; % TODO variable setpoint
    tooth_plates_cnt = 4; % Not important here
    pitch_type = "small"; % Not important here
    % TODO variable spring stiffness?
    
    sim_type = "push_spring";      % options:  "push_spring" "push_push_linear" "push_spring_rotation" "push_push_rotation"
    tb_type = 1;                        % Twin boundary type: options: 1 or 2
    SIMULATION_TIME = 0.04; % 0.06            % seconds
    simplified_visualization = false;    % poor visualization, but significantly faster computations   
    rng(seed);
    rand_seed_1 = randi([1 1e+7]); % for uncertainty in the desired position
    rand_seed_2 = randi([1 1e+7]); % for uncertainty in the external force
    tooth_random_initial_pos_coefficient = get_rand_initial_position();
    sine_phase = randi([1 1e+10]) / 100;
    trajectory_mode = randi([0 2]);
    % fitness parameters
%     tracking_margine = 0.03; % percents, defines how close MSM position to the setpoint needs to be to get a reward

    % preparing neural network
    % 'my_model' my_model2'
    modelFolder = strcat('ML_control', filesep, 'nn_models', filesep, model_folder_name);  % todo get full path from the function input argument
    if nargin < 2
        outputFolder = fullfile(pwd, modelFolder);
    else
        outputFolder = fullfile(sim_folder_path, modelFolder);
    end
    outputFile = fullfile(outputFolder, "net.mat");
    addpath(outputFolder);  % needed for the predict block to work correctly
    
    net = importTensorFlowNetwork(outputFolder, 'OutputLayerType', 'regression');
    save(outputFile, "net");


    % running simulation parameters
    % MSM_mechanism_simulation_properties
    sim_props = get_simulation_properties();
    msm_props = get_msm_properties(tb_type);
    tooth_props = get_tooth_properties(pitch_type, tb_type, sim_type,...
        tooth_plates_cnt, simplified_visualization, SIMULATION_TIME, msm_props);
    
    % initializing simulation and its parameters
    model = 'single_MSM_tooth_simulation';
    load_system(model)
    % set_param(model,'SimMechanicsOpenEditorOnUpdate','off')
    in = Simulink.SimulationInput(model);
    in = in.setVariable('setpoint', setpoint); in = in.setVariable('external_load', external_load);
    in = in.setVariable('tb_type', tb_type); in = in.setVariable('SIMULATION_TIME', SIMULATION_TIME);
    in = in.setVariable('simplified_visualization', simplified_visualization);
    in = in.setVariable('epsilon', epsilon);
    in = in.setVariable('tooth_random_initial_pos_coefficient', tooth_random_initial_pos_coefficient);
    in = in.setVariable('rand_seed_1', rand_seed_1); in = in.setVariable('rand_seed_2', rand_seed_2);
    in = in.setVariable('sine_phase', sine_phase); in = in.setVariable('trajectory_mode', trajectory_mode);
    
    in = fill_simulations_properties(in, {sim_props msm_props tooth_props});
    
    % running simulation
    out = sim(in); %, 'TransferBaseWorkspaceVariables','on');
    time = out.position_data.Time;
    desired_pos = out.position_data.Data(:,1);
    actual_pos = out.position_data.Data(:,2);
    actual_pos_d1 = out.position_data.Data(:,3);
    actual_pos_d2 = out.position_data.Data(:,4);
    action = round(out.position_data.Data(:,5));
    rand_extra_force = out.position_data.Data(:,6);

    data_vec = [time desired_pos actual_pos actual_pos_d1 actual_pos_d2 action (rand_extra_force + external_load)];
    % saving data if NN re-training is needed
    data_save_path = strcat(sim_folder_path, filesep, 'single_tooth_motion_data',...
        filesep, strrep(string(datetime("now")), ':', '-'), '.mat');
    save(data_save_path,'data_vec');

    rmpath(modelFolder); % removing the NN path from the search
    %--- fintess type 1, based on tracking error difference:
%     sqr_integral_error = trapz(time, (actual_pos - desired_pos).^2);
%     fitness = time(end) / sqr_integral_error;
    %--- fitness type 2, reward is for each time step that tracking was
    %than a margine
    
%     abs_tracking_error_vec = abs(desired_pos - actual_pos);
%     time_step = SIMULATION_TIME / length(time); % assume that time steps are equal for simplicity
%     correct_position_idx_vec = find(abs_tracking_error_vec < tracking_margine);
%     if isempty(correct_position_idx_vec)
%         fitness = 0;
%         return
%     end
%     non_regularized_reward = 1 - sigmf(abs_tracking_error_vec(correct_position_idx_vec),...
%                                                               [10/tracking_margine tracking_margine/2]);
%     fitness = sum(non_regularized_reward) * time_step / SIMULATION_TIME;
end

function res = get_rand_initial_position()
% returns a value in range [0.08 0.92]
res = rand;
while res < 0.08 || res > 0.92
    res = rand;
end

end
