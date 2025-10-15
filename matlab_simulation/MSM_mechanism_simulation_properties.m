% MSM mechanism simulation properties

% simulation properties
% stable settings, but slow:
% MAX_TIME_STEP = 1e-9; Also looks good MAX_TIME_STEP = 5e-9; % 1e-7 is still stable
% filter_time_constant = 1e-9; % 1e-8 is still stable
% fixed step ode14x
% variable step solver that simulation were made with: ode23t (mod.
% stiff/Trapeziodal)

% TODO for push-push linear and push-push rotation "force optimal" can
% happen the same thing as for push-spring force optimal, check the
% correctness of the initial position - checked - this is not the case, the
% initial position is correct.
% for some reason the MSM elements are not switching in the needed time (is
% the spring too stiff or a feedback problem?)
% The push-push force-optimal seems to work, mb not with the best
% performance, make the simulations and check the plots. Also for the 8
% plates setup the initial extension/contraction of MSM elements might not
% be correct, the elements are "jumping" up and down on the initialization

MAX_TIME_STEP = 5e-6; % 3e-7  stable
MIN_STEP_TIME = 0.01*MAX_TIME_STEP; % not verified
filter_time_constant = 5e-7; % working value: 1e-8; % needed for simulink-ps convertors. If smaller unpredicatble behavior may occur
solver_relative_tolerance = 1e-4; % default was 1e-3;

% ---- Control parametrs ----

% Useful load applied to the rack

if ~exist('useful_load','var')
    useful_load = -2; % N or Nm, positive pushes from left to right, negative pushes from right to left. Push along positive X axis
    % or Negative torque pusches clockwise if looking from positive Z into negative Z direction
end
if ~exist('useful_mass','var')
    useful_mass = 0.0001; % kg, extra mass which adds to the rack to imitate the inertial load
end
if ~exist('tb_type','var')
    tb_type = 1; % either 1 or 2, error will show on any other value
end
if ~exist('sim_type','var') 
    sim_type = "push_spring"; % "push_spring" "push_push_linear" "push_spring_rotation" "push_push_rotation"
end
if ~exist('tooth_plates_cnt','var')
    tooth_plates_cnt = 4; % number of tooth plates: 4, 6, 8
end
if ~exist('pitch_type','var') 
    % "small" "big" "force_optimal" or "prototype"
    % Note: "prototype" also redefines springs, masses and size of the MSM elements
    pitch_type = "force_optimal";
end
if ~exist('tooth_quality','var') % "low" "high" defines accuracy of the mesh
    tooth_quality = "low";
end
if ~exist('SIMULATION_TIME','var')
    SIMULATION_TIME = 0.08; % seconds  % usually 0.04
end
if ~exist('disck_diameter','var')
    disk_diameter = 35e-3; % m, central diameter of the teeth disk. For rotatary actuators only
    % WILL BE ROUNDED  to match tooth_pitch and integer numbers of teeth
end
if ~exist('simplified_visualization','var') % Note: if the value is <true> the simulation will look broken, but it is actually fine
    simplified_visualization = true; % used to speed up the computations significantly if set to true in expense of visualization
end

% other adjustable properties that are not intended for manual adjustment
if ~exist('max_teeth_passed','var'); max_teeth_passed = 5; end  % simulation will stop after this number of teeth will be passed
if ~exist('feedback_threshhold_offset','var'); feedback_threshhold_offset = 0.0; end  % [-1; 1] range, defines the actuation offset of the MSM element actuation
if ~exist('next_vec_fraction','var'); next_vec_fraction = 0.0; end  % [-CR; +CR] range, defines the disengagement timing for the last tooth, positive value leads to earlier disengagement

% --- controller properties ---
% NOTE: FOR OPEN LOOP CONTROL, PID AND BREAKING MUST BE DIASABLED MANUALLY
% IN THE MODEL (CONTROLLER BLOCK)
if ~exist('controller_type_vec','var') % Vector to select which teeth are controlled by NN agent and which are controlled by analytic algorithm
    % Vecltor length = tooth_plates_cnt; zero value in the vector means that the controller for the corresponding tooth is analytical
    % value of one or greater means that a corresponding tooth is controlled by NN agent
    controller_type_vec = zeros(tooth_plates_cnt, 1); % by default fully analytical controller is used; mixed controller are possible
