% script to simulate and save data from the strain MSM actuators
clear
for plates_cnt_iter = [4]  % options: 4 6 8
    disp(strcat("now computing for ", string(plates_cnt_iter), " tooth plates"))
    % for linear motion:
    max_load_4 = 2.05 : 0.05 : 7;
    max_load_6 = 69.0 : 3 : 140;
    max_load_8 = 46 : 2 : 250;
    interrupt_on_halt = false; % If true stops simulations for a particular parametewrs setup
    % for rotary motion:
%     max_load_4 = 0.0 : 0.05 : 2.5;
%     max_load_6 = 0.0 : 0.075 : 3.0;
%     max_load_8 = 0.0 : 0.10 : 3.5;
    max_load_vec = {max_load_4 max_load_6 max_load_8};
for tooth_pitch_iter = ["prototype"] % options: "small" or "big" or "force_optimal" or "prototype"
    disp(strcat("now computing for ", tooth_pitch_iter, " tooth pitch"))
    stop_force_iteration = false; % when halt or overloading is reached, this value is set to true and iteration of the next setup is started
iter = 1;
while iter <= length(max_load_vec{(plates_cnt_iter - 2) / 2})
    if stop_force_iteration; break; end % see the variable declaration explanation
    clearvars -except iter plates_cnt_iter max_load_vec tooth_pitch_iter stop_force_iteration interrupt_on_halt

    % --- simulation control parameters ---
    sim_type = "push_spring";      % options:  "push_spring" "push_push_linear" "push_spring_rotation" "push_push_rotation"
    tb_type = 1;                        % Twin boundary type: options: 1 or 2
    SIMULATION_TIME = 0.04;             % seconds
    simplified_visualization = true;    % poor visualization, but significantly faster computations   
    continue_iteration_on_halt = false; % If a halt state is detected and the parameter is false, then the simulation will be stopped for this particular setup, and the new simulaiton will be started for the next setup

    % --- simulation execution ---
    parallel_simulations_cnt = 8;  % simulations can be parallelized between CPUs
    tooth_plates_cnt = plates_cnt_iter;
    pitch_type = tooth_pitch_iter;

    MSM_mechanism_simulation_properties

    if motion_type == "linear";  dimension_name = ' N';
    else dimension_name = ' Nm'; end
     
    % simulation run
    upper_index_limit = min(parallel_simulations_cnt, length(max_load_vec{(plates_cnt_iter - 2) / 2}) - iter);
    if iter == length(max_load_vec{(plates_cnt_iter - 2) / 2}); upper_index_limit = 1; end

    useful_load_list = max_load_vec{(plates_cnt_iter - 2) / 2}(iter : iter + upper_index_limit - 1);
    model = 'MSM_strain_wave_actuator';
    load_system(model)
    set_param(model,'SimMechanicsOpenEditorOnUpdate','off')
    for i = 1 : upper_index_limit
        in(i) = Simulink.SimulationInput(model);
        in(i) = in(i).setVariable('useful_load', -useful_load_list(i));
        disp(strcat('Started simulation with external load of ', string(useful_load_list(i)), dimension_name, ...
            ' || ', sim_type, ' || ', string(datetime('now','TimeZone','local','Format','d-MMM HH:mm:ss'))))
    end
    iter = iter + upper_index_limit;
    % if a single computation is left, then multicore is not needed. Also implements a signle core desired computation if "parallel_simulations_cnt" is 1
    if      upper_index_limit > 1; sim_results = parsim(in,'TransferBaseWorkspaceVariables','on', 'UseFastRestart', 'on');
    else    sim_results = sim(in); end
    
    quit_on_halt = false;
    for i = 1 : upper_index_limit
        if upper_index_limit > 1; out = sim_results(i);
        else out = sim_results; end

        folder_name = strcat("SimResults",filesep ,"tb_type_", string(tb_type), filesep, sim_type, '_', pitch_type, '_pitch_plates_cnt_', string(tooth_plates_cnt));
        if ~isfolder(folder_name);  mkdir(folder_name);    end
        filename = strcat(sim_type, "_load_", replace(string(useful_load_list(i)), ".", "_"),...
            "_N_plates_cnt_", string(tooth_plates_cnt), "_sim_time_", replace(string(SIMULATION_TIME), ".", "_"), "_tb_type_", string(tb_type), '.mat');
        full_path = strcat(folder_name, filesep, filename);
        quit_on_halt = save_sim_result(out, full_path, quit_on_halt, useful_load_list(i));
        quit_on_halt = quit_on_halt & interrupt_on_halt; % don't automatically quit if user disables it
    end

    % going to the next simulation setup if the system is halted and the corresponding parameter is set
    if quit_on_halt; stop_force_iteration = true; end
end
end
end
disp(strcat('Simulations finished at ', string(datetime('now','TimeZone','local','Format','d-MMM HH:mm:ss'))))
% get dictionary back: dict = getfield(load(filename), "sim_results_dictionary")
