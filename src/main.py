#!/usr/bin/env python

from .pipeline import commands
from .pipeline.main.setup import setup
from .pipeline.main.util import find, copy_from_container


def main():
    context = setup()
    commands.basic_pipeline(context).run()
    output = copy_from_container(
        context, context.setting.container_data.output_path.ctn_pos
    )

    print("Output:")
    for file in find(output.iterdir(), ["qzv", "qza"]):
        print(file)


if __name__ == "__main__":
    main()
