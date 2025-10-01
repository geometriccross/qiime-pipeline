import datetime
import random
import string


def generate_id() -> str:
    """
    Generate a unique ID string in the format: 'mmddHHMMSS_xyz'
    where mm is the month name (lowercase), dd is the day,
    HHMMSS is the time, and xyz is a random 3-character string.

    Returns:
        str: Generated ID string
    """
    now = datetime.datetime.now()
    month = now.strftime("%b").lower()
    datetime_str = now.strftime("%d%H%M%S")

    # Generate random 3 characters (lowercase alphanumeric)
    chars = string.ascii_lowercase + string.digits
    random_str = "".join(random.choices(chars, k=3))

    return f"{month}{datetime_str}_{random_str}"
