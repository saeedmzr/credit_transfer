import random
import string


def generate_random_string(length=64):
    """Generates a random string of the specified length containing letters and digits.

    Args:
      length: The desired length of the string.

    Returns:
      A random string of the specified length.
    """

    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
