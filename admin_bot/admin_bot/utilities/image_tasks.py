from PIL import Image
from utilities.image_utils import register_image_task, register_chat_image_task
import numpy


# You can add new image tasks here

image_tasks = {
    "indah": {
        "image": "admin_bot/resources/indah_sad.png",
        "type": "overlay",
        "corners": [
            (67, 446),
            (406, 290),
            (513, 557),
            (195, 736),
        ],
    },
    "vote": {
        "image": "admin_bot/resources/vote.png",
        "type": "background",
        "corners": [
            (40, 240),
            (415, 240),
            (415, 490),
            (40, 490),
        ],
    },
    "whiteboard": {
        "image": "admin_bot/resources/look_at_this/foreground.png",
        "type": "overlay",
        "corners": [
            (1500, 75),
            (2500, 75),
            (2500, 2075),
            (1500, 2075),
        ],
    },
}

for name, task in image_tasks.items():

    def image_task(input_image: Image.Image, task=task):
        template = Image.open(task["image"]).convert("RGBA")
        transformed_image = four_corners(input_image, task["corners"])
        result_image = Image.new(
            "RGBA", template.size, (0, 0, 0, 0)
        )  # Fully transparent
        if task["type"] == "overlay":  # put the input_image on bottom
            result_image.paste(transformed_image, (0, 0), transformed_image)
            result_image.paste(template, (0, 0), template)
        else:  # "background" put the input_image on top # also fallback
            result_image.paste(template, (0, 0), template)
            result_image.paste(transformed_image, (0, 0), transformed_image)
        return result_image

    register_image_task(name)(image_task)


def find_coeffs(pa, pb):  # source: stack overflow
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

    A = numpy.matrix(matrix, dtype=float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)


def four_corners(image: Image.Image, output_corners):
    """Transform an image by its corners

    input_image: Image.Image -- Image that will be transformed
    output_corners           -- Where the four corners of the input will go
                                Array of Tuples (x, y). Top left corner first then clockwise
    """

    # input rectangular image corners
    input_corners = [(0, 0), (image.width, 0), image.size, (0, image.height)]

    coeffs = find_coeffs(output_corners, input_corners)  # calculate transformation

    size = tuple(map(max, zip(*output_corners)))  # find max size of image

    # apply transformation
    transformed_image = image.convert("RGBA").transform(
        size, Image.PERSPECTIVE, coeffs, Image.BICUBIC
    )

    return transformed_image


# Extra image tasks. You can still make more commands if
# you want to do something other than four corners transform


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


@register_image_task("pin")
def pin_task(input_image: Image.Image) -> Image.Image:
    """
    Create a pin template
    """

    template = Image.open("admin_bot/resources/pintemplate.png").convert("RGBA")

    dpi = 300

    pins = [
        (0.621, 0.370),
        (3.621, 0.370),
        (2.131, 2.873),
        (5.131, 2.873),
        (0.621, 5.377),
        (3.621, 5.377),
        (2.131, 7.880),
        (5.131, 7.880),
    ]
    pin_size = int(2.75 * dpi)  # 300 dpi
    pin_mask = Image.open("admin_bot/resources/pinmask.png").convert("RGBA")

    pin_image = Image.new("RGBA", (pin_size, pin_size), (0, 0, 0, 0))
    w, h = input_image.size
    if w > h:
        pin_image.paste(
            input_image.resize((pin_size, round(h / w * pin_size))),
            (0, round((pin_size - (h / w * pin_size)) / 2)),
        )
    else:
        pin_image.paste(
            input_image.resize((round(w / h * pin_size), pin_size)),
            (round((pin_size - (w / h * pin_size)) / 2), 0),
        )

    result_image = Image.new("RGB", template.size, (255, 255, 255))

    for pin in pins:
        result_image.paste(
            pin_image, tuple(map(lambda x: round(x * dpi), pin)), pin_mask
        )

    result_image.paste(template, (0, 0), template)
    return result_image


# You can only have 5 context menu commands.
# Use @register_chat_image_task to register an
# image command as a regular slash command


@register_chat_image_task("live")
def live_task(input_image: Image.Image) -> Image.Image:
    template = Image.open("admin_bot/resources/reaction.png").convert("RGBA")
    template.paste(input_image.resize((660, 378)), (10, 113))
    template.paste(input_image.resize((223, 84)), (140, 16))
    return template
