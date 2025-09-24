#!/usr/bin/env python

from scripts.pipeline import commands
from scripts.pipeline.main.setup import setup
from scripts.pipeline.main.util import find, copy_from_container


if __name__ == "__main__":
    context = setup()
    commands.basic_pipeline(context).run()
    output = copy_from_container(
        context, context.setting.container_data.output_path.ctn_pos
    )

    print("Output:")
    for file in find(output):
        print(file)
