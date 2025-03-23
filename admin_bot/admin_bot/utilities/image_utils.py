import io
import logging

from PIL import Image, UnidentifiedImageError
from typing import Callable, Dict

# Registry for image manipulation tasks
IMAGE_TASKS: Dict[str, Callable[[Image.Image], Image.Image]] = {}

# Registry for chat command image manipulation tasks
CHAT_IMAGE_TASKS: Dict[str, Callable[[Image.Image], Image.Image]] = {}


def register_image_task(name: str):
    """
    Decorator to register an image task.

    :param name: The name of the task.
    """

    def decorator(func: Callable[[Image.Image], Image.Image]):
        IMAGE_TASKS[name] = func
        return func

    return decorator


def register_chat_image_task(name: str):
    """
    Decorator to register an image task.

    :param name: The name of the task.
    """

    def decorator(func: Callable[[Image.Image], Image.Image]):
        CHAT_IMAGE_TASKS[name] = func
        return func

    return decorator


def apply_image_task(image: Image.Image, task_name: str) -> Image.Image:
    """
    Apply a registered image task to the given image.

    :param image: The input image.
    :param task_name: The task to apply.
    :return: The resulting image.
    """
    if task_name in IMAGE_TASKS:
        return IMAGE_TASKS[task_name](image)

    if task_name in CHAT_IMAGE_TASKS:
        return CHAT_IMAGE_TASKS[task_name](image)

    raise ValueError(f"Task '{task_name}' is not registered.")


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load an PIL image from bytes.

    :param image_bytes: The image data in bytes.
    :return: A PIL Image.
    """
    try:
        return Image.open(io.BytesIO(image_bytes))
    except UnidentifiedImageError as e:
        logging.error(f"Failed to load image: {e}")
        raise


def save_image_to_bytes(image: Image.Image) -> bytes:
    """
    Save a PIL Image to bytes.

    :param image: The PIL Image.
    :return: Image data as bytes.
    """
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()
