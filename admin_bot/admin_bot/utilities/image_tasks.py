from PIL import Image
from utilities.image_utils import register_image_task
import numpy


@register_image_task("myvote")
def myvote_task(input_image: Image.Image) -> Image.Image:
    frame = Image.open("admin_bot/resources/vote.png")
    input_image = input_image.resize((375, 250))
    frame.paste(input_image, (40, 240))
    return frame


@register_image_task("whiteboard")
def whiteboard_task(input_image: Image.Image) -> Image.Image:
    background = Image.open("admin_bot/resources/look_at_this/background.png")
    foreground = Image.open("admin_bot/resources/look_at_this/foreground.png")
    input_image = input_image.resize((1000, 2000))
    background.paste(input_image, (1500, 75))
    background.paste(foreground, (0, 0), foreground)
    return background


@register_image_task("dylan")
def dylan_task(input_image: Image.Image) -> Image.Image:
    """
    Dylan dosn't like what you put on his phone
    """

    # Load the foreground overlay (ensure it has an alpha channel)
    foreground = Image.open("admin_bot/resources/dylan_disappointed/fore.png").convert(
        "RGBA"
    )

    # Create a new blank RGBA image with the same size as the foreground
    result_image = Image.new("RGBA", foreground.size, (0, 0, 0, 0))  # Fully transparent

    # Resize image to fit screen
    resized_image = input_image.resize((500, 230))

    # Rotate image clockwise
    rotated_image = resized_image.rotate(-1.4, expand=True)

    # Paste the rotated image onto the result image
    result_image.paste(rotated_image, (65, 460))

    # Place the foreground on top
    result_image.paste(foreground, (0, 0), foreground)

    return result_image


@register_image_task("indah")
def indah_task(input_image: Image.Image) -> Image.Image:
    """
    You've upset Indah
    """

    # Load the foreground overlay (ensure it has an alpha channel)
    foreground = Image.open("admin_bot/resources/indah_sad.png").convert("RGBA")

    # Perspective Transform, transform based on moving the four corners
    input_corners = [  # input rectangular image corners
        (0, 0),
        (input_image.width, 0),
        (input_image.width, input_image.height),
        (0, input_image.height),
    ]
    output_corners = [  # four corners of the screen in foreground image
        (67, 446),
        (406, 290),
        (513, 557),
        (195, 736),
    ]

    coeffs = find_coeffs(output_corners, input_corners)  # calculate transformation

    transformed_image = input_image.transform(
        foreground.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC
    )  # apply transformation

    # Create a new blank RGBA image with the same size as the foreground
    result_image = Image.new("RGBA", foreground.size, (0, 0, 0, 0))  # Fully transparent
    result_image.paste(transformed_image, (0, 0))
    result_image.paste(foreground, (0, 0), foreground)

    return result_image


def find_coeffs(pa, pb):  # source: stack overflow
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

    A = numpy.matrix(matrix, dtype=float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)
