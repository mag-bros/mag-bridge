from datetime import datetime


def get_dynamic_version(version):
    return f"+{datetime.now().strftime('%Y%m%d%H%M%S')}"
