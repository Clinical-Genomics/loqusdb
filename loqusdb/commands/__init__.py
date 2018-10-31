from .cli import cli as base_command

from .wipe import wipe as wipe_command
from .load import load as load_command
from .update import update as update_command
from .delete import delete as delete_command
from .export import export as export_command
from .view import cases as cases_command
from .view import variants as variants_command
from .view import index as index_command
from .migrate import migrate as migration_command
from .identity import identity as identity_command
from .annotate import annotate as annotate_command
from .dump import dump as dump_command
from .restore import restore as restore_command