end
if length(controller_type_vec) ~= tooth_plates_cnt
    error('controller_type_vec length and tooth_plates_cnt values do not match')
end
if ~exist('next_vec_fraction','var'); next_vec_fraction = 0.0; end  % [-CR; +CR] range, defines the disengagement timing for the last tooth, positive value leads to earlier disengagement
if ~exist('random_delay_probablity','var'); random_delay_probablity = 0.0; end % [0, 1] - probability of analitical controller to randomly keep the previous control value
if ~exist('random_switch_probability','var'); random_switch_probability = 0.0; end % [0, 1] - probability of analitical controller to randomly switch output to the opposite value, i.e. 0 -> 1, 1 -> 0
if ~exist('controller_loop_type','var'); controller_loop_type = 1; end  % defines the type of analytical controller. 0 - open loop; 1 - closed loop
if ~exist('controller_velocity_setpoint','var'); controller_velocity_setpoint = -0.010; end % desired velocity for open loop controller, m/s. Not implemented for closed loop
    % closed loop setpoints:
if ~exist('controller_frequency_setpoint','var'); controller_frequency_setpoint = 1e-3; end % rad/s; no faster than 350 rad/sec
if ~exist('controller_amplitude_setpoint','var'); controller_amplitude_setpoint = 0; end % m/s
if ~exist('controller_desired_profile_type','var'); controller_desired_profile_type = 1; end % [1,2,...,5], 1 - constant desired velocity, others - various periodic signals

% NN controller
if ~exist('enable_neighbours_obs','var'); enable_neighbours_obs = 0; end % if > 0.5 in case of single element control adds neighbours position and velocity observations
if ~exist('enable_vel_setpoint','var'); enable_vel_setpoint = 0; end % if > 0.5 in case of single element control adds controller_velocity_setpoint value to the observations
if ( controller_loop_type < 0.5 || enable_vel_setpoint > 0.5) && abs(controller_velocity_setpoint) < 1e-4
    warning('controller_velocity_setpoint is set to zero. Controller will try to hold its position')
end
obs_matrix_size = 6; % size of the observat
if enable_neighbours_obs > 0.5; obs_matrix_size = obs_matrix_size + 4; end  % add vel and pos data
if enable_vel_setpoint > 0.5; obs_matrix_size = obs_matrix_size + 1; end
obs_matrix = zeros(tooth_plates_cnt, obs_matrix_size); %  obs_matrix_size);
%% simulation run properties
if ~exist('simulation_pause_time','var'); simulation_pause_time = 2*SIMULATION_TIME; end % seconds; Pauses simulation after simulation time reaches this value. Used for externally controlled simulation
if ~exist('has_external_controller','var'); has_external_controller = 0; end % 0 or 1. If > 0, then the control signal is taken from 'external_control_value' variable
if ~exist('external_control_value','var'); external_control_value = 0; end % [0 1] - pid value for external controller. Should be updated externally during the simulation


%% ---- Model properties ----

if sim_type == "push_spring" || sim_type == "push_push_linear"
    motion_type = "linear";
    motion_type_number = 0;
elseif sim_type == "push_push_rotation" || sim_type == "push_spring_rotation" 
    motion_type = "rotary";
    motion_type_number = 1;
else
    motion_type = NaN;
    motion_type_number = NaN;
end

% --- Masses ---
tooth_plate_mass = 0.22e-3; % kg
rack_mass = 1.5e-3; % kg, pure mass of the rack
swing_mass = 1e-3; % kg TODO set a proper mass, not a guess
tooth_disk_mass = 5e-3; % kg TODO set a proper mass, not a guess
if pitch_type == "prototype"
    tooth_plate_mass = 1.09e-3; % kg
    rack_mass = 4e-3; % kg, pure mass of the rack
end

% --- MSM crystal paratemers ---
% The msm full length is considered to be at fully extended position.
if pitch_type == "prototype"
    msm_length = 10e-3; % meters
    msm_width = 2.5e-3;   % meters
    msm_height = 1e-3;  % meters
else
    if ~exist('msm_length','var'); msm_length = 10e-3; end % meters
    if ~exist('msm_width','var');  msm_width = 4e-3;   end % meters
    if ~exist('msm_height','var'); msm_height = 1e-3;  end % meters
end
A0 = msm_width * msm_height; % MSM crystal cross section area

