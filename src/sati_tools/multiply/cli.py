import logging
from pathlib import Path

import ants
from ..utils import multiply_images

def add_arguments(parser):
    parser.add_argument("--image1", dest="image1_path", required=True,
                        help="Path to the first registered image (.nii.gz)")
    parser.add_argument("--image2", dest="image2_path", required=True,
                        help="Path to the second registered image (.nii.gz)")
    parser.add_argument("-o", "--output", dest="output_path", default="output/product.nii.gz",
                        help="Output path for the product image")

def run(args):
    log = logging.getLogger(__name__)
    log.info("Multiplying images...")
    product = multiply_images(args.image1_path, args.image2_path)
    Path(args.output_path).parent.mkdir(parents=True, exist_ok=True)
    ants.image_write(product, args.output_path)
    log.info("Wrote %s", args.output_path)
