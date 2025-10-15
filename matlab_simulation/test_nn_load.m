function net = test_nn_load()
% test to run TF NNs in matlab
nn_name = 'test_controller_tf_2_10'; % 'test_tf_10'
modelFolder = strcat('ML_control', filesep, 'nn_models', filesep,...
    nn_name); %, filesep, 'test.h5');
% net = importTensorFlowNetwork(modelFolder);  % originally this line worked well
net = importNetworkFromTensorFlow(modelFolder);  % not campatible with TF
% version higher than 2.10 currently (25.07.2024). But minimal available TF
% version is 2.12
% net = importNetworkFromONNX(modelFolder);

% net = importKerasNetwork(modelFolder);
outputFolder = fullfile(pwd, modelFolder);
outputFile = fullfile(outputFolder, "net.mat");
%test_vec = ones(1, 28*28);
addpath(outputFolder)  % needed for the predict block to work correctly

save(outputFile, "net");

% other possible option are custom level 2 s function from matlab code
% or following ideas. but non of them worked well
% gensim(net)
% my_nn = @(data) classify(net, data);
% genFunction(my_nn,'my_nn_func');
end