e_0 = 0.06; % max elongation, from Saren and Ullakko, approximate value
allowed_elongation = 0.05; % full extension is not allowed to keep the TB and increase cyclic life
one_side_elongation_capacity = ( e_0 - allowed_elongation ) / 2; % Used as an offset and shows the amount of possible additional elongation/contraction
one_side_absolute_offset = one_side_elongation_capacity * msm_length;
e_initial = 0.05; % initial contraction
contraction_initial = -msm_length * e_initial; % meters, value wrt to the full elongation, same as initial position of the Twin Boundary

ro = 8000; % kg/m^3, alloy density
msm_mass = ro * A0 * msm_length; % total mass of msm element

% Note following line and other code related to inital TB position and TB
% mass are implemented in MSM element Simscape model directly
% tb_initial_position = (abs(contraction_initial) + one_side_absolute_offset) / e_0; % meters TODO IS THAT CORRECT???
% msm_tb_mass_initial = msm_mass * (e_initial + one_side_elongation_capacity ) / e_0; % Let's for now consider the initial retoriented mass proportional to current strain. TODO is it correct?

constant_magnetic_stress = 3.27e+6; % Pa, from Saren and Ullakko 2017, ref [24] there
k_0 = 11.8; % from Saren and Ullakko 2017
cos_a = cos(deg2rad(43.23));

% cad y_offset = -0.3
% cad z_offset = -0.04
max_tooth_motion_range = -2e-6; % meters, basically 0, but needs to avoid the zero crossing
min_tooth_motion_range = -msm_length * allowed_elongation;

% --- Tooth properties ---

tooth_alpha = deg2rad(20); % rad, inclinations of the tooth profile

if pitch_type == "big"
    tooth_pitch = 0.6*1e-3; % meters
    tooth_height = 0.46*1e-3; % meters, max elongation is 0.5*1e-3, so there is some safety margin
    t_a = 0.15*1e-3 * 0.3; % meters, the second multiplier is to improve feedback control performance as the tooth plates will engage a bit earlier. This approach exploits roundings presents on the teeth
    t_b = 0.15*1e-3; % meters
    if sim_type == "push_spring" || sim_type == "push_spring_rotation"
        feedback_threshold = 0.80;
    else
        feedback_threshold = 0.85;
    end
    %half_y_grid_vec = [0 0.03 0.07 0.2  0.2191 0.2489 0.285] * 1e-3;
    %half_z_grid_vec = [0 0    0.03 0.39 0.421  0.4419 0.45] * 1e-3;
    half_y_grid_vec = [0.03 0.07 0.2  0.2191 0.2489 0.285] * 1e-3;
    half_z_grid_vec = [0    0.03 0.39 0.421  0.4419 0.45] * 1e-3;
elseif pitch_type == "small"
    tooth_pitch  = 0.52442*1e-3; % meters
    tooth_height = 0.475*1e-3; % intially height was this value, but it seems to be incorrect: 0.46*1e-3; % meters, max elongation is 0.5*1e-3, so there is some safety margin
    t_a = 0.07*1e-3 * 0.50; % meters, the second multiplier is to improve feedback control performance as the tooth plates will engage a bit earlier. This approach exploits roundings presents on the teeth
    t_b = 0.1867*1e-3; % meters
    feedback_threshold = 0.97; % the performance analysys simulations ran with this value (0.97) 
    % accurate radiuses on the bottom
    %     half_y_grid_vec = [0 0.02868 0.04698 0.05431 0.20790 0.22296 0.24229 0.26154] * 1e-3;
    %     half_z_grid_vec = ([0 0.00904 0.03290 0.05303 0.47500 0.49766 0.50949 0.51303] - 0.05303) * 1e-3;
    % simplified tooth profile
    if strcmp(tooth_quality, "low")
        half_y_grid_vec =  [0.03501 0.20790 0.22296 0.24229 0.26154] * 1e-3;
        half_z_grid_vec = ([0       0.47500 0.49766 0.50949 0.51303] - 0.05303) * 1e-3; % is there an error in substraction???
    elseif strcmp(tooth_quality, "high")
        half_y_grid_vec =  [0.03501 0.20790 0.22296 0.24229 0.26154] * 1e-3;
        half_z_grid_vec = ([0       0.47500 0.49766 0.50949 0.51303] - 0.051303) * 1e-3;
    else
        error("unknown tooth_quality parameter")
    end
