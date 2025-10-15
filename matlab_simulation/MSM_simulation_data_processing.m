% processing collection of the MSM simulation data, data visualization
% get dictionary back: dict = getfield(load(filename), "sim_results_dictionary")
clear
% --- Notes ---
% big pitches:
% 4 tooth plates 4.5 N load is maximum movable load, hold force up to 12 N
% 6 tooth plates 11 N load is maximum movable load, hold force up to 18 N
% --- --- ---
% small pitches:
% Push-push linear: 6 plates: 25.5 N - maximum movable load, 31 N - hold force
% Push-push linear: 4 plates: over 25 N - maximum movable load, over 30 N - hold force
% push_spring: 4 plates: over 20 N - maximum movable load, over 30 N - hold force
% push_spring_rotation: 4 plates: less than 0.8 Nm - holding torque
% push_spring_rotation: 6 plates: less than 1.35 Nm - holding torque
% push_push_rotation: 4 plates: less than 0.39 Nm - holding torque

sim_data.sim_type = ["push_spring"]; % "push_spring" "push_push_linear" "push_spring_rotation" "push_push_rotation"
sim_data.pitch_type = ["prototype"]; % "small" or "big" or "force_optimal" or "prototype"
sim_data.tb_type = [1]; % 1 2
sim_data.tooth_plates_cnt = [4]; %[4 6 8]; % 4 6 8
% the data folder of interest can be selected manufally if "analysis_type" variable is defined
% analysis_type = "sensetivity_threshold_fraction"; % "performance" "sensetivity_force_threshold" "sensetivity_threshold_fraction"
plots_to_draw = ["force_frequency"]; % ["force_velocity" "force_frequency"]; % optins: "3d_feedback_fraction_vel" "3d_force_vel_feedback" 
% options [2]:  "3d_feedback_fraction_average_abs_acceleration" "3d_force_average_abs_acceleration"
% options [3]:  "force_velocity", "force_frequency", "power_force", "power_velocity", "average_abs_acceleration"
b_print_max_values = true;  % ture/false; prints abs max values of the measured parameters

if ~exist('analysis_type','var')
    if isempty(plots_to_draw)
        analysis_type = "performance";
    else 
        analysis_type = get_analysis_type(plots_to_draw); 
    end
end

[sim_data, name_data] = define_motion_type_properties(sim_data);
name_data.plot_name_extra = get_plot_name(sim_data);
visual_params.title_font_size = 22;
visual_params.lables_font_size = 24;
visual_params.legend_font_size = 17;

data_collection = {};
for tb_type_iter = sim_data.tb_type
for sim_type_iter = sim_data.sim_type
    for pitch_iter = sim_data.pitch_type
        for tooth_iter = sim_data.tooth_plates_cnt
            tmp_dict = parse_folder(analysis_type, tb_type_iter, sim_type_iter, pitch_iter, tooth_iter);
            if ~isa(tmp_dict,'dictionary'); continue; end
            if  ~isKey(tmp_dict , "tooth_plates_cnt") % previously dictionary did not include tooth_pitch_cnt, so this line is for compatibility
                tmp_dict("tooth_plates_cnt") = {tooth_iter};
            end
            data_collection{end+1} = tmp_dict;
        end
    end
end
end

if b_print_max_values
    max_tb_vel = [];  max_tooth_velocity = []; max_rack_acceleration = []; max_tooth_acceleration = []; max_twinning_stress = [];
for i = 1 : length(data_collection)
    max_tb_vel = max([max_tb_vel cell2mat(data_collection{i}("max_tb_velocity"))]);
    max_tooth_velocity = max([max_tooth_velocity cell2mat(data_collection{i}("max_tooth_velocity"))]);
    max_rack_acceleration = max([max_rack_acceleration cell2mat(data_collection{i}("max_rack_acceleration"))]);
    max_tooth_acceleration = max([max_tooth_acceleration cell2mat(data_collection{i}("max_tooth_acceleration"))]);
    max_twinning_stress = max([max_twinning_stress cell2mat(data_collection{i}("max_twinning_stress"))]);
