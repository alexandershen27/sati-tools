import argparse
import logging

from .preprocess import cli as preprocess_cli
from .multiply import cli as multiply_cli


def main():

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-q", "--quiet", action="store_true",
                        help="Only log warnings and errors")

    parser = argparse.ArgumentParser(prog="sati", description="Sati Lab imaging tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pre = sub.add_parser("preprocess", parents=[common],
                           help="Register raw images to ACPC and zero threshold")
    preprocess_cli.add_arguments(p_pre)
    p_pre.set_defaults(func=preprocess_cli.run)

    p_mul = sub.add_parser("multiply", parents=[common],
                           help="Voxel-wise multiply two registered images")
    multiply_cli.add_arguments(p_mul)
    p_mul.set_defaults(func=multiply_cli.run)

    args = parser.parse_args()

    args.log_level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(level=args.log_level)
    logging.getLogger("dicom2nifti").setLevel(logging.WARNING)

    args.func(args)


if __name__ == "__main__":
    main()
