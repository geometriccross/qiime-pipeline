from scripts.pipeline.main.alpha_rarefaction import alpha_rarefaction_pipeline
from scripts.pipeline.main.db import db_pipeline
from scripts.pipeline.main.basic import basic_pipeline


def test_alpha_rarefaction_commands_is_current(mocked_context):
    assembly, result = alpha_rarefaction_pipeline(mocked_context).command_list()


def test_db_commands_is_current(mocked_context):
    assembly, result = db_pipeline(mocked_context).command_list()


def test_basic_commands_is_current(mocked_context):
    assembly, pre_dir, core_dir = basic_pipeline(mocked_context).command_list()
