# Mushroom Image Classification

This folder contains MATLAB scripts used for image classification of mushrooms using a custom convolutional neural network (CNN) and transfer learning with ResNet-18. 

## Project Overview

This work was part of the NUCL 575 graduate course and focused on comparing the performance of a custom CNN and a ResNet-18 model when trained on a dataset of four mushroom genera: **Amanita**, **Boletus**, **Cantharellus**, and **Morchella**.

## File Descriptions

### ResNet-18 Transfer Learning
- `mushroom_classification_resnet_10.m`  
  ResNet-18 trained for 10 epochs – reached 100% validation accuracy.
  
- `mushroom_classification_resnet_15.m`  
  Trained for 15 epochs – accuracy remained 100%, validating model stability.
  
- `mushroom_classification_resnet_20.m`  
  Trained for 20 epochs – no further improvement over 10 epochs.

### Custom CNN Architecture
- `mushroom_classification.m`  
  Initial version of custom CNN using MATLAB’s Deep Learning Toolbox.
  
- `mushroom_classification2.m`  
  Iterative improvement with additional layers or parameter tuning.
  
- `mushroom_classification3.m`  
  Final custom CNN version before transitioning to ResNet.

## Tools & Libraries
- MATLAB R2024b+
- Deep Learning Toolbox
- `imageDatastore`, `trainNetwork`, `analyzeNetwork`, `resnet18`

## Notes on Results
- **ResNet-18** outperformed the custom CNN significantly in accuracy and convergence.
- Best result: **100% accuracy** after just 10 epochs using ResNet-18.
- Scripts are organized for reproducibility and comparison of training behavior.

