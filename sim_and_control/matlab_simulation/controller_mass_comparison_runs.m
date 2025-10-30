% running the variable mass and load script
model = 'MSM_strain_wave_actuator';
open_system(model);

% --- variable mass ---
% masses = [0.005 0.025 0.050 0.100 0.150];
% useful_load = -2;
% for mass_iter = masses
%     useful_mass = mass_iter;
%     out = sim(model);
% end

% --- variable force ---
% forces = [-1 -2 -4 -8 -12];
% useful_mass = 0.025;
% for force_iter = forces
%     useful_load = force_iter;
%     out = sim(model);
% end

% --- variable velocity ---
velocities = -0.01 : 0.0005 : -0.001;
useful_load = -2;
useful_mass = 0.025;
steady_rms_vector = [];
transition_rms_vector = [];
for velocity_iter = velocities
    controller_velocity_setpoint = velocity_iter;
    out = sim(model);
    [transition_data, steady_data] = compute_rms_from_sim(out, controller_velocity_setpoint);
    steady_rms_vector(end+1) = steady_data.rms_error;
    transition_rms_vector(end+1) = transition_data.rms_error;
end

visual_velocities = abs(velocities(end:-1:1)*1000);
visual_steady_rms_vector = steady_rms_vector(end:-1:1);
visual_transition_rms_vector = transition_rms_vector(end:-1:1);