function tooth_struct = get_tooth_properties(pitch_type, tb_type, sim_type, tooth_plates_cnt, simplified_visualization, SIMULATION_TIME, msm_props)
% tooth plate and rack properties
% MSM mechanism simulation properties


% other adjustable properties that are not intended for manual adjustment
if ~exist('max_teeth_passed','var'); tmp_s.max_teeth_passed = 5; end  % simulation will stop after this number of teeth will be passed
if ~exist('feedback_threshhold_offset','var'); tmp_s.feedback_threshhold_offset = 0.0; end  % [-1; 1] range, defines the actuation offset of the MSM element actuation
if ~exist('next_vec_fraction','var'); tmp_s.next_vec_fraction = 0.0; end  % [-CR; +CR] range, defines the disengagement timing for the last tooth, positive value leads to earlier disengagement


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

% ---- Control parametrs ----
tmp_s.disk_diameter = 35e-3; % m, central diameter of the teeth disk. For rotatary actuators only

% ---- Model properties ----
if sim_type == "push_spring" || sim_type == "push_push_linear"
    tmp_s.motion_type = "linear";
    tmp_s.motion_type_number = 0;
elseif sim_type == "push_push_rotation" || sim_type == "push_spring_rotation" 
    tmp_s.motion_type = "rotary";
    tmp_s.motion_type_number = 1;
else
    tmp_s.motion_type = NaN;
    tmp_s.motion_type_number = NaN;
end

% --- Masses ---
tmp_s.tooth_plate_mass = 0.22e-3; % kg
tmp_s.rack_mass = 1.5e-3; % kg
tmp_s.swing_mass = 1e-3; % kg TODO set a proper mass, not a guess
tmp_s.tooth_disk_mass = 5e-3; % kg TODO set a proper mass, not a guess

% --- Tooth properties ---

tmp_s.tooth_alpha = deg2rad(20); % rad, inclinations of the tooth profile

if pitch_type == "big"
    tmp_s.tooth_pitch = 0.6*1e-3; % meters
    tmp_s.tooth_height = 0.46*1e-3; % meters, max elongation is 0.5*1e-3, so there is some safety margin
    t_a = 0.15*1e-3 * 0.3; % meters, the second multiplier is to improve feedback control performance as the tooth plates will engage a bit earlier. This approach exploits roundings presents on the teeth
    t_b = 0.15*1e-3; % meters
    if sim_type == "push_spring" || sim_type == "push_spring_rotation"
        tmp_s.feedback_threshold = 0.80;
    else
        tmp_s.feedback_threshold = 0.85;
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
    tmp_s.feedback_threshold = 0.97; % the performance analysys simulations ran with this value (0.97) 
        
    % accurate radiuses on the bottom
    %     half_y_grid_vec = [0 0.02868 0.04698 0.05431 0.20790 0.22296 0.24229 0.26154] * 1e-3;
    %     half_z_grid_vec = ([0 0.00904 0.03290 0.05303 0.47500 0.49766 0.50949 0.51303] - 0.05303) * 1e-3;
    % simplified tooth profile
    half_y_grid_vec =  [0.03501 0.20790 0.22296 0.24229 0.26154] * 1e-3;
    half_z_grid_vec = ([0       0.47500 0.49766 0.50949 0.51303] - 0.05303) * 1e-3;
elseif pitch_type == "force_optimal"
    tmp_s.feedback_threshold = 0.98; % the performance analysys simulations ran with this value (0.98)
    tooth_height = 0.49*1e-3; % m, the max tooth height is 0.5 mm, but let's keep some margin
    t_b = tooth_height * tan(tooth_alpha); % m
    t_a = 3e-6; % m, keep it non-zero for computational purpusoses
    tooth_pitch = 2 * (t_a + t_b);
    half_y_grid_vec = [ 0.01*t_a          t_a/2  t_b + t_a/2          t_b + t_a/3 + t_a/2 ];
    half_z_grid_vec = [-0.01*tooth_height 0      tooth_height         tooth_height        ]; % the last term is needed because a tooth plate may jam with points around a tooth
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
tmp_s.t_a = t_a;
tmp_s.t_b = t_b;
tmp_s.tooth_pitch = tooth_pitch;
tmp_s.tooth_height = tooth_height;

tmp_s.contact_ratio = tooth_plates_cnt / (2 * (t_a / t_b + 1));

% --- Returning spring properties ---
if tb_type == 2
    tmp_s.spring_y_offset = 5e-3; % meters, 0.5e-3
    tmp_s.spting_natural_length = 20e-3 + tmp_s.spring_y_offset; % m 5e-3 + spring_y_offset
    tmp_s.spring_stiffness = 0.5e+2; % N/m 1e+2
elseif tb_type == 1
    tmp_s.spring_y_offset = 5e-3; % meters, old, used for simulations: 0.5e-3
    tmp_s.spting_natural_length = 20e-3 + tmp_s.spring_y_offset; % m, old, used for simulations: 5e-3 + spring_y_offset
    tmp_s.spring_stiffness = 3.40e+2; % N/m, old, used for simulations: 1.70e+2
