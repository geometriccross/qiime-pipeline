from scripts.pipeline.main.alpha_rarefaction import alpha_rarefaction_pipeline
from scripts.pipeline.main.db import db_pipeline


def test_alpha_rarefaction_commands_is_current(mocked_context):
    assembly, result = alpha_rarefaction_pipeline(mocked_context).command_list()


def test_db_commands_is_current(mocked_context):
    assembly, result = db_pipeline(mocked_context).command_list()