elseif pitch_type == "force_optimal"
    feedback_threshold = 0.98; % the performance analysys simulations ran with this value (0.98)
    tooth_height = 0.49*1e-3; % m, the max tooth height is 0.5 mm, but let's keep some margin
    t_b = tooth_height * tan(tooth_alpha); % m
    t_a = 3e-6; % m, keep it non-zero for computational purpusoses
    tooth_pitch = 2 * (t_a + t_b);
    if tooth_quality == "low"
        half_y_grid_vec = [ 0.01*t_a          t_a/2  t_b + t_a/2          t_b + t_a/3 + t_a/2 ];
        half_z_grid_vec = [-0.01*tooth_height 0      tooth_height         tooth_height        ]; % the last term is needed because a tooth plate may jam with points around a tooth
    elseif tooth_quality == "high"
        error("tooth_quality HIGH parameter is not available")
    else
        error("unknown tooth_quality parameter")
    end
    %half_y_grid_vec = [t_a/2  t_b + t_a/2 ];
    %half_z_grid_vec = [0      tooth_height];
elseif pitch_type == "prototype"  % TODO: GIVE INSERT REAL VALUES!!!! RIGHT NOW THE VALUES ARE GIVEN AS FOR FORCE_OPTIMAL
    feedback_threshold = 0.98; % the performance analysys simulations ran with this value (0.98)
    next_vec_fraction = -0.05;
    tooth_height = 0.41*1e-3; % m, the max tooth height is 0.5 mm, but let's keep some margin
    % t_b = toothr_height * tan(tooth_alpha); % m
    t_a = 0.15*1e-3; % m, keep it non-zero for computational purpusoses
    t_b = t_a;
    tooth_pitch = 2 * (t_a + t_b);
    if tooth_quality == "low"
        half_y_grid_vec = [ 0.01  0.0758  0.2034  0.2276  0.2517  0.2759  ] * 1e-3; % last point 0.3000
        half_z_grid_vec = [-0.04  0       0.351   0.3867  0.4024  0.4092  ] * 1e-3; % last point 0.4100
    elseif tooth_quality == "high"
        error("tooth_quality HIGH parameter is not available")
    else
        error("unknown tooth_quality parameter")
    end
    %half_y_grid_vec = [t_a/2  t_b + t_a/2 ];
    %half_z_grid_vec = [0      tooth_height];
end

tooth_number_multiplier = 1; % multiplies the number of teeth in the rack surface. Needs for teeth count scaling when pitch is scaled
if sim_type == "push_push_linear" || sim_type == "push_push_rotation" % to keep the same MSM element the pitch needs to be scaled down
    if pitch_type == "small"
        tooth_size_modifier = 0.60; % 0.55;  % max 0.67, but the spring is not helping at the middle position
        feedback_threshold = 0.90;
        t_a = t_a * 0;
    elseif pitch_type == "force_optimal"
        t_a = 0;
        tooth_size_modifier = 0.65; % tested with 0.60 perfomance is worse compared to "small pitch"
        feedback_threshold = 1.025; % feedback from 0.90+ to 0.70- gives the same result
    else
        tooth_size_modifier = NaN;
    end
    tooth_pitch =       tooth_pitch * tooth_size_modifier;
    tooth_height =      tooth_height * tooth_size_modifier;
    half_y_grid_vec =   half_y_grid_vec * tooth_size_modifier;
    half_z_grid_vec =   half_z_grid_vec * tooth_size_modifier;
    tooth_number_multiplier = 2;
    t_a = t_a * tooth_size_modifier;
    t_b = t_b * tooth_size_modifier;
end

contact_ratio = tooth_plates_cnt / (2 * (t_a / t_b + 1));

% --- Returning spring properties ---
if tb_type == 2
    spring_y_offset = 5e-3; % meters, 0.5e-3
    spting_natural_length = 20e-3 + spring_y_offset; % m 5e-3 + spring_y_offset
    spring_stiffness = 0.5e+2; % N/m 1e+2
elseif tb_type == 1
    spring_y_offset = 5e-3; % meters, 0.5e-3
    spting_natural_length = 20e-3 + spring_y_offset; % m 5e-3 + spring_y_offset
    spring_stiffness = 3.40e+2; % N/m old did not return fully: 1.70e+2
    if pitch_type == "prototype"  % TODO insert the real values
        spring_y_offset = 2e-3; % meters, 
        spting_natural_length = 6.35e-3 + spring_y_offset; % m
        spring_stiffness = 650; % N/m spring E00630090250M
    end