end

if sim_type == "push_push_linear" || sim_type == "push_push_rotation"
    tmp_s.spring_stiffness = 1e-15; % basically equal to zero as this spring is not used for the mechanisms
    tmp_s.swing_spring_upper_offset = 3e-3; % m
    tmp_s.swing_spring_crank_length = 3e-3; % m
    tmp_s.swing_spring_natural_length = (tmp_s.swing_spring_crank_length + tmp_s.swing_spring_upper_offset) / 2; % m
    tmp_s.swing_spring_compressed_length = (tmp_s.swing_spring_crank_length + tmp_s.swing_spring_upper_offset...  % 35 is a bit too low, 45 is a bit too much
            - tmp_s.swing_spring_natural_length);
    if tb_type == 1
        tmp_s.swing_spring_stiffness = 45 / tmp_s.swing_spring_compressed_length; % N / m, desired force devided by elongation; 35 is a bit too low, 45 is a bit too much
        if pitch_type == "force_optimal"
            tmp_s.swing_spring_stiffness = 25 / tmp_s.swing_spring_compressed_length; % N / m, desired force devided by elongation; the contracted element might not have enough force to overcome the spring, so the spring stiffnes might be reduced
        end
    elseif tb_type == 2  % for now, keep the same spring properties
        tmp_s.swing_spring_stiffness = 45 / tmp_s.swing_spring_compressed_length; % N / m, desired force devided by elongation; 35 is a bit too low, 45 is a bit too much
        if pitch_type == "force_optimal"
            tmp_s.swing_spring_stiffness = 25 / tmp_s.swing_spring_compressed_length; % N / m, desired force devided by elongation; the contracted element might not have enough force to overcome the spring, so the spring stiffnes might be reduced
        end
    end
end

tmp_s.plate_teeth_cnt = 1;
% correcting the disk diameter to match the integer number of teeth
tmp_s.disk_teeth_count = ceil(pi * tmp_s.disk_diameter / tooth_pitch);
tmp_s.disk_diameter = tmp_s.disk_teeth_count * tooth_pitch / pi;

