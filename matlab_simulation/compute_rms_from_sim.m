% compute RMS error from the simulation
function [transition_data, steady_data] = compute_rms_from_sim(out, controller_velocity_setpoint)
    steady_time_starts = 0.01; % seconds
    sample_frequency = 8000; % kHz
    setpoint = abs(controller_velocity_setpoint * 1000);
    time_vec = out.sim_results.Time;
    velocity_vec = out.sim_results.Data(:, 3);
    sampled_velocity_vec = [];
    
    start_idx = 0;
    for i = 1 : length(time_vec)
        if time_vec(i) > steady_time_starts
            start_idx = i;
            sampled_velocity_vec(1) = velocity_vec(i);
            break
        end
    end
    
    previous_sample_idx = start_idx;
    for i = start_idx : length(time_vec)
        if time_vec(i) > time_vec(previous_sample_idx) + 1 / sample_frequency
            sampled_velocity_vec(end+1) = velocity_vec(i);
            previous_sample_idx = i;
        end
    end

    setpoint_vec = double(setpoint) * ones(length(sampled_velocity_vec), 1);
    steady_data.rms_error = rmse(sampled_velocity_vec, setpoint_vec');
    steady_data.mean_abs_error = mae(sampled_velocity_vec, setpoint_vec');
    steady_data.max_abs_error = max(abs(sampled_velocity_vec - setpoint_vec'));

    previous_sample_idx = 1;
    sampled_velocity_vec = [];
    for i = 1 : start_idx
        if time_vec(i) > time_vec(previous_sample_idx) + 1 / sample_frequency
            sampled_velocity_vec(end+1) = velocity_vec(i);
            previous_sample_idx = i;
        end
    end
    setpoint_vec = double(setpoint) * ones(length(sampled_velocity_vec), 1);
    transition_data.rms_error = rmse(sampled_velocity_vec, setpoint_vec');
    transition_data.mean_abs_error = mae(sampled_velocity_vec, setpoint_vec');
    transition_data.max_abs_error = max(abs(sampled_velocity_vec - setpoint_vec'));
    
    
end