end

if sim_type == "push_push_linear" || sim_type == "push_push_rotation"
    spring_stiffness = 1e-15; % basically equal to zero as this spring is not used for the mechanisms
    swing_spring_upper_offset = 3e-3; % m
    swing_spring_crank_length = 3e-3; % m
    swing_spring_natural_length = (swing_spring_crank_length + swing_spring_upper_offset) / 2; % m
    swing_spring_compressed_length = (swing_spring_crank_length + swing_spring_upper_offset...  % 35 is a bit too low, 45 is a bit too much
            - swing_spring_natural_length);
    if tb_type == 1
        swing_spring_stiffness = 45 / swing_spring_compressed_length; % N / m, desired force devided by elongation; 35 is a bit too low, 45 is a bit too much
        if pitch_type == "force_optimal"
            swing_spring_stiffness = 25 / swing_spring_compressed_length; % N / m, desired force devided by elongation; the contracted element might not have enough force to overcome the spring, so the spring stiffnes might be reduced
        end
    elseif tb_type == 2  % for now, keep the same spring properties
        swing_spring_stiffness = 45 / swing_spring_compressed_length; % N / m, desired force devided by elongation; 35 is a bit too low, 45 is a bit too much
        if pitch_type == "force_optimal"
            swing_spring_stiffness = 25 / swing_spring_compressed_length; % N / m, desired force devided by elongation; the contracted element might not have enough force to overcome the spring, so the spring stiffnes might be reduced
        end
    end
end

plate_teeth_cnt = 1;
% correcting the disk diameter to match the integer number of teeth
disk_teeth_count = ceil(pi * disk_diameter / tooth_pitch);
disk_diameter = disk_teeth_count * tooth_pitch / pi;

