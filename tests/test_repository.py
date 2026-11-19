"""Checks for metadata maintenance and protection of experimental bytes."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

FILE=Path(__file__).resolve().parents[1]/'tools/repository_check.py'
SPEC=importlib.util.spec_from_file_location('submission_integrity',FILE)
INTEGRITY=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(INTEGRITY)


class RepositoryIntegrity(unittest.TestCase):
    def test_changed_baseline_cannot_be_refreshed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'docs').mkdir()
            evidence=root/'raw.csv';evidence.write_bytes(b'value\r\n17\r\n')
            manifest=root/'docs/BASELINE_SHA256.txt'
            manifest.write_text(INTEGRITY.digest(evidence)+'  raw.csv\n')
            evidence.write_bytes(b'value\n17\n')
            with self.assertRaisesRegex(ValueError,'Checksum mismatch'):
                INTEGRITY.refresh(root)
            self.assertFalse((root/'CHECKSUMS.txt').exists())

    def test_unsafe_manifest_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest=Path(temporary)/'bad.txt'
            manifest.write_text('0'*64+'  ../outside.csv\n')
            with self.assertRaisesRegex(ValueError,'Unsafe checksum path'):
                INTEGRITY.manifest_entries(manifest)

    def test_duplicate_manifest_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest=Path(temporary)/'bad.txt'
            manifest.write_text(('0'*64+'  raw.csv\n')*2)
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                INTEGRITY.manifest_entries(manifest)

    def test_git_and_build_outputs_do_not_enter_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for name in ['.git/config','scratch/run.txt','dist/archive.zip','nested/__pycache__/module.pyc','datasets/input.csv']:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('example')
            self.assertEqual([str(path.relative_to(root)) for path in INTEGRITY.product_files(root)],['datasets/input.csv'])


if __name__=='__main__': unittest.main()
