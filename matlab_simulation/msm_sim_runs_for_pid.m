% script to simulate and save data for PID training
clear
MAX_ITERATIONS = 500;
iter = 1;
while iter < MAX_ITERATIONS
    clearvars -except iter MAX_ITERATIONS

    % --- simulation control parameters ---
    sim_type = "push_spring";      % options:  "push_spring" "push_push_linear" "push_spring_rotation" "push_push_rotation"
    tb_type = 1;                        % Twin boundary type: options: 1 or 2
    SIMULATION_TIME = 0.04;             % seconds

    continue_iteration_on_halt = false; % If a halt state is detected and the parameter is false, then the simulation will be stopped for this particular setup, and the new simulaiton will be started for the next setup
    tooth_plates_cnt = 4;
    pitch_type = "force_optimal";

    simplified_visualization = true;    % poor visualization, but significantly faster computations   
    enable_model_visualization(false); % show visualization (no matter simple or full) on iterations
    enable_fast_restart(true);  % disabling fast restart slows down simulation approximately in two times; set_param(model,"FastRestart","off")
    enable_acceleration(true);

    % --- simulation execution ---
    parallel_simulations_cnt = 8;  % simulations can be parallelized between CPUs
    
    

    MSM_mechanism_simulation_properties

    if motion_type == "linear";  dimension_name = ' N';
    else dimension_name = ' Nm'; end
     
    % simulation run
    upper_index_limit = min(parallel_simulations_cnt, MAX_ITERATIONS - iter);
    if iter == MAX_ITERATIONS; upper_index_limit = 1; end

    model = 'MSM_strain_wave_actuator';
    load_system(model)
    set_param(model,'SimMechanicsOpenEditorOnUpdate','off')
    load_vec = []; vel_vec = []; freq_vec = []; amp_vec = [];
    for i = 1 : upper_index_limit
        load_vec(i) = 15*(rand-0.5)*2;
        profile_type = randi(4);
        [velocity, frequency, amplitude] = get_random_motion_profile(profile_type);
        vel_vec(i) = velocity; freq_vec(i) = frequency; amp_vec(i) = amplitude;
        in(i) = Simulink.SimulationInput(model);
        in(i) = in(i).setVariable('useful_load', load_vec(i));
        in(i) = in(i).setVariable('controller_velocity_setpoint', velocity);
        in(i) = in(i).setVariable('controller_frequency_setpoint', frequency);
        in(i) = in(i).setVariable('controller_amplitude_setpoint', amplitude);
        
        disp(strcat('Started simulation with external load of ', string(load_vec(i)), dimension_name, ...
            ' || vel:', string(velocity), ' || freq:', string(frequency), ' || amplitude:', string(amplitude), ' || ',...
            sim_type, ' || ', string(datetime('now','TimeZone','local','Format','d-MMM HH:mm:ss'))))
    end
    iter = iter + upper_index_limit;
    % if a single computation is left, then multicore is not needed. Also implements a signle core desired computation if "parallel_simulations_cnt" is 1
    if      upper_index_limit > 1; sim_results = parsim(in,'TransferBaseWorkspaceVariables','on', 'UseFastRestart', 'on');
    else    sim_results = sim(in); end
    
    for i = 1 : upper_index_limit
        disp(strcat("data prcoessing ", string(i)))
        if upper_index_limit > 1; out = sim_results(i);
        else out = sim_results; end

        folder_name = strcat("SimResults",filesep ,"pid_data",filesep, pitch_type, '_pitch_plates_cnt_', string(tooth_plates_cnt));
        if ~isfolder(folder_name);  mkdir(folder_name);    end
        filename = strcat("load_", replace(string(load_vec(i)), ".", "_"),...
            "_vel_", replace(string(vel_vec(i)), ".", "_"), "_freq_", replace(string(freq_vec(i)), ".", "_"),...
            "_amp_", replace(string(amp_vec(i)), ".", "_"), '.mat');
        full_path = strcat(folder_name, filesep, filename);
        save_pid_run_results(out, full_path, load_vec(i));
    end