% -- Friction and damping -- 
% Consider bronze-stainless steel friction pair. Tooth
% plates are from Bronze, other elements from stainless steel (or another
% hard material that is not ferromagnetic
if ~exist('zero_friction','var'); zero_friction = false; end  % [-CR; +CR] range, defines the disengagement timing for the last tooth, positive value leads to earlier disengagement

if zero_friction
    rack_coulumb_friction = 1e-10; % N, based on approximation with plastic and bronze parts for prototype
    rotational_rack_coulumb_friction = 1e-10;  % Nm
    % TODO add proper values for contact forces, right now there is some
    % default non-zero friction values
    % contact friction:
    rack_contact_coeff_static_friction = 1e-10; % source https://mechguru.com/machine-design/typical-coefficient-of-friction-values-for-common-materials/
    bronze_steel_kinetic_friction = 1e-10; % source https://mechguru.com/machine-design/typical-coefficient-of-friction-values-for-common-materials/
    steel_steel_contact_coeff_kinetic_friction = 1e-10; % same source
    rotational_contact_coeff_kinetic_friction = 1e-10;
else
    rack_coulumb_friction = 0.01; % N, based on approximation with plastic and bronze parts for prototype
    rotational_rack_coulumb_friction = rack_coulumb_friction * disk_diameter;  % Nm
    % TODO add proper values for contact forces, right now there is some
    % default non-zero friction values
    % contact friction:
    rack_contact_coeff_static_friction = 0.16; % source https://mechguru.com/machine-design/typical-coefficient-of-friction-values-for-common-materials/
    bronze_steel_kinetic_friction = 0.16; % source https://mechguru.com/machine-design/typical-coefficient-of-friction-values-for-common-materials/
    steel_steel_contact_coeff_kinetic_friction = 0.23; % same source
    rotational_contact_coeff_kinetic_friction = bronze_steel_kinetic_friction * disk_diameter / (2*pi);
end
% Twinning stress friction
if tb_type == 1
    coulomb_friction_ts = (0.6 * A0)*(1e+6);  % MPa
elseif tb_type == 2
    coulomb_friction_ts = (0.1 * A0)*(1e+6);  % MPa
else
    coulomb_friction_ts = NaN;
    error('Unknown Twin boundary type, only values of 1 or 2 are possible')
end
if zero_friction
    coulomb_friction_ts = 1e-10;
end

% --- visualization ---
solid_block_opacity = 0.3;
moving_tb_color = [0.0 0.0 0.0];
rotary_gear_contact_sphere_radius = 1e-5; % m
linear_msm_elements_contact_sphere_radius = 8e-6; % m

% Tooth plate dimensions
tooth_plate_height = 4.64e-3; % meters, from tooth bottom to the other edge of the plate

if abs(min_tooth_motion_range) < tooth_height; disp('MSM motion range is smaller than tooth height! Motion is NOT possible'); end

angle_single_tooth_step         = 2*pi * tooth_pitch / tooth_plates_cnt / (pi*disk_diameter);
if simplified_visualization
    rack_teeth_cnt = 20 * tooth_number_multiplier;
    if tb_type == 2; rack_teeth_cnt = 80 * tooth_number_multiplier; end
    tooth_plates_pitch              = tooth_pitch * 1 + tooth_pitch / tooth_plates_cnt; % for push_spring case
    in_pair_tooth_plates_pitch      = 16 * tooth_pitch + tooth_pitch / 2; % distance between plates inside a swing block
    swing_block_tooth_plates_pitch  = 1 * tooth_pitch + tooth_pitch / tooth_plates_cnt; % distance between swing blocks

    angle_tooth_plates_pitch        = 2*pi * (-2*tooth_pitch + tooth_plates_pitch) / (pi*disk_diameter);
    in_pair_angle_tooth_plates_pitch        = 2*pi * (5*tooth_pitch + tooth_pitch / 2) / (pi*disk_diameter);
    swing_block_angle_tooth_plates_pitch    = 2*pi * (1*tooth_pitch + tooth_pitch / tooth_plates_cnt) / (pi*disk_diameter);
else
    rack_teeth_cnt = 200 * tooth_number_multiplier;
    tooth_plates_pitch              = tooth_pitch * 12 + tooth_pitch / tooth_plates_cnt; % for push_spring case
    in_pair_tooth_plates_pitch      = 2 * tooth_pitch * 10 + tooth_pitch / 2; % distance between plates inside a swing block
    swing_block_tooth_plates_pitch  = 2 * tooth_pitch * 22 + tooth_pitch / tooth_plates_cnt; % distance between swing blocks

    angle_tooth_plates_pitch        = 2*pi * (-23*tooth_pitch + tooth_plates_pitch) / (pi*disk_diameter);
    in_pair_angle_tooth_plates_pitch        = 2*pi * (-2*tooth_pitch + in_pair_tooth_plates_pitch) / (pi*disk_diameter);
    swing_block_angle_tooth_plates_pitch    = 2*pi * (-7*tooth_pitch + swing_block_tooth_plates_pitch) / (pi*disk_diameter);
end
swing_end_offset = -tooth_plate_height/3; % seems to work: -tooth_plate_height/2;
swing_coord_vec = [in_pair_tooth_plates_pitch/2 
                   swing_end_offset + min_tooth_motion_range * feedback_threshold / 2
                   msm_height];
swing_length = in_pair_tooth_plates_pitch * 0.5;
if motion_type == "rotary"
    swing_coord_vec(1) = 0;
end

% --- Contact properties ---

contact_transition_region_width = 1e-4; % meters; % 1e-4 - precise but quite slow; 1e-3 - fast but not precise;  
% depth to start computing the penetration force, 
% can affect quality and speed of contact computations; defaul 1e-4, all tests were made with this value.
% value of 1e-3 is close to the limit, it entroduces a slight error, but
% increases computation by over 20%

contact_damping = 1e+4; % N/(m/s); 1e+3; default value (all simulation results were obtrained with it)

% --- Other ---
if ~exist('initial_spike_force','var'); initial_spike_force = 0; end % force that is initially applied to the rack and then decays raåpidly (for extra randomness in intial rack velocity)
force_control_coeff = 1.0; % to reduce MFIS value

if motion_type == "linear"
    if simplified_visualization
        rack_initial_position = 10 * tooth_pitch;  % the value must be in phase with tooth plates, meters
        if tb_type == 2; rack_initial_position = 60 * tooth_pitch; end
    else
        rack_initial_position = 85 * tooth_pitch;  % the value must be in phase with tooth plates, meters
    end
    MAX_OVERLOAD_VELOCITY = 2.5; % m/s; If the rack reaches the value the mechanism is considered overloaded and simulation stops
    HALT_VELOCITY = 2e-4; % Value used for performance curves: 1e-3; % m/s; if the average rack velocity is lower than this value, the actuator is considered halted
    MAX_POSITION = max_teeth_passed * tooth_pitch; % m, before was 7; push-spring 8 plates - 10 teeth to end, push-push - 8 plates (taking one less than max)
elseif motion_type == "rotary"
    rack_initial_position = tooth_plates_cnt / 2 * angle_single_tooth_step; % Rad
    % there is a mess with feedback based on purely initial position, TODO should be reworked
    % This mess might be caused by the rounding of the teeth on the gear, but for now:
    if pitch_type == "force_optimal"  % for now the constant multiplier is basically tooth_plate_cnt/2, but depending on the pitch value, it could be different
        if tooth_plates_cnt == 4
            rack_initial_position = rack_initial_position + 2*angle_single_tooth_step; % TODO does it work with non-visually simplified?
        elseif tooth_plates_cnt == 6
            rack_initial_position = rack_initial_position + 3*angle_single_tooth_step;  
        elseif tooth_plates_cnt == 8
            rack_initial_position = rack_initial_position + 4*angle_single_tooth_step;
        end
    end
    MAX_OVERLOAD_VELOCITY = 100; % rad/s; If the rack reaches the value the mechanism is considered overloaded and simulation stops
    HALT_VELOCITY = 0.2; % rad/s; if the average rack velocity is lower than this value, the actuator is considered halted
    MAX_POSITION = rack_initial_position + max_teeth_passed * tooth_plates_cnt * angle_single_tooth_step; % Rad
end
if ~exist('rack_initial_velocity','var')
    rack_initial_velocity = 0.0; % intial velocity of the rack of the main gear, m/s or rad/s; positive value is towards world X axis positive direction
    % when simulations are iterated, this value update requres fast restart
    % to be switched off: set_param(model,"FastRestart","off")
end

% simulation stopping codes (for halt or overload detection
SIM_OK = 0;
SIM_HALT = 1; % the MSM elements cannot push the rack, 0 velocity is reached
SIM_OVERLOAD = 2; % the loading force is too strong to backdrive the actuator
SIM_MAX_POS_REACHED = 3; % simulation is stopped when max position is reached, considered as a normal state
% previous lines are for compatibility
sim_state_code.SIM_OK = 0;
sim_state_code.SIM_HALT = 1; % the MSM elements cannot push the rack, 0 velocity is reached
sim_state_code.SIM_OVERLOAD = 2; % the loading force is too strong to backdrive the actuator
sim_state_code.SIM_MAX_POS_REACHED = 3; % simulation is stopped when max position is reached, considered as a normal state
sim_state_code.SIM_MAX_TIME_REACHED = 4; % simulation is stoped if time overeaches SIMULATION_TIME (needed for RL control, otherwise will be stopped by simulation itself)


VALIDATION_START_TIME = 0.05*SIMULATION_TIME; % Time from which the check for stop is strarted (needs to eliminate the transient processes)
if sim_type == "push_push_linear" || sim_type == "push_push_rotation"
    VALIDATION_START_TIME = 0.15*SIMULATION_TIME;
    if pitch_type == "force_optimal"
        VALIDATION_START_TIME = 0.25*SIMULATION_TIME;
    end
end

% CAD file paths: 
% flat_tooth_plate_cad_path = 'Tooth plate single piece.STEP';
% rack_cad_path = 'Rack.STEP';

% crystal_visualization_length =msm_length+msm_width; % in case the TB is tilted
crystal_visualization_length = msm_length; % in case the TB is flat

linear_mechanism = Simulink.Variant('motion_type == "linear"'); 
rotary_mechanism = Simulink.Variant('motion_type == "rotary"'); 

four_tooth_plates = Simulink.Variant('tooth_plates_cnt == 4');
six_tooth_plates = Simulink.Variant('tooth_plates_cnt == 6');
eight_tooth_plates = Simulink.Variant('tooth_plates_cnt == 8');

push_spring_mechanism = Simulink.Variant('sim_type == "push_spring"'); 
push_push_linear_mechanism = Simulink.Variant('sim_type == "push_push_linear"'); 
push_spring_rotation_mechanism = Simulink.Variant('sim_type == "push_spring_rotation"');
push_push_rotation_mechanism = Simulink.Variant('sim_type == "push_push_rotation"');

simple_visuals_variant = Simulink.Variant('simplified_visualization == true'); % Use of enabled subsystem in this case does not work due to transmission of the physical signals
full_visuals_variant = Simulink.Variant('simplified_visualization == false'); % Consequantly, variant subsystem is the solution

% --- Grid ---

x_grid_vec = [-0.5 0.5] * 1e-3; % meters % [-0.5 0 0.5] * 1e-3;
% y_grid_vec = [0 0.03 0.07 0.2  0.29 0.31 0.4  0.53 0.57 0.6] * 1e-3; % meters
% z_grid_vec = [0 0    0.03 0.39 0.45 0.45 0.39 0.03 0.0  0.0] * 1e-3; % meters
y_grid_vec = half_y_grid_vec;
z_grid_vec = half_z_grid_vec;  % z is height

for i = 1 : length(half_y_grid_vec) % - 1 for the linear actuators -1 was always substracted
    y_grid_vec(i + length(half_y_grid_vec)) = tooth_pitch - half_y_grid_vec(length(half_y_grid_vec) + 1 - i);
    z_grid_vec(i + length(half_y_grid_vec)) = half_z_grid_vec(length(half_y_grid_vec) + 1 - i); % z is height
end

z_grid_mat = []; % meters
for i = 1 : length(x_grid_vec)
    z_grid_mat = [z_grid_mat; z_grid_vec];
end

if motion_type == "linear"
    point_cloud_tooth_mat = zeros(length(y_grid_vec), 3);
    point_cloud_tooth_mat(:,2) = y_grid_vec;
    point_cloud_tooth_mat(:,3) = z_grid_vec;
elseif motion_type == "rotary"
    tmp_tooth_mat = ones(length(y_grid_vec(2:end-1)), 3) * disk_diameter / 2;
    tmp_tooth_mat(:,2) = y_grid_vec(2:end-1);
    tmp_tooth_mat(:,3) = z_grid_vec(2:end-1);  % z is height
    % point_cloud_tooth_mat = tmp_tooth_mat;
    point_cloud_tooth_mat = [];
    if simplified_visualization % generate only part of the teeth to speed up the simulation
        disk_start_tooth = round((disk_teeth_count - 1) / 1.4);
        disk_end_tooth = round((disk_teeth_count - 1) / 2.6) + round((disk_teeth_count - 1) / 2.2);
        if tb_type == 2
            disk_end_tooth = disk_end_tooth + NaN; % TODO increase the number of teeth for tb type 2 disk
            disk_end_tooth = min(disk_end_tooth, disk_teeth_count - 1);
        end 
    else
        disk_start_tooth = 1;
        disk_end_tooth = disk_teeth_count - 1;
    end
    for i = disk_start_tooth : disk_end_tooth  % for i = 1 : disk_teeth_count - 1 % simulate all the teeth on the disk
        cur_rot_angle = 2*pi * i / disk_teeth_count;
        z_rot = [cos(cur_rot_angle) -sin(cur_rot_angle) 0;
                 sin(cur_rot_angle)  cos(cur_rot_angle) 0;
                 0                   0                  1];
        cur_tooth_cloud = tmp_tooth_mat * z_rot;
        point_cloud_tooth_mat = [point_cloud_tooth_mat; cur_tooth_cloud];
    end
    min_z = min(z_grid_vec);
    disk_half_width = 2.5e-4;
    disk_height = 2.5e-4;
    disk_cross_section = [(disk_diameter/2 - disk_half_width) min_z; (disk_diameter/2 - disk_half_width) (min_z-disk_height);
                          (disk_diameter/2 + disk_half_width) (min_z-disk_height); (disk_diameter/2 + disk_half_width) min_z]; % rotation around Z axis
end
plate_y_grid = [];
plate_z_grid = [];
rack_y_grid = [];
rack_z_grid = [];

for i = 0 : plate_teeth_cnt - 1
    plate_y_grid = [plate_y_grid (y_grid_vec + tooth_pitch * i)];
    plate_z_grid = [plate_z_grid z_grid_mat];
end
plate_y_grid = plate_y_grid - 3*tooth_pitch;
for i = 0 : rack_teeth_cnt - 1
    rack_y_grid = [rack_y_grid (y_grid_vec + tooth_pitch * i)];
    rack_z_grid = [rack_z_grid z_grid_mat];
end