from PIL import Image
from utilities.image_utils import register_image_task


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


@register_image_task("keegan")
def keegan_task(input_image: Image.Image) -> Image.Image:
    """
    Keegan transformations lol!
    """
    # Load the foreground overlay (ensure it has an alpha channel)
    foreground = Image.open(
        "admin_bot/resources/what_is_keegan_looking_at/fore.png"
    ).convert("RGBA")

    # Create a new blank RGBA image with the same size as the foreground
    result_image = Image.new("RGBA", foreground.size, (0, 0, 0, 0))  # Fully transparent

    # Resize image to fit screen
    resized_image = input_image.resize((1550, 900))

    # Rotate image counterclockwise by 38.2 degrees
    rotated_image = resized_image.rotate(38.2, expand=True)

    # Paste the rotated image onto the result image
    result_image.paste(rotated_image, (240, 780))

    # Place the foreground on top
    result_image.paste(foreground, (0, 0), foreground)

    return result_image


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
