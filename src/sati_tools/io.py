import os
from pathlib import Path
import zipfile
import tempfile

import numpy as np
import nibabel as nib
import ants
import dicom2nifti
from templateflow import api as tflow

def _unzip_dicom(dicom_path):
    with tempfile.TemporaryDirectory() as scratch:
        with zipfile.ZipFile(dicom_path, "r") as zip_ref:
            zip_ref.extractall(scratch)
        out_path = str(Path(scratch) / "converted.nii.gz")
        dicom2nifti.dicom_series_to_nifti(scratch, out_path, reorient_nifti=True)
        return ants.image_read(out_path)

def get_image(image_path: str):
    name = Path(image_path).name.lower()
    if name.endswith(".nii") or name.endswith(".nii.gz"):
        return ants.image_read(image_path)
    if name.endswith(".zip"):
        return _unzip_dicom(image_path)
    raise ValueError(f"Unsupported file type: {image_path}")

def get_template(suffix: str):
    # Template fetched from TeplateFlow
    # See also MNI152NLin6Asym or MNI152NLin6Sym

    path = str(tflow.get(       # type: ignore[operator] 
        "MNI152NLin2009cAsym",
        resolution=1,
        suffix=suffix,
        desc=None,
        extension=".nii.gz",
    ))
    
    return ants.image_read(path)

def convert_nifti_datatype(image, dtype, output_path):
    fd, tmp_path = tempfile.mkstemp(suffix=".nii.gz")
    os.close(fd)
    try:
        ants.image_write(image, tmp_path)
        nii = nib.Nifti1Image.from_filename(tmp_path)
        data = np.asarray(nii.get_fdata()).astype(dtype)
        out = nib.Nifti1Image(data, nii.affine, nii.header)
        out.set_data_dtype(dtype)
        nib.save(out, output_path)
    finally:
        os.remove(tmp_path)
    return output_path