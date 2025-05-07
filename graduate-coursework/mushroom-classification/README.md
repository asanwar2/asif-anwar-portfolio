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

## 📈 Results
- ResNet-18 model achieved 100% validation accuracy in 10 epochs
- Custom CNN achieved ~94% accuracy
- Python model achieved ~93.8% accuracy
- Results suggest that transfer learning can significantly outperform traditional CNNs with limited data

## Future Work
- Add more visually similar species to improve generalization
- Use augmented datasets to improve robustness
- Deploy model in a user-friendly application or mobile tool