end
    max_values = strcat(sim_data.sim_type(1), " ", sim_data.pitch_type(1), " tb type ", num2str(sim_data.tb_type(1)),...
        " max tb vel mm/s: ", num2str(round(max_tb_vel*1000)), " max tooth vel: ", num2str(round(max_tooth_velocity)),...
        " max rack acc, m/ss: ", num2str(max_rack_acceleration), " max tooth acc: m/ss", num2str(max_tooth_acceleration), ...
        " max TS, MPa: ", num2str(max_twinning_stress));
    disp(max_values)
end

if ~isempty(plots_to_draw)
if sum(ismember("force_velocity", plots_to_draw)) > 0.5; plot_force_velocity(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("power_velocity", plots_to_draw)) > 0.5; plot_power_velocity(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("power_force", plots_to_draw)) > 0.5; plot_power_force(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("force_frequency", plots_to_draw)) > 0.5; plot_force_frequency(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("3d_force_vel_feedback", plots_to_draw)) > 0.5; plot_3d_force_vel_feedback(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("3d_force_average_abs_acceleration", plots_to_draw)) > 0.5; plot_3d_force_average_abs_acceleration(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("3d_feedback_fraction_vel", plots_to_draw)) > 0.5; plot_3d_feedback_fraction_vel(data_collection, sim_data, name_data, visual_params); end
if sum(ismember("3d_feedback_fraction_average_abs_acceleration", plots_to_draw)) > 0.5; plot_3d_feedback_fraction_average_abs_acceleration(data_collection, sim_data, name_data, visual_params); end
end


function analysis_type = get_analysis_type(plots_to_draw)
    if sum(ismember("3d_feedback_fraction_vel", plots_to_draw)) > 0.5 ||...
        sum(ismember("3d_feedback_fraction_average_abs_acceleration", plots_to_draw))
        analysis_type = "sensetivity_threshold_fraction"; 
    elseif sum(ismember("3d_force_vel_feedback", plots_to_draw)) > 0.5 ||...
            sum(ismember("3d_force_average_abs_acceleration", plots_to_draw)) > 0.5
        analysis_type = "sensetivity_force_threshold";
    else
        analysis_type = "performance";
    end
end
function [sim_data, name_data] = define_motion_type_properties(sim_data)
    if sim_data.sim_type(1) == "push_spring" || sim_data.sim_type(1) == "push_push_linear"
        sim_data.motion_type = "linear";
        sim_data.motion_type_number = 0;
        name_data.velocity_name_string = 'Rack velocity (mm/s)';
        name_data.load_name_string = 'Load (N)';
    elseif sim_data.sim_type(1) == "push_push_rotation" || sim_data.sim_type(1) == "push_spring_rotation" 
        sim_data.motion_type = "rotary";
        sim_data.motion_type_number = 1;
        name_data.velocity_name_string = 'Output angular velocity (Rad/s)';
        name_data.load_name_string = 'Load (Nm)';
    else
        sim_data.motion_type = NaN;
        sim_data.motion_type_number = NaN;
    end
