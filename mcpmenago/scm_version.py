import sys
import time


def get_dynamic_version(version):
    package_version = f"py{sys.version_info.major}{sys.version_info.minor}"
    return f"+{int(time.time())}.{package_version}"
