from .cli import cli as base_command

from .wipe_db import wipe as wipe_command
from .load_variants import load as load_command
from .delete_variants import delete as delete_command
