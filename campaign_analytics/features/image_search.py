from google_images_search import GoogleImagesSearch
import requests
from PIL import Image
from io import BytesIO

def display_image(image):
    """
    Display an image and return its URL and description.

    Parameters:
    - image (GoogleImagesSearch.ImageResult): An image result object from Google Images Search.

    Returns:
    tuple: A tuple containing the image URL and description.
    """
    # Return the image URL and description
    return image.url, image.description

def download_image(image):
    """
    Download an image from a given URL.

    Parameters:
    - image (GoogleImagesSearch.ImageResult): An image result object from Google Images Search.

    Returns:
    Image: A PIL Image object representing the downloaded image.
    """
    # Send a GET request to the image URL
    response = requests.get(image.url)

    # Open the image using PIL (Python Imaging Library)
    img = Image.open(BytesIO(response.content))

    # Return the PIL Image object
    return img
