from scripts.pipeline.main.db import command_list


def test_command_list_check_current(mocked_context):
    assembly, result = command_list(mocked_context)