end

disp(strcat('Simulations finished at ', string(datetime('now','TimeZone','local','Format','d-MMM HH:mm:ss'))))
% get dictionary back: dict = getfield(load(filename), "sim_results_dictionary")


function enable_model_visualization(enable_visualization)
% switches ON or OFF visualization of the simulation
% enable_visualization: bool, true = visualizaion is on, false = visualization is off
    if enable_visualization
        state = 'on';
    else
        state = 'off';
    end
    model = 'MSM_strain_wave_actuator';
    load_system(model);
    cur_state = get_param(model,'SimMechanicsOpenEditorOnUpdate');
    if ~strcmp(state, cur_state)
        set_param(model,'SimMechanicsOpenEditorOnUpdate', state);
        save_system(model);
    end
end

function enable_acceleration(enable)
% switches ON or OFF accelerator mode of the simulation
% enable: bool, true = acceleration is on, false = acceleration is off

% Note: Rapid accelerator mode was tested. It does not work as C code cannot be generated
% for some modules

    model = 'MSM_strain_wave_actuator';
    if enable
        state = 'accelerator';
    else
        state = 'normal'; % default mode that was on the model
    end
    load_system(model);
    cur_state = get_param(model,'SimulationMode');
    if ~strcmp(state, cur_state)
        set_param(model,'SimulationMode', state);
        save_system(model);
    end
end

function enable_fast_restart(enable)
% switches ON or OFF fast restart of the simulation
% enable: bool, true = fast restart is on, false = fast restart is off
    if enable
        state = 'on';
    else
        state = 'off';
    end
    model = 'MSM_strain_wave_actuator';
    load_system(model);
    cur_state = get_param(model,'FastRestart');
    if ~strcmp(state, cur_state)
        set_param(model,'FastRestart', state);
        save_system(model);
    end

    cur_state = get_param(model,'FastRestart');
    if strcmp(cur_state, 'off')
        disp("NOTE: fast restart is switched off!!!")
    end

end

