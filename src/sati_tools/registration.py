import os
import tempfile
import ants
import numpy as np

def two_step_alignment(moving_image, fixed_image):
    # ANTs writes its transforms (and our rigid .mat) to temp files; track them so
    # we can clean them all up regardless of how this function exits.
    temp_files = set()

    try:
        # Step A: 12-DOF affine
        reg = ants.registration(
            fixed=fixed_image,
            moving=moving_image,
            type_of_transform="antsRegistrationSyNQuick[a]",
        )
        temp_files.update(reg.get("fwdtransforms", []))
        temp_files.update(reg.get("invtransforms", []))

        affine_tx_path = reg["fwdtransforms"][0]
        affine_tx = ants.read_transform(affine_tx_path)

        # Step B: pull rigid component out of the affine via SVD
        params = np.asarray(affine_tx.parameters)
        matrix_part = params[:9].reshape((3, 3))
        translation_part = params[9:]

        u, _s, vh = np.linalg.svd(matrix_part)
        rigid_matrix = u @ vh
        if np.linalg.det(rigid_matrix) < 0:
            # flip the last column of U so we end up with a proper rotation (det = +1)
            u[:, -1] *= -1
            rigid_matrix = u @ vh

        # Rebuild as an ANTs AffineTransform with the rigid matrix + original translation
        rigid_params = np.concatenate([rigid_matrix.flatten(), translation_part])
        rigid_tx = ants.create_ants_transform(
            transform_type="AffineTransform",
            dimension=3,
            precision="float",
            parameters=rigid_params,
            fixed_parameters=np.asarray(affine_tx.fixed_parameters),
        )

        fd, rigid_tx_path = tempfile.mkstemp(suffix=".mat")
        os.close(fd)
        temp_files.add(rigid_tx_path)
        ants.write_transform(rigid_tx, rigid_tx_path)

        # Step C: apply rigid transform with sinc interpolation
        aligned = ants.apply_transforms(
            fixed=fixed_image,
            moving=moving_image,
            transformlist=[rigid_tx_path],
            interpolator="hammingWindowedSinc",
        )
        return aligned

    finally:
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)