end
function data_dict = parse_folder(analysis_type, tb_type, sim_type, pitch_type, tooth_plates_cnt)
% returns NaN if a given folder is empty
    if analysis_type == "performance"
        folder = strcat("SimResults", filesep, "tb_type_", string(tb_type), filesep, sim_type,'_', pitch_type, '_pitch_plates_cnt_', string(tooth_plates_cnt));
    else
        folder = strcat("SimResults", filesep, analysis_type, filesep, "tb_type_", string(tb_type), filesep, sim_type,'_', pitch_type, '_pitch_plates_cnt_', string(tooth_plates_cnt));
    end
    files = dir(fullfile(folder,'*.mat'));
    if isempty(files)
        data_dict = NaN;
        disp(strcat('no files were found in folder: ', folder))
        return;
    end

    data_dictionary_cell = {};
    for i = 1 : length(files)
        filename = strcat(folder, filesep, getfield(files(i), "name"));
        data_dictionary_cell(end+1) = {getfield(load(filename), "sim_results_dictionary")};
    end

    frequency_vec = []; load_vec = [];
    velocity_vec = []; feedback_threshold_vec = [];
    next_vec_fraction_vec = []; abs_acc_integral_vec = [];
    high_pass_cutoff = 0.005;
    if          pitch_type == "small";   high_pass_cutoff = 0.005;
    elseif      pitch_type == "big"
        if      tooth_plates_cnt == 4;   high_pass_cutoff = 0.01;    % ?
        elseif  tooth_plates_cnt == 6;   high_pass_cutoff = 0.018;   % ?
        elseif  tooth_plates_cnt == 8;   high_pass_cutoff = 0.01;    % ?
        end
    end
    if          tb_type == 2;            high_pass_cutoff = 0.0005; end

    for i = 1 : length(files)
        tmp_data = data_dictionary_cell{i}; % unpacking data using {} brackets
        time = cell2mat(tmp_data("time"));
        %frequency_vec = [frequency_vec mean(rmoutliers(cell2mat(tmp_data("rack_single_element_frequency")), "quartiles"))];
        tmp_frequency = [cell2mat(tmp_data("rack_single_element_frequency"))];
        if isnan(tmp_frequency); tmp_frequency = 0; end  % sometimes frequency is saved incorrectly after simulation data post processing
        frequency_vec(end+1) = tmp_frequency;
        cur_load = cell2mat(tmp_data("useful_load"));
        load_vec = [load_vec cur_load];
        if isKey(tmp_data, "feedback_threshold"); feedback_threshold_vec = [feedback_threshold_vec cell2mat(tmp_data("feedback_threshold"))];
        else feedback_threshold_vec = [feedback_threshold_vec 0]; end
        if isKey(tmp_data, "next_vec_fraction"); next_vec_fraction_vec = [next_vec_fraction_vec cell2mat(tmp_data("next_vec_fraction"))];
        else next_vec_fraction_vec = [next_vec_fraction_vec 0]; end
        
        % starting not from the very beginning because of the initial transient processes
        start_cutoff_index = length(find(time < high_pass_cutoff));
        
        end_cutoff_index = length(find(time < 0.075));
        rack_acceleration = cell2mat(tmp_data("rack_acceleration"));
        rack_velocity = cell2mat(tmp_data("rack_velocity"));
        rack_position = cell2mat(tmp_data("rack_position"));
        average_vel = (rack_position(end_cutoff_index) - rack_position(start_cutoff_index)) / (time(end_cutoff_index) - time(start_cutoff_index));
        velocity_vec = [velocity_vec average_vel];

        tmp_abs_acc_integral = trapz(time, abs(rack_acceleration)) / time(end);
        abs_acc_integral_vec = [abs_acc_integral_vec tmp_abs_acc_integral];
        
        max_tb_velocity = max(abs(cell2mat(tmp_data("TB_velocity")))); % m/s
        max_tooth_velocity = max(abs(cell2mat(tmp_data("Tooth_velocity_mm_per_s")))); % mm/s
        max_rack_acceleration = max(abs(rack_acceleration));  % m/s^2 or rad/s^2
        max_tooth_acceleration = max(abs(cell2mat(tmp_data("tooth_acceleration")))); % m/s^2
        max_ts_const = max(abs(cell2mat(tmp_data("Twinning_stress_constant_part")))); % MPa
        max_ts_dyn = max(abs(cell2mat(tmp_data("Twinning_dynamic_resistance_force")))); % N!!!
        A0 = 4.0000; % mm^2, Note: not re-computable. TODO Make dynamicly changing if the crystal size is varied
        % max_twinning_stress =  max_ts_const + max_ts_dyn / A0 / 1e+6; % MPa; 
        if tb_type == 1
            max_twinning_stress =  0.6 + max_ts_dyn / A0; % MPa;
        elseif tb_type == 2
            max_twinning_stress =  0.1 + max_ts_dyn / A0; % MPa;
        end
    
    end
    velocity_vec(isnan(velocity_vec))=0; % first implementation of halt detection gave NaN values for halted velocities. This line fixes the problem
    sorted_vel_load_vec = sortrows([load_vec' velocity_vec' frequency_vec' feedback_threshold_vec' ...
        next_vec_fraction_vec' abs_acc_integral_vec']); % sortrows([velocity_vec' load_vec']);

    dict_keys = ["velocity_vec" "load_vec" "frequency_vec" "feedback_threshold_vec" "next_vec_fraction_vec" "abs_acc_integral_vec"...
        "max_tb_velocity" "max_tooth_velocity" "max_rack_acceleration" "max_tooth_acceleration" "max_twinning_stress"];
    % the order for data entries definition is not consecutive. TODO can it
    % be changed (by changing dict_keys positions) and then for-looped?
    dict_entries = {sorted_vel_load_vec(:, 2), sorted_vel_load_vec(:, 1), sorted_vel_load_vec(:, 3),...
        sorted_vel_load_vec(:, 4), sorted_vel_load_vec(:, 5), sorted_vel_load_vec(:, 6), max_tb_velocity...
        max_tooth_velocity, max_rack_acceleration, max_tooth_acceleration, max_twinning_stress};% {sorted_vel_load_vec(:, 1), sorted_vel_load_vec(:, 2)};
    data_dict = dictionary(dict_keys, dict_entries);
    data_dict("sim_type")   = data_dictionary_cell{1}("sim_type");
    data_dict("tb_type")    = data_dictionary_cell{1}("tb_type"); 
    data_dict("pitch_type") = data_dictionary_cell{1}("pitch_type");

    if  isKey(data_dictionary_cell{1}, "tooth_plates_cnt") % previously dictionary did not include tooth_pitch_cnt, so this line is for compatibility
        data_dict("tooth_plates_cnt") = data_dictionary_cell{1}("tooth_plates_cnt");
    end