function save_pid_run_results(out, full_path, useful_load)

        % getting simulation parameters from the base workspace
        tb_type = evalin('base','tb_type');
        sim_type = evalin('base','sim_type');
        pitch_type = evalin('base','pitch_type');
        tooth_plates_cnt = evalin('base','tooth_plates_cnt');
        SIMULATION_TIME = evalin('base','SIMULATION_TIME');
        motion_type = evalin('base','motion_type');
        tooth_pitch = evalin('base','tooth_pitch');
        disk_diameter = evalin('base','disk_diameter');
        SIM_OVERLOAD = evalin('base','SIM_OVERLOAD');
        SIM_HALT = evalin('base','SIM_HALT');
        feedback_threshold = evalin('base','feedback_threshold');
        next_vec_fraction = evalin('base','next_vec_fraction');

        % checking if simulationg is halted
        if isprop(out,"sim_stop_result") && isprop(out.sim_stop_result,"Data") && ~isempty(out.sim_stop_result.Data)
            if max(out.sim_stop_result.Data(1) == SIM_OVERLOAD)   % max() is in case Data will be a vector, not scalar
                disp('simulated actuator overloaded')
                % break; % before multicoring it was just breaking
                out.sim_results.Data(:,1) = zeros(length(out.sim_results.Data(:,1)), 1); % position
                out.sim_results.Data(:,2) = zeros(length(out.sim_results.Data(:,2)), 1); % velocity
            elseif max(out.sim_stop_result.Data(1) == SIM_HALT)  % note: the check for continue_iteration_on_halt condition is at the end of the cycle
                disp('simulated actuator is halted')
                out.sim_results.Data(:,1) = zeros(length(out.sim_results.Data(:,1)), 1); % position
                out.sim_results.Data(:,2) = zeros(length(out.sim_results.Data(:,2)), 1); % velocity
            end
            % There is also stop on max position reached, however, it is
            % considered as a normal stop, therefore no actions are taken
        end


        
        time                         = out.sim_results.Time; % seconds
        %sim_type
        %tb_type
        %pitch_type
        %tooth_plates_cnt
        %SIMULATION_TIME
    
        rack_position                = -out.sim_results.Data(:,1); % meters             -OR-  Rad
        rack_velocity                = -out.sim_results.Data(:,2); % meters / sec       -OR-  Rad / sec
        rack_accelearation           = -out.controller_state.Data(:,6); % Tach of 1e-3 rack acceleration
        
        if tb_type == 1
            initial_cutoff_time = 0.004; % seconds. Strating from this time values are taken into account. Needed to eliminate initial transient processes
        elseif tb_type == 2
            initial_cutoff_time = 0.0005;
        else
            initial_cutoff_time = NaN;
        end
        initial_cutoff_index = length(find(time<initial_cutoff_time));
        if motion_type == "linear"
            rack_single_element_frequency =  abs(rack_position(end) - rack_position(initial_cutoff_index))...
                / (time(end) - time(initial_cutoff_index)) / tooth_pitch; % out.sim_results.Data(:,4); % Hz
        elseif motion_type == "rotary"
            rack_single_element_frequency = abs(rack_position(end) - rack_position(initial_cutoff_index))...
                / (time(end) - time(initial_cutoff_index)) / (2 * tooth_pitch / disk_diameter);
        end
        forward_pid             = out.controller_state.Data(:,1);
        reverse_pid             = out.controller_state.Data(:,2);
        new_pid                 = out.controller_state.Data(:,3);
        initial_pid             = out.controller_state.Data(:,4);
        controller_switch_spike = out.controller_state.Data(:,5);
        desired_velocity        = out.controller_state.Data(:,7);

        keys_parameters = ["time" "sim_type" "tb_type" "pitch_type" "tooth_plates_cnt" "simulation_time"...
            "rack_position" "rack_velocity" "tahn_rack_acceleration" "rack_single_element_frequency"...
            "useful_load" "feedback_threshold" "next_vec_fraction" "forward_pid" "reverse_pid"...
            "new_pid" "initial_pid" "controller_switch_spike" "desired_velocity"];
        dictionary_entries = {time, sim_type, tb_type, pitch_type, tooth_plates_cnt, SIMULATION_TIME, ...
            rack_position, rack_velocity, rack_accelearation, rack_single_element_frequency,...
            useful_load, feedback_threshold, next_vec_fraction, forward_pid, reverse_pid, new_pid,...
            initial_pid, controller_switch_spike, desired_velocity};
    
        if sim_type == "push_spring" || sim_type == "push_spring_rotation"
            keys_parameters = [keys_parameters "spring_y_offset" "spting_natural_length" "spring_stiffness"];
            spring_y_offset         = evalin('base','spring_y_offset');
            spting_natural_length   = evalin('base','spting_natural_length');
            spring_stiffness        = evalin('base','spring_stiffness');
            dictionary_entries{end + 1} = spring_y_offset;
            dictionary_entries{end + 1} = spting_natural_length;
            dictionary_entries{end + 1} = spring_stiffness;
        else
            keys_parameters = [keys_parameters "swing_spring_upper_offset" "swing_spring_crank_length" "swing_spring_stiffness"];
            swing_spring_upper_offset   = evalin('base','swing_spring_upper_offset');
            swing_spring_crank_length   = evalin('base','swing_spring_crank_length');
            swing_spring_stiffness      = evalin('base','swing_spring_stiffness');
            dictionary_entries{end + 1} = swing_spring_upper_offset;
            dictionary_entries{end + 1} = swing_spring_crank_length;
            dictionary_entries{end + 1} = swing_spring_stiffness;
        end
        
        sim_results_dictionary = dictionary(keys_parameters, dictionary_entries);
        save(full_path, 'sim_results_dictionary')
        
end