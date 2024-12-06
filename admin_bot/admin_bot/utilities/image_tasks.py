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
    # Load the foreground overlay (with transparency)
    foreground = Image.open(
        "admin_bot/resources/what_is_keegan_looking_at/fore.png"
    ).convert("RGBA")

    # Corner points for his screen (close enough)
    corners = [(450, 1600), (1448, 856), (984, 2300), (1800, 1500)]

    # Perform a perspective transform on the input image
    transformed_image = input_image.transform(
        foreground.size,  # Match the size of the foreground image
        Image.QUAD,
        [coord for point in corners for coord in point],  # Flatten corner points
        Image.BICUBIC,
    )

    # Composite the transformed image onto the foreground
    result = Image.alpha_composite(foreground, transformed_image.convert("RGBA"))

    return result
