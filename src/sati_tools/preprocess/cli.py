import logging
from pathlib import Path

import numpy as np
import ants

from ..io import get_image, get_template, convert_nifti_datatype
from ..registration import two_step_alignment
from ..utils import zero_threshold


def add_arguments(parser):
    sources = parser.add_argument_group("Image paths, .nii.gz or .zip")
    sources.add_argument("--t1", dest="t1_path", help="Path to raw T1 image")
    sources.add_argument("--t2star", dest="t2star_path", help="Path to raw T2* image")
    sources.add_argument("--flair", dest="flair_path", help="Path to raw FLAIR image")

    config = parser.add_argument_group("Optional configuration")
    config.add_argument("-o", "--output-dir", default="output", help="Directory for outputs")


def run(args):
    log = logging.getLogger(__name__)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    t2star_clean = None

    if args.t2star_path:
        log.info("Processing T2* image...")
        t2star_raw = get_image(args.t2star_path)
        template = get_template("T2w")
        template_up = ants.resample_image(template, tuple(t2star_raw.spacing), use_voxels=False, interp_type=3)
        t2star_acpc = two_step_alignment(moving_image=t2star_raw, fixed_image=template_up)

        t2star_clean = zero_threshold(t2star_acpc)
        convert_nifti_datatype(t2star_clean, np.uint32, output_path=str(out_dir / "t2star_acpc.nii.gz"))

    if args.flair_path:
        log.info("Processing FLAIR image...")
        flair_raw = get_image(args.flair_path)

        if t2star_clean is not None:
            fixed = t2star_clean
        else:
            log.warning("No T2* provided; FLAIR will be aligned to the T2w template instead of T2*.")
            fixed = get_template("T2w")

        flair_acpc = two_step_alignment(moving_image=flair_raw, fixed_image=fixed)
        flair_clean = zero_threshold(flair_acpc)
        convert_nifti_datatype(flair_clean, np.uint32, output_path=str(out_dir / "flair_acpc.nii.gz"))

    if args.t1_path:
        log.info("Processing T1 image...")
        t1_raw = get_image(args.t1_path)
        template = get_template("T1w")
        t1_acpc = two_step_alignment(moving_image=t1_raw, fixed_image=template)

        if t2star_clean is not None:
            t1_acpc = ants.resample_image(t1_acpc, tuple(t2star_clean.spacing), use_voxels=False, interp_type=3)
        else:
            log.warning("No T2* provided; T1 will not be upsampled to T2* spacing.")

        t1_clean = zero_threshold(t1_acpc)
        convert_nifti_datatype(t1_clean, np.uint16, output_path=str(out_dir / "t1_acpc.nii.gz"))
