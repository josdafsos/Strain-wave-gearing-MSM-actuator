function [velocity, frequency, amplitude] = get_random_motion_profile(profile_type)
% Function generates random motion properties that are suitable for simulation
% Params:
% profile_type - integer in [1...4] range; 1 - constant motion, 2 -square,
% 3 - sawtooth, 4 - sine
MAX_VELOCITY = 0.03; % m/s
velocity = (rand - 0.5) * 2 * MAX_VELOCITY; % m/s, range from -0.03 to +0.03
amplitude = (MAX_VELOCITY - abs(velocity)) * sign(rand - 0.5) * rand;
if profile_type == 1
    frequency = 1e-3;
elseif profile_type == 2
    frequency = rand*400 + 200; % rad/s
elseif profile_type == 3
    frequency = rand*800 + 200; % rad/s
else
    frequency = rand*400 + 150;
end

end