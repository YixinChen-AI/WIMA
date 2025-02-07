# Whole-Body Inter-Organ Metabolic Atlas for PET/CT Anomaly Detection

Medical anomaly detection (MAD) in PET/CT is critical for diagnosing and planning treatments for a broad range of systemic diseases. However, existing deep learning–based MAD approaches often encounter high noise in PET scans and struggle to learn normal representations in the presence of anomalies, resulting in overfitting and diminished detection accuracy. To address these challenges, we propose a novel method that integrates multi-organ metabolic analysis into MAD by constructing a Whole-body Inter-Organ Metabolic Atlas (WIMA). Developed using linear regression and deep-learning-based pre-segmentation, WIMA captures thousands of inter-organ metabolic associations under normal conditions. Unlike traditional ``black box" deep learning methods, this atlas provides transparent, interpretable explanations for anomaly classification. We evaluate WIMA on cancer (lymphoma, melanoma, and lung cancer), epilepsy, and Alzheimer’s disease (AD), demonstrating superior anomaly detection performance and revealing distinct metabolic signatures across diverse pathologies.

## Features

- **Feature 1**: A novel Whole-body Inter-Organ Metabolic Atlas (WIMA) is proposed for anomaly detection in whole-body 18F-FDG PET/CT scans. It integrates an atlas of inter-organ metabolic associations and unbiased linear regression techniques to identify pathological deviations effectively.
- **Feature 2**: WIMA outperforms advanced anomaly detection methods such as AE, VAE, MemAE, and GANomaly. It achieves higher accuracy with significantly reduced computational resources, as demonstrated by AUC and AP metrics in different datasets.
- **Feature 3**: It provides valuable insights into disease pathology. For example, WIMA highlights the thymus as a key organ in lymphoma and reveals the involvement of ribs and vertebrae in lung cancer. It also detects metabolic anomalies associated with epilepsy, offering evidence of aberrant brain metabolism. Moreover, WIMA differentiates distinct metabolic patterns in Alzheimer’s Disease (AD) and Mild Cognitive Impairment (MCI), aiding both diagnosis and the assessment of disease progression.

# System Requirements
## Hardware requirements
`MPUM` package requires only a standard computer with enough RAM and a NVIDIA GPU with more than 12G momery.

## Software requirements
### OS Requirements
This package is supported for *Linux*. The package has been tested on the following systems:
+ Linux: Ubuntu 20.04, Rocky Linux

### Python Dependencies
`MPUM` mainly depends on the Python scientific stack.
```
numpy
tqdm
monai==1.2.0
SimpleITK==2.2.1
```
