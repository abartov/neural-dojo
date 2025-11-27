# Module 29 Examples: Convolutional Neural Networks (CNNs)

This directory contains working code examples for Module 29 - Convolutional Neural Networks.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Convolution Visualizer
**File**: `example_01_convolution_visualizer.py`
**Description**: Visualize how convolution kernels process images - see edge detection, blur, and sharpen in action.
**Run**: `python example_01_convolution_visualizer.py`

### Example 2: Build a CNN from Scratch
**File**: `example_02_custom_cnn.py`
**Description**: Build and train a custom CNN architecture on CIFAR-10.
**Run**: `python example_02_custom_cnn.py`

### Example 3: Transfer Learning
**File**: `example_03_transfer_learning.py`
**Description**: Use pretrained ResNet for your own classification task with minimal data.
**Run**: `python example_03_transfer_learning.py`

### Example 4: Feature Visualization
**File**: `example_04_feature_visualization.py`
**Description**: Visualize what CNN layers learn - from edges to textures to objects.
**Run**: `python example_04_feature_visualization.py`

## Deliverable

### CNN Vision Toolkit
**File**: `deliverable_cnn_vision_toolkit.py`
**Description**: A comprehensive toolkit for building, training, and analyzing CNNs.
**Documentation**: See `DELIVERABLE_README.md`

```bash
python deliverable_cnn_vision_toolkit.py demo1  # Train custom CNN on CIFAR-10
python deliverable_cnn_vision_toolkit.py demo2  # Transfer learning comparison
python deliverable_cnn_vision_toolkit.py demo3  # Architecture analysis
python deliverable_cnn_vision_toolkit.py demo4  # Generate CNN report
```

## Expected Output

### Training Results
- Custom CNN on CIFAR-10: ~85% accuracy
- Transfer learning (ResNet-18): ~92% accuracy
- Training time: 5-15 minutes (GPU recommended)

### Architecture Analysis
- Parameter counts for various architectures
- Memory requirements
- FLOPs comparison

## Notes

- GPU is recommended but not required (CPU training is slower)
- CIFAR-10 dataset will be downloaded automatically (~170MB)
- First run may take longer due to model/dataset downloads

## Related Module

See `docs/curriculum/notes/module_29_cnns.md` for the full theory.
