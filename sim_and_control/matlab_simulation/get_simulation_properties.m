function sim_struct = get_simulation_properties()
% simulation properties

% stable settings, but slow: better values go after
% MAX_TIME_STEP = 1e-9; Also looks good MAX_TIME_STEP = 5e-9; % 1e-7 is still stable
% filter_time_constant = 1e-9; % 1e-8 is still stable
% fixed step ode14x

sim_struct.MAX_TIME_STEP = 5e-6; % 3e-7  stable
sim_struct.MIN_STEP_TIME = 0.01*sim_struct.MAX_TIME_STEP; % not verified
sim_struct.filter_time_constant = 5e-7; % working value: 1e-8; % needed for simulink-ps convertors. If smaller unpredicatble behavior may occur
% useful_load = -1; % N or Nm, positive pushes from left to right, negative pushes from right to left. Push along positive X axis
    % or Negative torque pusches clockwise if looking from positive Z into negative Z direction

end