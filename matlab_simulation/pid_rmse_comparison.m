% DATA for plotting is available in Velocity RMSE data.txt at
% PID_comparison_plots folder
fontsize = 16;

figure;
set(gcf, 'Color', 'w');
set(gca, 'FontSize', fontsize);

plot(visual_velocities, conventional_visual_transition_rms_vector)
hold on
plot(visual_velocities, adaptive_visual_transition_rms_vector)

xlabel('Velocity reference (m/s)', 'FontSize', fontsize);
ylabel('Tracking RMSE (m/s)', 'FontSize', fontsize);
title('Transition PID comparison', 'FontSize', fontsize);
legend('PID', 'Adaptive PID', 'FontSize', fontsize);
grid on
hold off

figure;
set(gcf, 'Color', 'w');
set(gca, 'FontSize', fontsize);

plot(visual_velocities, conventional_visual_steady_rms_vector)
hold on
plot(visual_velocities, adaptive_visual_steady_rms_vector)

xlabel('Velocity reference (m/s)', 'FontSize', fontsize);
ylabel('Tracking RMSE (m/s)', 'FontSize', fontsize);
title('Steady PID comparison', 'FontSize', fontsize);
legend('PID', 'Adaptive PID', 'FontSize', fontsize);
grid on
hold off