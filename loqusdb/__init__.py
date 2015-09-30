import logging
from pkg_resources import get_distribution

logger = logging.getLogger(__name__)

__version__ = get_distribution("loqusdb").version
