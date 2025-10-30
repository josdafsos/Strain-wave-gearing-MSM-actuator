function sim_in = fill_simulations_properties(sim_in, cell_struct_vec, model)
% Defines variables from cell vector "cell_struct_vec" in simulink model sim_in, 
% wokspace of the model is provided in model. If model is not provided
% workspace is default

for i = 1 : length(cell_struct_vec)
    fields = fieldnames(cell_struct_vec{i});
    for j = 1 : length(fields)
        val = getfield(cell_struct_vec{i}, fields{j});
        if nargin > 2
            sim_in = sim_in.setVariable(fields{j}, val, "Workspace", model);
        else
            sim_in = sim_in.setVariable(fields{j}, val);
        end
    end
end

end