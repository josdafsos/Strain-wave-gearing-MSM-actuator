function quit_on_halt = save_sim_result(out, ...
    full_path, quit_on_halt, useful_load, set_zero_halt_velocity, ...
    feedback_threshold, next_vec_fraction)

        if nargin < 7; next_vec_fraction = 0; end
        if nargin < 6; feedback_threshold = 0; end
        if nargin < 5; set_zero_halt_velocity = true; end  % position and velocity values will be set to zero if Halt state occurs

        % getting simulation parameters from the base workspace
        tb_type = evalin('base','tb_type');
        sim_type = evalin('base','sim_type');
        pitch_type = evalin('base','pitch_type');
        tooth_plates_cnt = evalin('base','tooth_plates_cnt');
        SIMULATION_TIME = evalin('base','SIMULATION_TIME');
        motion_type = evalin('base','motion_type');
        continue_iteration_on_halt = evalin('base','continue_iteration_on_halt');
        tooth_pitch = evalin('base','tooth_pitch');
        disk_diameter = evalin('base','disk_diameter');
        SIM_OVERLOAD = evalin('base','SIM_OVERLOAD');
        SIM_HALT = evalin('base','SIM_HALT');

        % checking if simulationg is halted
        if isprop(out,"sim_stop_result") && isprop(out.sim_stop_result,"Data") && ~isempty(out.sim_stop_result.Data)
            if max(out.sim_stop_result.Data(1) == SIM_OVERLOAD)   % max() is in case Data will be a vector, not scalar
                disp('simulated actuator overloaded')
                % break; % before multicoring it was just breaking
                out.sim_results.Data(:,1) = zeros(length(out.sim_results.Data(:,1)), 1); % position
                out.sim_results.Data(:,2) = zeros(length(out.sim_results.Data(:,2)), 1); % velocity
                if ~continue_iteration_on_halt; quit_on_halt = true; end
            elseif max(out.sim_stop_result.Data(1) == SIM_HALT)  % note: the check for continue_iteration_on_halt condition is at the end of the cycle
                disp('simulated actuator is halted')
                % NOTE previously the following two lines were not commented
                if set_zero_halt_velocity
                    disp('Halt is trigger, setting velocity to zero on halt')
                    out.sim_results.Data(:,1) = zeros(length(out.sim_results.Data(:,1)), 1); % position
                    out.sim_results.Data(:,2) = zeros(length(out.sim_results.Data(:,2)), 1); % velocity
                else
                    disp('Halt is trigger. Velocity is not set to zero due to the settings')
                end
                if ~continue_iteration_on_halt; quit_on_halt = true; end
            end
            % There is also stop on max position reached, however, it is
            % considered as a normal stop, therefore no actions are taken
        end
        % previously tooth plates count was not included into the dictionary
        % keys_parameters = ["time" "sim_type" "tb_type" "pitch_type" "simulation_time"...
        keys_parameters = ["time" "sim_type" "tb_type" "pitch_type" "tooth_plates_cnt" "simulation_time"...
            "rack_position" "rack_velocity" "rack_acceleration" "rack_single_element_frequency"...
            "tooth_position_mm" "msm_resulting_force" "Twinning_dynamic_resistance_force" "Tooth_velocity_mm_per_s" "TB_velocity"...
            "tooth_acceleration" "Twinning_stress_constant_part" "useful_load" "feedback_threshold" "next_vec_fraction"];
        
        time                         = out.sim_results.Time; % seconds
        %sim_type
        %tb_type
        %pitch_type
        %tooth_plates_cnt
        %SIMULATION_TIME
    
        rack_position                = -out.sim_results.Data(:,1); % meters             -OR-  Rad
        rack_velocity                = -out.sim_results.Data(:,2); % meters / sec       -OR-  Rad / sec
        rack_accelearation           = -out.sim_results.Data(:,3); % meters / sec^2     -OR-  Rad / sec^2
        
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
        tooth_position_mm                   = out.msm_parameters_results.Data(:,1);
        msm_resulting_force                 = out.msm_parameters_results.Data(:,2);
        Twinning_dynamic_resistance_force   = out.msm_parameters_results.Data(:,3);
        Tooth_velocity_mm_per_s             = out.msm_parameters_results.Data(:,4);
        TB_velocity                         = out.msm_parameters_results.Data(:,5);
        tooth_acceleration                  = out.msm_parameters_results.Data(:,6);
        Twinning_stress_constant_part       = out.msm_parameters_results.Data(:,7);
    
        dictionary_entries = {time, sim_type, tb_type, pitch_type, tooth_plates_cnt, SIMULATION_TIME, ...
            rack_position, rack_velocity, rack_accelearation, rack_single_element_frequency,...
            tooth_position_mm, msm_resulting_force, Twinning_dynamic_resistance_force, Tooth_velocity_mm_per_s, TB_velocity, tooth_acceleration, Twinning_stress_constant_part,...
            useful_load, feedback_threshold, next_vec_fraction};
    
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