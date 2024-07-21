import shutil
from pathlib import Path
from unittest import TestCase

from add_noqa_to_import import fix_file


class TestAddComments(TestCase):
    def test_add_comments(self):
        shutil.copyfile(
            'test_folders/backup_test_files/uncommented_file.py',
            'test_folders/test_folder1/uncommented_file.py',
        )
        fix_file('test_folders/test_folder1/uncommented_file.py')
        self.assertEqual(
            Path('test_folders/test_folder1/uncommented_file.py').read_text(),)
