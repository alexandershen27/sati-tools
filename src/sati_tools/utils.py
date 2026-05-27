
import numpy as np
import ants

from .io import get_image

def zero_threshold(image_or_path, output_path=None):
    if isinstance(image_or_path, str):
        img = ants.image_read(image_or_path)
        target = output_path or image_or_path
    else:
        img = image_or_path
        target = output_path

    arr = img.numpy()
    arr[arr < 0] = 0
    cleaned = ants.from_numpy(
        arr.astype(np.float32),
        origin=img.origin,
        spacing=img.spacing,
        direction=img.direction,
    )
    if target is not None:
        ants.image_write(cleaned, target)
    return cleaned

def multiply_images(path1, path2):
    image1 = get_image(path1)
    image2 = get_image(path2)
    if image1.shape != image2.shape or image1.spacing != image2.spacing:
        raise ValueError("Images are not on the same grid; register them first.")
    return image1 * image2