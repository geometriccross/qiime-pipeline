#!/usr/bin/env python

import unittest
import shutil
from pathlib import Path
from datetime import time
import scripts.extract_id


class TestExtractID(unittest.TestCase):
    def setUp(self):
        hash_val = hash(str(time.time()).encode()).hexdigest()
        test_dir = Path("/tmp") / hash_val
        test_dir.mkdir()

        for csv_file in Path("meta").glob("*.csv"):
            shutil.copy(csv_file, test_dir)
            test_dir = Path("/tmp").joinpath(hash(time))
            test_dir.mkdir()


if __name__ == "__main__":
    unittest.main()