end
function legend_name = get_legend_title(sim_data, tooth_iter, sim_type_iter, pitch_iter, tb_iter)
    tmp_legend_name = '';
    if length(sim_data.sim_type) > 1
        if sim_type_iter == "push spring"; sim_type_iter = "spring returned"; end % 
        if sim_type_iter == "push spring rotation"; sim_type_iter = "spring returned rotation"; end
        tmp_legend_name = strcat(sim_type_iter, ', ');
    end
    if length(sim_data.tooth_plates_cnt) > 1
        tmp_legend_name = strcat(tmp_legend_name, string(tooth_iter), " MSM el., ");
    end
    if length(sim_data.pitch_type) > 1
        tmp_legend_name = strcat(tmp_legend_name, pitch_iter, ' tooth, ');
    end
    if length(sim_data.tb_type) > 1
        tmp_legend_name = strcat(tmp_legend_name,'TB ', tb_iter, ', ');
    end
    legend_name = strrep(tmp_legend_name,'_',' ');
    legend_name = strtrim(legend_name);
    tmp_char = char(legend_name);
    if length(tmp_char) > 2 && tmp_char(end) == ','
        tmp_char = tmp_char(1:end-1);
        legend_name = string(tmp_char);
    end
end
function plot_name = get_plot_name(sim_data)
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    tmp_plot_name = '';
    if length(sim_type) == 1
        if sim_type == "push_spring"; sim_type = "spring returned"; end
        if sim_type == "push_spring_rotation"; sim_type = "spring returned rotation"; end
        tmp_plot_name = strcat(sim_type, ', ');
    end
    if length(tooth_plates_cnt) == 1
        tmp_plot_name = strcat(tmp_plot_name, string(tooth_plates_cnt), " MSM el., ");
    end
    if length(pitch_type) == 1
        tmp_plot_name = strcat(tmp_plot_name, pitch_type, ' tooth, ');
    end
    plot_name = strrep(tmp_plot_name,'_',' ');
    if plot_name ~= ""
        plot_name = strcat(', ', plot_name);
    end
    plot_name = strtrim(plot_name);
    tmp_char = char(plot_name);
    if length(tmp_char) > 2 
        if tmp_char(end-1) == ','
            tmp_char = tmp_char(1:end-2);
            plot_name = string(tmp_char);
        elseif tmp_char(end) == ','
            tmp_char = tmp_char(1:end-1);
            plot_name = string(tmp_char);
        end
    end
    % if plot_name(end-1) == ','; plot_name = plot_name(1:end-2); end
