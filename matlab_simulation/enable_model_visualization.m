function enable_model_visualization(enable_visualization)
% switches ON or OFF visualization of the simulation
% enable_visualization: bool, true = visualizaion is on, false = visualization is off
    if enable_visualization
        state = 'on';
    else
        state = 'off';
    end
    model = 'MSM_strain_wave_actuator';
    load_system(model);
    cur_state = get_param(model,'SimMechanicsOpenEditorOnUpdate');
    if ~strcmp(state, cur_state)
        set_param(model,'SimMechanicsOpenEditorOnUpdate', state);
        save_system(model);
    end
end