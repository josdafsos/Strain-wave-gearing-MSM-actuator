% MSM actuation time sensetivity analysis
clear
for plates_cnt_iter = [6 8]  % options: 4 6 8
    disp(strcat("now computing for ", string(plates_cnt_iter), " tooth plates"))
for tooth_pitch_iter = ["small"] % options: "small" or "big" or "force_optimal"
    disp(strcat("now computing for ", tooth_pitch_iter, " tooth pitch"))

iter = 1;
ITERATIONS_NUMBER = 240;
while iter <= ITERATIONS_NUMBER
    disp(strcat("started simulation: ", string(iter), " / ", string(ITERATIONS_NUMBER)))
    clearvars -except iter plates_cnt_iter max_load_vec tooth_pitch_iter ITERATIONS_NUMBER
    
    % --- simulation control parameters ---
    sim_type = "push_spring";      % options:  "push_spring" "push_push_linear" "push_spring_rotation" "push_push_rotation"
    tb_type = 1;                        % Twin boundary type: options: 1 or 2
    SIMULATION_TIME = 0.04;             % seconds
    simplified_visualization = true;    % poor visualization, but significantly faster computations   
    continue_iteration_on_halt = true; % If a halt state is detected and the parameter is false, then the simulation will be stopped for this particular setup, and the new simulaiton will be started for the next setup
    force_rand_range = [0; 45]; % min and max values, N; [0; 30];
    feedback_threshold_rand_range = [0.25; 1.75]; % min and max values, no dimension
    next_vec_fraction_range = [0; 0];

    saving_folder = "sensetivity_threshold_fraction"; %  "sensetivity_force_threshold" "sensetivity_threshold_fraction"

    if abs(force_rand_range(1) - force_rand_range(2)) < 1e-3;                               is_force_variable = false;
    else                                                                                    is_force_variable = true; end
    if abs(feedback_threshold_rand_range(1) - feedback_threshold_rand_range(2)) < 1e-3;     is_feedback_threshold_variable = false;
    else                                                                                    is_feedback_threshold_variable = true; end
    if abs(next_vec_fraction_range(1) - next_vec_fraction_range(2)) < 1e-3;                 is_next_vec_fraction_variable = false;
    else                                                                                    is_next_vec_fraction_variable = true; end

    % --- simulation execution ---
    parallel_simulations_cnt = 8;  % simulations can be parallelized between CPUs
    tooth_plates_cnt = plates_cnt_iter;
    pitch_type = tooth_pitch_iter;

    MSM_mechanism_simulation_properties

    if motion_type == "linear";  dimension_name = ' N';
    else dimension_name = ' Nm'; end
     
    % simulation run
    upper_index_limit = min(parallel_simulations_cnt, ITERATIONS_NUMBER - iter + 1);
    if iter == ITERATIONS_NUMBER; upper_index_limit = 1; end

    useful_load_list        = NaN(upper_index_limit, 1);
    feedback_threshold_list = NaN(upper_index_limit, 1);
    next_vec_fraction_list  = NaN(upper_index_limit, 1);
    if is_force_variable; force_pd = makedist('Uniform', 'Lower', force_rand_range(1), 'Upper', force_rand_range(2)); end
    if is_feedback_threshold_variable; feedback_pd = makedist('Uniform', 'Lower', feedback_threshold_rand_range(1), 'Upper', feedback_threshold_rand_range(2)); end
    if is_next_vec_fraction_variable; next_vec_fraction_pd = makedist('Uniform', 'Lower', next_vec_fraction_range(1), 'Upper', next_vec_fraction_range(2)); end
    
    model = 'MSM_strain_wave_actuator';
    load_system(model)
    set_param(model,'SimMechanicsOpenEditorOnUpdate','off')
    for i = 1 : upper_index_limit
        if is_force_variable;                   useful_load_list(i) = random(force_pd);
        else                                    useful_load_list(i) = force_rand_range(1); end
        if is_feedback_threshold_variable;      feedback_threshold_list(i) = random(feedback_pd);
        else                                    feedback_threshold_list(i) = feedback_threshold_rand_range(1); end
        if is_next_vec_fraction_variable;       next_vec_fraction_list(i) = random(next_vec_fraction_pd);
        else                                    next_vec_fraction_list(i) = next_vec_fraction_range(1); end

        in(i) = Simulink.SimulationInput(model);
        in(i) = in(i).setVariable('useful_load', -useful_load_list(i));
        in(i) = in(i).setVariable('feedback_threshold', feedback_threshold_list(i));
        in(i) = in(i).setVariable('next_vec_fraction', next_vec_fraction_list(i));
        disp(strcat('Started simulation with external load of ', string(useful_load_list(i)), dimension_name, ...
            ' || feedback threshold: ', string(feedback_threshold_list(i)),' || next vec fraction: ', string(next_vec_fraction_list(i)),...
            ' || ', sim_type, ' || ', string(datetime('now','TimeZone','local','Format','d-MMM HH:mm:ss'))))
    end
    iter = iter + upper_index_limit;

    % if a single computation is left, then multicore is not needed. Also implements a signle core desired computation if "parallel_simulations_cnt" is 1
    if      upper_index_limit > 1 
        sim_results = parsim(in,'TransferBaseWorkspaceVariables','on', 'UseFastRestart', 'on');
    else    
        sim_results = sim(in); 
    end
    
    quit_on_halt = false;
    for i = 1 : upper_index_limit
        if upper_index_limit > 1; out = sim_results(i);
        else out = sim_results; end

        folder_name = strcat("SimResults",filesep, saving_folder, filesep, "tb_type_", string(tb_type), filesep,...
            sim_type, '_', pitch_type, '_pitch_plates_cnt_', string(tooth_plates_cnt));
        if ~isfolder(folder_name);  mkdir(folder_name);    end
        filename = strcat(sim_type, "_load_", replace(string(useful_load_list(i)), ".", "_"), '_N_feedback_threshold_', replace(string(feedback_threshold_list(i)), ".", "_"),...
            '_next_vec_fraction_', replace(string(next_vec_fraction_list(i)), ".", "_"), "_plates_cnt_", string(tooth_plates_cnt),...
            "_sim_time_", replace(string(SIMULATION_TIME), ".", "_"), "_tb_type_", string(tb_type), '.mat');
        full_path = strcat(folder_name, filesep, filename);

        quit_on_halt = save_sim_result(out, full_path, quit_on_halt, useful_load_list(i), feedback_threshold_list(i), next_vec_fraction_list(i));
    end

    % going to the next simulation setup if the system is halted and the corresponding parameter is set
    if quit_on_halt; stop_force_iteration = true; end
end
end
end
disp(strcat('Simulations finished at ', string(datetime('now','TimeZone','local','Format','d-MMM HH:mm:ss'))))
% get dictionary back: dict = getfield(load(filename), "sim_results_dictionary")
