from pkg_resources import DistributionNotFound, get_distribution

from .robotinterface import Robot

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed
