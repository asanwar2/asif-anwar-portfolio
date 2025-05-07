trainFolder = 'C:\Users\asanw\Downloads\archive\dataset_augmented_vgg\train';
testFolder = 'C:\Users\asanw\Downloads\archive\dataset_augmented_vgg\test';


% Create image datastores for training and testing
imdsTrain = imageDatastore(trainFolder, 'IncludeSubfolders', true, 'LabelSource', 'foldernames');
imdsTest = imageDatastore(testFolder, 'IncludeSubfolders', true, 'LabelSource', 'foldernames');
[imdsTrain, imdsValidate] = splitEachLabel(imdsTrain, 0.85, 'randomized');


inputSize = [224 224]; % Image size

% Apply data augmentation only on the training data
augTrain = augmentedImageDatastore(inputSize, imdsTrain, ...
    'DataAugmentation', imageDataAugmenter( ...
        'RandRotation', [-10,10], ...
        'RandXTranslation', [-5 5], ...
        'RandYTranslation', [-5 5], ...
        'RandXScale', [0.9 1.1], ...
        'RandYScale', [0.9 1.1]));



augTest = augmentedImageDatastore(inputSize, imdsTest);

if exist('imdsValidate', 'var')
    augValidate = augmentedImageDatastore(inputSize, imdsValidate);
end

% Load ResNet-18 and Convert to Layer Graph
net = resnet18;
lgraph = layerGraph(net); % Convert to layer graph for modification

% Modify the Network
% Update these layer names based on the output of net.Layers
lgraph = removeLayers(lgraph, {'fc1000', 'prob', 'ClassificationLayer_predictions'});

% Add new layers for your 4-class problem
numClasses = 4;
newLayers = [
    fullyConnectedLayer(numClasses, 'Name', 'new_fc', 'WeightLearnRateFactor', 10, 'BiasLearnRateFactor', 10)
    softmaxLayer('Name', 'new_softmax')
    classificationLayer('Name', 'new_classoutput')];

% Connect the new layers to the layer graph
lgraph = addLayers(lgraph, newLayers);
lgraph = connectLayers(lgraph, 'pool5', 'new_fc'); % Adjust if necessary based on your layer inspection

% Training options and training code as before
%options = trainingOptions('adam', ...
%    'InitialLearnRate', 1e-4, ...
%    'MaxEpochs', 20, ...
%    'MiniBatchSize', 32, ...
%    'Shuffle', 'every-epoch', ...
%    'ValidationData', augTest, ...
%    'ValidationFrequency', 5, ...
%    'Verbose', true, ...
%    'Plots', 'training-progress');

options = trainingOptions('adam', ...
    'InitialLearnRate', 1e-4, ...         % Starting learning rate
    'LearnRateSchedule', 'piecewise', ... % Use a piecewise learning rate schedule
    'LearnRateDropFactor', 0.5, ...       % Factor to reduce learning rate by (e.g., halves it)
    'LearnRateDropPeriod', 5, ...         % Period (in epochs) after which to reduce the learning rate
    'MaxEpochs', 20, ...                  % Set max epochs based on your needs
    'MiniBatchSize', 32, ...              % Batch size for training
    'Shuffle', 'every-epoch', ...         % Shuffle the data each epoch
    'ValidationData', augTest, ...        % Validation data
    'ValidationFrequency', 5, ...         % Frequency of validation checks
    'Verbose', true, ...
    'Plots', 'training-progress');        % Show training progress plot


% Train the modified network
net = trainNetwork(augTrain, lgraph, options);


% Classify Test Set and Calculate Accuracy
[predictedLabels, scores] = classify(net, augTest);
trueLabels = imdsTest.Labels;

% Calculate test accuracy
accuracy = mean(predictedLabels == trueLabels);
fprintf('Test Accuracy: %.2f%%\n', accuracy * 100);

% Plot Confusion Matrix
plotconfusion(trueLabels, predictedLabels);