% names = ["Unicycle" "Bicycle" "Tricyle"];
% wheels = {[1; 2; 3], [-1], "sdfsdfsd" };
% d = dictionary(names,wheels);

original_folder = strcat(pwd, filesep, "SimResults\pid_data\force_optimal_pitch_plates_cnt_4");
excel_folder = "SimResults\pid_data\excel_force_optimal_pitch_plates_cnt_4";
full_path_excel_folder = strcat(pwd, filesep, excel_folder);
original_files = dir(fullfile(original_folder, '*.mat'));
processed_files = dir(fullfile(full_path_excel_folder, '*.xlsx'));
%TODO from here

orig_vec = {}; processed_vec = {};
% dict_filename = "ML_control\test_matlab_dictionary.mat";
for i = 1 : length(original_files)
    orig_vec{i} = original_files(i).name(1:end-4);
end
for i = 1 : length(processed_files)
    processed_vec{i} = processed_files(i).name(1:end-5);
end

files_to_process =  setdiff(orig_vec, processed_vec, 'stable');
disp('all files length')
length(orig_vec)
disp('processed files length')
length(processed_vec)
disp('to process files length')
length(files_to_process)


w = warning ('off','all');
for i = 1 : length(files_to_process)
    cur_file = files_to_process(i); % files(i).name;
    cur_file_path = strcat(original_folder, filesep, cur_file);
    full_excel_path = strcat(excel_folder, filesep, cur_file, '.xlsx'); % cur_file(1:end-4), '.xlsx');
    d = load(cur_file_path); %dict_filename
    d = d.sim_results_dictionary;
    k = keys(d);
    
    for j = 1 : length(k)
        data = d(k(j));
        try  % try catch needs if we are trying to convert a string. In this case nothing will happen
            data = cell2mat(data);
        catch
        end
        xlswrite(full_excel_path,data,k(j))
    end
    if mod(i,5) == 0
        disp(strcat('copied ', string(i), ' files out of:', string(length(files_to_process))))
    end
end
w = warning ('on','all');