end
function plot_force_velocity(data_collection, sim_data, name_data, visual_params)
    figure('Name', strcat('Force/velocity plot', name_data.plot_name_extra), 'Color', [1 1 1])
    title(strcat('Force/velocity ', name_data.plot_name_extra), 'FontSize', visual_params.title_font_size)
    legend_titles = {};
    for data_sample = data_collection
                if sim_data.motion_type == "linear"
                    plot(cell2mat(data_sample{1}("velocity_vec"))*1e+3, cell2mat(data_sample{1}("load_vec")), '-x', 'LineWidth', 3)  
                    % semilogx(abs(cell2mat(data_sample{1}("velocity_vec"))*1e+3) + 1e-5, cell2mat(data_sample{1}("load_vec")), '-x', 'LineWidth', 3)
                else
                    plot(abs(cell2mat(data_sample{1}("velocity_vec"))), cell2mat(data_sample{1}("load_vec")), '-x', 'LineWidth', 3)
                end
                legend_titles{end+1} = get_legend_title(sim_data, cell2mat(data_sample{1}("tooth_plates_cnt")), ...
                   string(data_sample{1}("sim_type")), string(data_sample{1}("pitch_type")), string(data_sample{1}("tb_type")));
                hold on;
    end
    fontsize(gcf, visual_params.lables_font_size,"points"); 
    xlim([1 inf]) % needed for the log plot to work correctly
    xlabel(name_data.velocity_name_string) 
    ylabel(name_data.load_name_string) % , 'FontSize', 12
    lgd = legend(legend_titles);
    fontsize(lgd,visual_params.legend_font_size,'points')
    grid on;
    hold off
end
function plot_power_velocity(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Power/velocity ', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Power/velocity ', plot_name_extra), 'FontSize', visual_params.title_font_size)
    grid on; hold on; legend_titles = {};
    for data_sample = data_collection
        if motion_type == "linear"
            plot(cell2mat(data_sample{1}("velocity_vec"))*1e+3, cell2mat(data_sample{1}("load_vec")).*cell2mat(data_sample{1}("velocity_vec")), '-x', 'LineWidth', 3)  
        else
            plot(abs(cell2mat(data_sample{1}("velocity_vec"))), abs(cell2mat(data_sample{1}("load_vec")).*cell2mat(data_sample{1}("velocity_vec"))), '-x', 'LineWidth', 3)
        end
        legend_titles{end+1} = get_legend_title(cell2mat(data_sample{1}("tooth_plates_cnt")), tooth_plates_cnt, ...
                   string(data_sample{1}("sim_type")), sim_type, string(data_sample{1}("pitch_type")), pitch_type);
    end
    fontsize(gcf, visual_params.lables_font_size,"points"); legend(legend_titles)
    xlabel(velocity_name_string) 
    ylabel('Power (W)') 
    hold off
end
function plot_power_force(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Power/force ', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Power/force ', plot_name_extra), 'FontSize', visual_params.title_font_size)
    grid on; hold on; legend_titles = {};
    for data_sample = data_collection
        plot(abs(cell2mat(data_sample{1}("load_vec"))), abs(cell2mat(data_sample{1}("load_vec")).*cell2mat(data_sample{1}("velocity_vec"))), '-x', 'LineWidth', 3)
        legend_titles{end+1} = get_legend_title(cell2mat(data_sample{1}("tooth_plates_cnt")), tooth_plates_cnt, ...
                   string(data_sample{1}("sim_type")), sim_type, string(data_sample{1}("pitch_type")), pitch_type);
    end
    fontsize(gcf, visual_params.lables_font_size,"points"); lgnd = legend(legend_titles);
    set(lgnd,'color','none');
    xlabel(load_name_string) 
    ylabel('Power, W') 
    hold off
