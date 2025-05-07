% Define directories
%trainFolder = fullfile('C:\Users\asanw\Downloads\archive\dataset_augmented_vgg\train', 'train');
%testFolder = fullfile('C:\Users\asanw\Downloads\archive\dataset_augmented_vgg\test', 'test');

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

layers = [
    imageInputLayer([224 224 3]) % Input layer for 224x224 RGB images

    convolution2dLayer(3, 8, 'Padding', 'same')
    batchNormalizationLayer
    reluLayer
    maxPooling2dLayer(2, 'Stride', 2)

    convolution2dLayer(3, 16, 'Padding', 'same')
    batchNormalizationLayer
    reluLayer
    maxPooling2dLayer(2, 'Stride', 2)

    convolution2dLayer(3, 32, 'Padding', 'same')
    batchNormalizationLayer
    reluLayer
    maxPooling2dLayer(2, 'Stride', 2)

    fullyConnectedLayer(4) % 4 output classes (adjust based on your classes)
    softmaxLayer
    classificationLayer];

options = trainingOptions('adam', ...
    'InitialLearnRate', 1e-4, ...
    'MaxEpochs', 10, ...            % Start with 10 epochs; adjust based on performance
    'MiniBatchSize', 32, ...
    'Shuffle', 'every-epoch', ...
    'ValidationData', augTest, ...   % Use augTest as validation if you didn’t split a separate validation set
    'ValidationFrequency', 5, ...
    'Verbose', true, ...
    'Plots', 'training-progress');   % Shows a live plot of accuracy and loss during training

net = trainNetwork(augTrain, layers, options);

save('mushroomClassifier.mat', 'net');

% Classify Test Set and Calculate Accuracy
[predictedLabels, scores] = classify(net, augTest);
trueLabels = imdsTest.Labels;

% Calculate test accuracy
accuracy = mean(predictedLabels == trueLabels);
fprintf('Test Accuracy: %.2f%%\n', accuracy * 100);

% Plot Confusion Matrix
plotconfusion(trueLabels, predictedLabels);
