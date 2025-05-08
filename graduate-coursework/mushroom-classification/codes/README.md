# Mushroom Image Classification

This folder contains MATLAB scripts used for image classification of mushrooms using a custom convolutional neural network (CNN) and transfer learning with ResNet-18. 

## Project Overview

This work was part of the NUCL 575 graduate course and focused on comparing the performance of a custom CNN and a ResNet-18 model when trained on a dataset of four mushroom genera: **Amanita**, **Boletus**, **Cantharellus**, and **Morchella**.

## File Index

| File Name                             | Description                                  |
| ------------------------------------- | -------------------------------------------- |
| `mushroom_classification.m`           | First version of custom CNN                  |
| `mushroom_classification2.m`          | Iteration with improved layer tuning         |
| `mushroom_classification3.m`          | Final CNN version before switching to ResNet |
| `mushroom_classification_resnet_10.m` | ResNet model, 10 epochs                      |
| `mushroom_classification_resnet_15.m` | ResNet model, 15 epochs                      |
| `mushroom_classification_resnet_20.m` | ResNet model, 20 epochs                      |


## File Descriptions

### Custom CNN Architecture
- `mushroom_classification.m`  
  Initial version of custom CNN using MATLAB’s Deep Learning Toolbox.
  
- `mushroom_classification2.m`  
  Iterative improvement with additional layers or parameter tuning.
  
- `mushroom_classification3.m`  
  Final custom CNN version before transitioning to ResNet.

### ResNet-18 Transfer Learning
- `mushroom_classification_resnet_10.m`  
  ResNet-18 trained for 10 epochs – reached 100% validation accuracy.
  
- `mushroom_classification_resnet_15.m`  
  Trained for 15 epochs – accuracy remained 100%, validating model stability.
  
- `mushroom_classification_resnet_20.m`  
  Trained for 20 epochs – no further improvement over 10 epochs.

## Sample Architecture Snippet (Custom CNN)

```matlab
numClasses = 4;
newLayers = [
    fullyConnectedLayer(numClasses, 'Name', 'new_fc', 'WeightLearnRateFactor', 10, 'BiasLearnRateFactor', 10)
    softmaxLayer('Name', 'new_softmax')
    classificationLayer('Name', 'new_classoutput')];


lgraph = addLayers(lgraph, newLayers);
lgraph = connectLayers(lgraph, 'pool5', 'new_fc');

Example Training Output (10 Epochs – ResNet-18)
Validation Accuracy: 100%
Training Loss: Rapid convergence after epoch 3
Confusion Matrix:
|                        | Pred: Amanita | Pred: Boletus | Pred: Cantharellus | Pred: Morchella |
| ---------------------- | ------------- | ------------- | ------------------ | --------------- |
| **True: Amanita**      | ✅ 20          | 0             | 0                  | 0               |
| **True: Boletus**      | 0             | ✅ 20          | 0                  | 0               |
| **True: Cantharellus** | 0             | 0             | ✅ 20               | 0               |
| **True: Morchella**    | 0             | 0             | 0                  | ✅ 20            |

How to Run (ResNet Model)
Open any of the ResNet scripts (e.g., mushroom_classification_resnet_10.m) in MATLAB.

Make sure the dataset path is correct:
imds = imageDatastore('data/', ...
    'IncludeSubfolders',true, ...
    'LabelSource','foldernames');
run('mushroom_classification_resnet_10.m')

Performance Summary
| Model      | Epochs | Accuracy |
| ---------- | ------ | -------- |
| Custom CNN | 10     | \~94.8%  |
| ResNet-18  | 10     | **100%** |
| ResNet-18  | 15     | 100%     |
| ResNet-18  | 20     | 100%     |


## Notes on Results
- **ResNet-18** outperformed the custom CNN significantly in accuracy and convergence.
- Best result: **100% accuracy** after just 10 epochs using ResNet-18.
- Scripts are organized for reproducibility and comparison of training behavior.

Future Improvements
- Incorporate visually similar mushroom species to test model generalization
- Expand to mobile/web deployment
- Use real-world noisy image data

## Tools & Libraries
- MATLAB R2024b+
- Deep Learning Toolbox
- `imageDatastore`, `trainNetwork`, `analyzeNetwork`, `resnet18`

