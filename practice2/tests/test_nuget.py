"""Проверки собственного чтения NuGet и выбора версий: этап 2."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nuget import NuGetRepository, manifest_dependencies
from versions import choose_version, matches


class NuGetTests(unittest.TestCase):
    """Проверять формат метаданных без обязательного доступа к сети."""

    def test_version_ranges(self):
        """Границы интервалов и минимальные версии различаются."""
        self.assertTrue(matches("2.0.0", "[1.0,2.0]"))
        self.assertFalse(matches("2.0.0", "[1.0,2.0)"))
        self.assertFalse(matches("1.0.0", "(1.0,)"))
        self.assertTrue(matches("1.0.0", "(,1.0]"))
        self.assertTrue(matches("1.0.0", "[1.0]"))
        self.assertFalse(matches("1.0.1", "[1.0]"))
        versions = ["2.0.0", "1.10.0", "1.2.0", "3.0.0-rc.1"]
        self.assertEqual(choose_version(versions), "2.0.0")
        self.assertEqual(choose_version(versions, "1.3"), "1.10.0")
        with self.assertRaises(ValueError):
            choose_version(versions, "[5.0]")

    def test_xml_groups_and_empty_group(self):
        """Чужие платформы не смешиваются, пустая группа сохраняется."""
        xml = '''<package xmlns="urn:nuget"><metadata><dependencies>
        <group targetFramework="net8.0" />
        <group targetFramework="net7.0">
        <dependency id="Other" version="[1.0]" />
        </group></dependencies></metadata></package>'''
        self.assertEqual(manifest_dependencies(xml, "net8.0"), [])
        self.assertEqual(manifest_dependencies(xml, "net7.0"),
                         [("other", "[1.0]")])
        with self.assertRaises(ValueError):
            manifest_dependencies(xml, "net6.0")

    def test_service_index_versions_and_manifest(self):
        """URL извлекается из индекса, затем читается XML-манифест."""
        index = {"resources": [{"@type": "PackageBaseAddress/3.0.0",
                                "@id": "https://example.org/flat/"}]}
        responses = [json.dumps(index), '{"versions": ["1.0.0"]}',
                     '<package><metadata><dependencies>'
                     '<dependency id="Child" version="1.0" />'
                     '</dependencies></metadata></package>',
                     '{"versions": ["1.0.0", "2.0.0"]}']
        with patch("nuget.download", side_effect=responses) as fetch:
            repo = NuGetRepository("https://example.org/index.json")
            root = repo.root("Root", "1.0.0")
            self.assertEqual(root, "root@1.0.0")
            self.assertEqual(repo.dependencies(root), ["child@1.0.0"])
            self.assertIn("root/1.0.0/root.nuspec",
                          fetch.call_args_list[2].args[0])

    def test_missing_service(self):
        """Индекс без адреса пакетов даёт понятную ошибку."""
        with patch("nuget.download", return_value='{"resources": []}'):
            with self.assertRaises(ValueError):
                NuGetRepository("https://example.org/index.json")


if __name__ == "__main__":
    unittest.main()
