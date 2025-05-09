# Mushroom Image Classification Using Neural Networks

This project was completed as the final assignment for NUCL 575. It explores the application of convolutional neural networks (CNNs) and transfer learning for image classification of mushroom genera. This project deepened my understanding of how machine learning tools can be applied to solve classification problems, even outside traditional nuclear engineering applications.


## Objective
To develop and compare multiple neural network architectures for classifying mushroom images using a dataset of four distinct genera: Amanita, Boletus, Cantharellus, and Morchella.

## Methods
- **Custom CNN** built in MATLAB using ReLU, max-pooling, and fully connected layers
- **Transfer learning with ResNet-18**, modified for the classification task
- **Sequential model in Python** using Keras for cross-toolset experimentation

## Contents
- codes:
- `NUCL575-mushroom-classification.pdf`: Final report with methodology, results, and discussion

# Mushroom Image Classification

This folder contains MATLAB scripts used for image classification of mushrooms using a custom convolutional neural network (CNN) and transfer learning with ResNet-18. 

## Project Overview

This work was part of the NUCL 575 graduate course and focused on comparing the performance of a custom CNN and a ResNet-18 model when trained on a dataset of four mushroom genera: **Amanita**, **Boletus**, **Cantharellus**, and **Morchella**.

## Dataset Structure

Download the dataset (from Kaggle): https://www.kaggle.com/datasets/viktormodroczky/mushroom-dataset-4-classes

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

```

## Example Training Output (10 Epochs – ResNet-18)
Confusion Matrix:
|                        | Pred: Amanita | Pred: Boletus | Pred: Cantharellus | Pred: Morchella |
| ---------------------- | ------------- | ------------- | ------------------ | --------------- |
| **True: Amanita**      | ✅ 20          | 0             | 0                  | 0               |
| **True: Boletus**      | 0             | ✅ 20          | 0                  | 0               |
| **True: Cantharellus** | 0             | 0             | ✅ 20               | 0               |
| **True: Morchella**    | 0             | 0             | 0                  | ✅ 20            |

- Validation Accuracy: 100%
- Training Loss: Rapid convergence after epoch 3

## How to Run (ResNet Model)
Open any of the ResNet scripts (e.g., mushroom_classification_resnet_10.m) in MATLAB.

Make sure the dataset path is correct:
```
imds = imageDatastore('data/', ...
    'IncludeSubfolders',true, ...
    'LabelSource','foldernames');
run('mushroom_classification_resnet_10.m')
```
MATLAB will:
- Load pre-trained ResNet-18
- Replace the final layer with 4 output classes
- Train on your dataset for 10 epochs

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

## Tools & Libraries
- MATLAB R2024b+
- Deep Learning Toolbox
- `imageDatastore`, `trainNetwork`, `analyzeNetwork`, `resnet18`

## Why It Matters
This project showcases a full model development pipeline, blending computer vision and deep learning in a nuclear engineering course. The structure, metrics, and reproducibility make it ready for real-world applications and portfolio presentation.

## Results
- ResNet-18 model achieved 100% validation accuracy in 10 epochs
- Custom CNN achieved ~94% accuracy
- Python model achieved ~93.8% accuracy
- Results suggest that transfer learning can significantly outperform traditional CNNs with limited data

## Future Work
- Add more visually similar species to improve generalization
- Use augmented datasets to improve robustness
- Deploy model in a user-friendly application or mobile tool