end
function plot_force_frequency(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Force/frequency plot', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Force/frequency ', plot_name_extra), 'FontSize', visual_params.title_font_size)
      legend_titles = {};
    for data_sample = data_collection
                plot(cell2mat(data_sample{1}("frequency_vec")), cell2mat(data_sample{1}("load_vec")), '-x', 'LineWidth', 3)
                % semilogx(abs(cell2mat(data_sample{1}("frequency_vec"))) + 1e-5, cell2mat(data_sample{1}("load_vec")), '-x', 'LineWidth', 3)
                legend_titles{end+1} = get_legend_title(sim_data, cell2mat(data_sample{1}("tooth_plates_cnt")), ...
                   string(data_sample{1}("sim_type")), string(data_sample{1}("pitch_type")), string(data_sample{1}("tb_type")));
                hold on;
    end
    fontsize(gcf, visual_params.lables_font_size,"points"); lgd = legend(legend_titles);
    % set(lgd,'color','none');
    fontsize(lgd,visual_params.legend_font_size,'points')
    xlabel("Single MSM element frequency (Hz)") 
    ylabel(load_name_string) % , 'FontSize', 12
    xlim([1 inf]) % needed for the log plot to work correctly
    grid on;
    hold off
end
function plot_3d_force_vel_feedback(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Feedback and force sensetivity', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Feedback and force sensetivity ', plot_name_extra), 'FontSize', visual_params.title_font_size)
    hold on; legend_titles = {};
    x = []; y = []; z = [];
    for data_sample = data_collection
        % plot3(cell2mat(data_sample{1}("feedback_threshold_vec")), cell2mat(data_sample{1}("load_vec")), cell2mat(data_sample{1}("velocity_vec")), 'o')
        legend_titles{end+1} = get_legend_title(cell2mat(data_sample{1}("tooth_plates_cnt")), tooth_plates_cnt, ...
                    string(data_sample{1}("sim_type")), sim_type, string(data_sample{1}("pitch_type")), pitch_type);
        x = cell2mat(data_sample{1}("feedback_threshold_vec"));
        y = cell2mat(data_sample{1}("load_vec"));
        z = cell2mat(data_sample{1}("velocity_vec"));
        stem3(x, y, z)
        grid on
        xv = linspace(min(x), max(x), 50);
        yv = linspace(min(y), max(y), 50);
        [X,Y] = meshgrid(xv, yv);
        Z = griddata(x,y,z,X,Y);
        %figure(2)
        surf(X, Y, Z);
        grid on
    end
    
    fontsize(gcf, visual_params.lables_font_size,"points"); 
%    lgnd = legend(legend_titles);
%    set(lgnd,'color','none');
    xlabel("Teeth engagement offset") 
    ylabel(load_name_string) % , 'FontSize', 12
    zlabel(velocity_name_string)
    hold off
end
function plot_3d_force_average_abs_acceleration(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Average abs acceleration vs force ', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Average abs acceleration vs force ', plot_name_extra), 'FontSize', visual_params.title_font_size)
    hold on; legend_titles = {};
    x = []; y = []; z = [];
    for data_sample = data_collection
        % plot3(cell2mat(data_sample{1}("feedback_threshold_vec")), cell2mat(data_sample{1}("load_vec")), cell2mat(data_sample{1}("velocity_vec")), 'o')
        legend_titles{end+1} = get_legend_title(cell2mat(data_sample{1}("tooth_plates_cnt")), tooth_plates_cnt, ...
                    string(data_sample{1}("sim_type")), sim_type, string(data_sample{1}("pitch_type")), pitch_type);
        x = cell2mat(data_sample{1}("feedback_threshold_vec"));
        y = cell2mat(data_sample{1}("load_vec"));
        z = cell2mat(data_sample{1}("abs_acc_integral_vec"));
        stem3(x, y, z)
        grid on
        xv = linspace(min(x), max(x), 50);
        yv = linspace(min(y), max(y), 50);
        [X,Y] = meshgrid(xv, yv);
        Z = griddata(x,y,z,X,Y);
        %figure(2)
        surf(X, Y, Z);
        grid on
    end
    
    fontsize(gcf, visual_params.lables_font_size,"points"); 
