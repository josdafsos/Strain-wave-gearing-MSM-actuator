function msm_props_struct = get_msm_properties(tb_type, is_simple_visualization)
% MSM crystal properties

% msm_props_dict = dictionary;

% --- Masses ---
msm_props_struct.tooth_plate_mass = 0.22e-3; % kg
msm_props_struct.rack_mass = 1.5e-3; % kg
msm_props_struct.swing_mass = 1e-3; % kg TODO set a proper mass, not a guess
msm_props_struct.tooth_disk_mass = 5e-3; % kg TODO set a proper mass, not a guess

% --- MSM crystal paratemers ---
% The msm full length is considered to be at fully extended position.

msm_props_struct.msm_length = 10e-3; % meters
msm_props_struct.msm_width = 4e-3; % meters
msm_props_struct.msm_height = 1e-3; % meters
msm_props_struct.A0 = msm_props_struct.msm_width * msm_props_struct.msm_height; % MSM crystal cross section area

msm_props_struct.e_0 = 0.06; % max elongation, from Saren and Ullakko, approximate value
msm_props_struct.allowed_elongation = 0.05; % full extension is not allowed to keep the TB and increase cyclic life
msm_props_struct.one_side_elongation_capacity = ( msm_props_struct.e_0 - msm_props_struct.allowed_elongation ) / 2; % Used as an offset and shows the amount of possible additional elongation/contraction
msm_props_struct.one_side_absolute_offset = msm_props_struct.one_side_elongation_capacity * msm_props_struct.msm_length;
msm_props_struct.e_initial = 0.05; % initial contraction
msm_props_struct.contraction_initial = -msm_props_struct.msm_length * msm_props_struct.e_initial; % meters, value wrt to the full elongation, same as initial position of the Twin Boundary

msm_props_struct.ro = 8000; % kg/m^3
msm_props_struct.msm_mass = msm_props_struct.ro * msm_props_struct.A0 * msm_props_struct.msm_length; % total mass of msm element

% Note following line and other code related to inital TB position and TB
% mass are implemented in MSM element Simscape model directly
% tb_initial_position = (abs(contraction_initial) + one_side_absolute_offset) / e_0; % meters TODO IS THAT CORRECT???
% msm_tb_mass_initial = msm_mass * (e_initial + one_side_elongation_capacity ) / e_0; % Let's for now consider the initial retoriented mass proportional to current strain. TODO is it correct?

msm_props_struct.constant_magnetic_stress = 3.27e+6; % Pa, from Saren and Ullakko 2017, ref [24] there
msm_props_struct.k_0 = 11.8; % from Saren and Ullakko 2017
msm_props_struct.cos_a = cos(deg2rad(43.23));

msm_props_struct.max_tooth_motion_range = -2e-6; % meters, basically 0, but needs to avoid the zero crossing
msm_props_struct.min_tooth_motion_range = -msm_props_struct.msm_length * msm_props_struct.allowed_elongation;


% -- Friction and damping -- 
% Consider bronze-stainless steel friction pair. Tooth
% plates are from Bronze, other elements from stainless steel (or another
% hard material that is not ferromagnetic

% Twinning stress friction
if tb_type == 1
    msm_props_struct.coulomb_friction_ts = (0.6 * msm_props_struct.A0)*(1e+6);  % MPa
elseif tb_type == 2
    msm_props_struct.coulomb_friction_ts = (0.1 * msm_props_struct.A0)*(1e+6);  % MPa
else
    msm_props_struct.coulomb_friction_ts = NaN;
    error('Unknown Twin boundary type, only values of 1 or 2 are possible')
end

% --- visualization ---
msm_props_struct.solid_block_opacity = 0.3;
msm_props_struct.moving_tb_color = [0.0 0.0 0.0];

% msm_props_struct.simple_visuals_variant = Simulink.Variant('simplified_visualization == true'); % Use of enabled subsystem in this case does not work due to transmission of the physical signals
% msm_props_struct.full_visuals_variant = Simulink.Variant('simplified_visualization == false'); % Consequantly, variant subsystem is the solution

% crystal_visualization_length =msm_length+msm_width; % in case the TB is tilted
msm_props_struct.crystal_visualization_length = msm_props_struct.msm_length; % in case the TB is flat

% --- Other ---
msm_props_struct.force_control_coeff = 1.0; % to reduce MFIS value

end