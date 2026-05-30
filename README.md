# Sati Lab imaging tools

## Usage

### Preprocessing

Accepts DICOM zip or NIFTI paths. Each input is optional, however:
  - FLAIR is registered to T2*, will register to T2 MNI template if missing
  - T1 is upscaled to T2* resolution, will skip final upscale if missing

You can safely run with only T2* and FLAIR if T1 is not needed. It is not recommended to process T1 or FLAIR without registering T2* simultaneously.

```bash
sati preprocess --t1 path/to/t1 \
                --t2star path/to/t2 \
                --flair path/to/flair
```

Optional flags: `--quiet`, `--output-dir (default output/)`

### Multiply

Multiply (eg. FLAIR*) checks for alignment, then multiplies:

```bash
sati multiply --image1 path/to/image1 \
              --image2 path/to/image2
```

Optional flags: `--output (default output/product.nii.gz)`

## Install

Note: python version must be >=3.9 and <3.13
```bash
git clone https://github.com/alexandershen27/sati-tools.git
cd sati-tools
conda create -n sati-tools python=3.12
conda activate sati-tools
pip install -e .
```

## Implementation

Preprocessing based on CAVS preprocessing steps:
  - Calculated as 12-DOF transformation, stripped down to 6-DOF transformation
  - T1 registered to MNI T1 template, then upscaled to T2* spacing
  - MNI T2 template is first upscaled to T2* spacing, then T2* is registered to upscaled MNI T2 template
  - FLAIR is registered to registered T2* output
  - Voxels are zero-thresholded