%    lgnd = legend(legend_titles);
%    set(lgnd,'color','none');
    xlabel("Teeth engagement offset") 
    ylabel(load_name_string) % , 'FontSize', 12
    zlabel("Average abs acceleration mm/s^2")
    hold off
end
function plot_3d_feedback_fraction_vel(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Feedback and fraction sensetivity', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Feedback and fraction sensetivity ', plot_name_extra), 'FontSize', visual_params.title_font_size)
    hold on; legend_titles = {};
    x = []; y = []; z = [];
    for data_sample = data_collection
        % plot3(cell2mat(data_sample{1}("feedback_threshold_vec")), cell2mat(data_sample{1}("load_vec")), cell2mat(data_sample{1}("velocity_vec")), 'o')
        legend_titles{end+1} = get_legend_title(cell2mat(data_sample{1}("tooth_plates_cnt")), tooth_plates_cnt, ...
                    string(data_sample{1}("sim_type")), sim_type, string(data_sample{1}("pitch_type")), pitch_type);
        x = cell2mat(data_sample{1}("feedback_threshold_vec"));
        y = cell2mat(data_sample{1}("next_vec_fraction_vec"));
        z = cell2mat(data_sample{1}("velocity_vec"));
        stem3(x, y, z)
        grid on
        xv = linspace(min(x), max(x), 30);
        yv = linspace(min(y), max(y), 30);
        [X,Y] = meshgrid(xv, yv);
        Z = griddata(x,y,z,X,Y);
        %figure(2)
        surf(X, Y, Z);
        grid on
    end
    fontsize(gcf, visual_params.lables_font_size,"points"); 
%    lgnd = legend(legend_titles);
%    set(lgnd,'color','none');
    xlabel("Teeth engagement offset") 
    ylabel("Teeth disengagement offset") % , 'FontSize', 12
    zlabel(velocity_name_string)
    hold off
end
function plot_3d_feedback_fraction_average_abs_acceleration(data_collection, sim_data, name_data, visual_params)
    motion_type = sim_data.motion_type;
    plot_name_extra = name_data.plot_name_extra;
    velocity_name_string = name_data.velocity_name_string;
    load_name_string = name_data.load_name_string;
    tooth_plates_cnt = sim_data.tooth_plates_cnt;
    sim_type = sim_data.sim_type;
    pitch_type = sim_data.pitch_type;

    figure('Name', strcat('Average abs acceleration ', plot_name_extra), 'Color', [1 1 1])
    title(strcat('Average abs acceleration ', plot_name_extra), 'FontSize', visual_params.title_font_size)
    hold on; legend_titles = {};
    x = []; y = []; z = [];
    for data_sample = data_collection
        % plot3(cell2mat(data_sample{1}("feedback_threshold_vec")), cell2mat(data_sample{1}("load_vec")), cell2mat(data_sample{1}("velocity_vec")), 'o')
        legend_titles{end+1} = get_legend_title(cell2mat(data_sample{1}("tooth_plates_cnt")), tooth_plates_cnt, ...
                    string(data_sample{1}("sim_type")), sim_type, string(data_sample{1}("pitch_type")), pitch_type);
        x = cell2mat(data_sample{1}("feedback_threshold_vec"));
        y = cell2mat(data_sample{1}("next_vec_fraction_vec"));
        z = cell2mat(data_sample{1}("abs_acc_integral_vec"));
        stem3(x, y, z)
        grid on
        xv = linspace(min(x), max(x), 30);
        yv = linspace(min(y), max(y), 30);
        [X,Y] = meshgrid(xv, yv);
        Z = griddata(x,y,z,X,Y);
        %figure(2)
        surf(X, Y, Z);
        grid on
    end
    fontsize(gcf, visual_params.lables_font_size,"points"); 
%    lgnd = legend(legend_titles);
%    set(lgnd,'color','none');
    xlabel("Teeth engagement offset") 
    ylabel("Teeth disengagement offset") % , 'FontSize', 12
    zlabel("Average abs acceleration mm/s^2")
    hold off
end