# Reliability-aware Normative Graph Modeling for Individualized ${}^{18}$F-FDG PET Deviation Fingerprinting Across Brain and Total-body Imaging

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Chenyixin/TotalBody-18F-FDG-Connectomics)

Companion resources for an individualized metabolic deviation fingerprinting framework for brain and total-body ${}^{18}$F-FDG PET.

## Overview

The framework characterizes how an individual subject's inter-regional metabolic relationships deviate from a cognitively normal reference. It consists of four main steps:

1. Adjust regional PET uptake values for demographic covariates.
2. Estimate a Reference Metabolic Graph (RMG) from cognitively normal training subjects.
3. Derive an Individual Metabolic Deviation (IMD) matrix using standardized bidirectional prediction residuals.
4. Aggregate edge-wise deviations into reliability-weighted within- and between-subnetwork fingerprints.

## Evaluation settings

The associated study evaluates the framework in two complementary settings:

- ADNI brain ${}^{18}$F-FDG PET: CN-versus-AD diagnostic classification and sMCI-versus-pMCI progression classification.
- Private total-body ${}^{18}$F-FDG PET: within-AD prediction of spatial disorientation, emotional changes, language decline, and motor impairment.

The total-body analysis uses 202 anatomical regions, comprising 83 cerebral and 119 extracranial regions. Cognitively normal controls are used to estimate the normative reference; symptom prediction is performed within the AD group.

## Interpretable fingerprint features

The IMD matrix is summarized using three feature families:

- Within-subnetwork deviation magnitude ($\Delta^w$).
- Within-subnetwork deviation heterogeneity ($\Sigma^w$).
- Between-subnetwork deviation magnitude ($\Gamma^w$).

These features retain explicit subnetwork definitions while reducing the dimensionality of the edge-wise deviation matrix.

## Repository scope

The current public repository provides sample data, ROI-level preprocessing utilities, anomaly-visualization code, and an interactive demonstration. The included notebook should not be interpreted as an end-to-end reproduction package for every cross-validation experiment reported in the manuscript.

Interactive demonstration:  
https://huggingface.co/spaces/Chenyixin/TotalBody-18F-FDG-Connectomics

## Data availability

ADNI data are available through the ADNI data-access platform. The private total-body PET cohort is not publicly distributed because of patient privacy and ethical restrictions. Access may be considered through the corresponding authors, subject to reasonable request and approval by the relevant ethics committee.

---

## 💻 System Requirements

### Hardware Requirements
- **CPU:** Standard computer with sufficient RAM (16GB+ recommended).
- **GPU:** NVIDIA GPU with **>12GB VRAM** (Required for the MPUM segmentation step).

### Software Requirements
**OS:**
- Linux (Tested on Ubuntu 20.04, Rocky Linux)

**Python Dependencies:**
```txt
numpy
tqdm
monai==1.2.0
SimpleITK==2.2.1
sklearn
scipy
```
