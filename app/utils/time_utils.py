from datetime import datetime

def get_timestamp_filename(prefix="scan", ext=".pdf"):
    """Generate filename with current timestamp."""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{ext}"

def get_timestamp_folder(prefix="session"):
    """Generate a timestamped folder name."""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"