% -- Friction and damping -- 
% Consider bronze-stainless steel friction pair. Tooth
% plates are from Bronze, other elements from stainless steel (or another
% hard material that is not ferromagnetic

tmp_s.rack_coulumb_friction = 0.01; % N, based on approximation with plastic and bronze parts for prototype
tmp_s.rotational_rack_coulumb_friction = tmp_s.rack_coulumb_friction * tmp_s.disk_diameter;  % Nm
% TODO add proper values for contact forces, right now there is some
% default non-zero friction values
% contact friction:
tmp_s.rack_contact_coeff_static_friction = 0.16; % source https://mechguru.com/machine-design/typical-coefficient-of-friction-values-for-common-materials/
tmp_s.bronze_steel_kinetic_friction = 0.16; % source https://mechguru.com/machine-design/typical-coefficient-of-friction-values-for-common-materials/
tmp_s.steel_steel_contact_coeff_kinetic_friction = 0.23; % same source
tmp_s.rotational_contact_coeff_kinetic_friction = tmp_s.bronze_steel_kinetic_friction * tmp_s.disk_diameter / (2*pi);


% --- visualization ---
tmp_s.rotary_gear_contact_sphere_radius = 1e-5; % m
tmp_s.linear_msm_elements_contact_sphere_radius = 8e-6; % m

% Tooth plate dimensions
tmp_s.tooth_plate_height = 4.64e-3; % meters, from tooth bottom to the other edge of the plate

if abs(msm_props.min_tooth_motion_range) < tooth_height; disp('MSM motion range is smaller than tooth height! Motion is NOT possible'); end

tmp_s.angle_single_tooth_step         = 2*pi * tooth_pitch / tooth_plates_cnt / (pi*tmp_s.disk_diameter);
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

    angle_tooth_plates_pitch        = 2*pi * (-23*tooth_pitch + tooth_plates_pitch) / (pi*tmp_s.disk_diameter);
    in_pair_angle_tooth_plates_pitch        = 2*pi * (-2*tooth_pitch + in_pair_tooth_plates_pitch) / (pi*tmp_s.disk_diameter);
    swing_block_angle_tooth_plates_pitch    = 2*pi * (-7*tooth_pitch + swing_block_tooth_plates_pitch) / (pi*tmp_s.disk_diameter);
end
tmp_s.rack_teeth_cnt = rack_teeth_cnt;
tmp_s.tooth_plates_pitch = tooth_plates_pitch;
tmp_s.in_pair_tooth_plates_pitch = in_pair_tooth_plates_pitch;
tmp_s.swing_block_tooth_plates_pitch = swing_block_tooth_plates_pitch;
tmp_s.angle_tooth_plates_pitch = angle_tooth_plates_pitch;
tmp_s.in_pair_angle_tooth_plates_pitch = in_pair_angle_tooth_plates_pitch;
tmp_s.swing_block_angle_tooth_plates_pitch = swing_block_angle_tooth_plates_pitch;


tmp_s.swing_end_offset = -tmp_s.tooth_plate_height/3; % seems to work: -tooth_plate_height/2;
tmp_s.swing_coord_vec = [tmp_s.in_pair_tooth_plates_pitch/2 
                   tmp_s.swing_end_offset + msm_props.min_tooth_motion_range * tmp_s.feedback_threshold / 2
                   msm_props.msm_height];
tmp_s.swing_length = tmp_s.in_pair_tooth_plates_pitch * 0.5;
if tmp_s.motion_type == "rotary"
    tmp_s.swing_coord_vec(1) = 0;
end

% --- Other ---
if tmp_s.motion_type == "linear"
    if simplified_visualization
        rack_initial_position = 10 * tooth_pitch;  % the value must be in phase with tooth plates, meters
        if tb_type == 2; rack_initial_position = 60 * tooth_pitch; end
    else
        rack_initial_position = 85 * tooth_pitch;  % the value must be in phase with tooth plates, meters
    end
    MAX_OVERLOAD_VELOCITY = 2.5; % m/s; If the rack reaches the value the mechanism is considered overloaded and simulation stops
    HALT_VELOCITY = 1e-3; % m/s; if the average rack velocity is lower than this value, the actuator is considered halted
    MAX_POSITION = tmp_s.max_teeth_passed * tooth_pitch; % m, before was 7; push-spring 8 plates - 10 teeth to end, push-push - 8 plates (taking one less than max)
elseif tmp_s.motion_type == "rotary"
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
tmp_s.rack_initial_position = rack_initial_position;
tmp_s.MAX_OVERLOAD_VELOCITY = MAX_OVERLOAD_VELOCITY;
tmp_s.HALT_VELOCITY = HALT_VELOCITY;
tmp_s.MAX_POSITION = MAX_POSITION;

% simulation stopping codes (for halt or overload detection
tmp_s.SIM_OK = 0;
tmp_s.SIM_HALT = 1; % the MSM elements cannot push the rack, 0 velocity is reached
tmp_s.SIM_OVERLOAD = 2; % the loading force is too strong to backdrive the actuator
tmp_s.SIM_MAX_POS_REACHED = 3; % simulation is stopped when max position is reached, considered as a normal state

tmp_s.VALIDATION_START_TIME = 0.05*SIMULATION_TIME; % Time from which the check for stop is strarted (needs to eliminate the transient processes)
if sim_type == "push_push_linear" || sim_type == "push_push_rotation"
    tmp_s.VALIDATION_START_TIME = 0.15*SIMULATION_TIME;
    if pitch_type == "force_optimal"
        tmp_s.VALIDATION_START_TIME = 0.25*SIMULATION_TIME;
    end
end

% CAD file paths: 
% flat_tooth_plate_cad_path = 'Tooth plate single piece.STEP';
% rack_cad_path = 'Rack.STEP';

% linear_mechanism = Simulink.Variant('motion_type == "linear"'); 
% rotary_mechanism = Simulink.Variant('motion_type == "rotary"'); 
% 
% four_tooth_plates = Simulink.Variant('tooth_plates_cnt == 4');
% six_tooth_plates = Simulink.Variant('tooth_plates_cnt == 6');
% eight_tooth_plates = Simulink.Variant('tooth_plates_cnt == 8');
% 
% push_spring_mechanism = Simulink.Variant('sim_type == "push_spring"'); 
% push_push_linear_mechanism = Simulink.Variant('sim_type == "push_push_linear"'); 
% push_spring_rotation_mechanism = Simulink.Variant('sim_type == "push_spring_rotation"');
% push_push_rotation_mechanism = Simulink.Variant('sim_type == "push_push_rotation"');


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

if tmp_s.motion_type == "linear"
    point_cloud_tooth_mat = zeros(length(y_grid_vec), 3);
    point_cloud_tooth_mat(:,2) = y_grid_vec;
    point_cloud_tooth_mat(:,3) = z_grid_vec;
elseif tmp_s.motion_type == "rotary"
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
    tmp_s.disk_cross_section = [(disk_diameter/2 - disk_half_width) min_z; (disk_diameter/2 - disk_half_width) (min_z-disk_height);
                                (disk_diameter/2 + disk_half_width) (min_z-disk_height); (disk_diameter/2 + disk_half_width) min_z]; % rotation around Z axis
end
tmp_s.point_cloud_tooth_mat = point_cloud_tooth_mat;


plate_y_grid = [];
plate_z_grid = [];
rack_y_grid = [];
rack_z_grid = [];

for i = 0 : tmp_s.plate_teeth_cnt - 1
    tmp_s.plate_y_grid = [plate_y_grid (y_grid_vec + tooth_pitch * i)];
    tmp_s.plate_z_grid = [plate_z_grid z_grid_mat];
end
tmp_s.plate_y_grid = plate_y_grid - 3*tooth_pitch;
for i = 0 : rack_teeth_cnt - 1
    tmp_s.rack_y_grid = [rack_y_grid (y_grid_vec + tooth_pitch * i)];
    tmp_s.rack_z_grid = [rack_z_grid z_grid_mat];
end

tooth_struct = tmp_s;

end