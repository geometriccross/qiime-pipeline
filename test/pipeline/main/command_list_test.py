from scripts.pipeline.main.alpha_rarefaction import command_list as alpha_cmds
from scripts.pipeline.main.db import command_list as db_cmds


def test_alpha_rarefaction_commands_is_current(mocked_context):
    assembly, result = alpha_cmds(mocked_context)


def test_db_commands_is_current(mocked_context):
    assembly, result = db_cmds(mocked_context)
