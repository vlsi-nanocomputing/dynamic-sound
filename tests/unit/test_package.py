from importlib import metadata
from pathlib import Path
import types
import inspect

import dynamic_sound as ds


class TestPackage:

    def test_package_import(self):
        assert ds is not None

    def test_package_metadata(self):
        assert ds.__name__ == "dynamic_sound"
        assert ds.__package__ == "dynamic_sound"

        package_path = Path(ds.__file__)
        assert package_path.name == "__init__.py"
        assert package_path.parent.name == "dynamic_sound"

        package_metadata = metadata.metadata("dynamic-sound")
        assert package_metadata.get("Name") == "dynamic-sound"
        assert package_metadata.get("Version")
        assert package_metadata.get("Summary")
        assert package_metadata.get("Author")
        assert package_metadata.get("Author-email")
        assert package_metadata.get("License")
    
    def test_version(self):
        assert hasattr(ds, "__version__")
        assert isinstance(ds.__version__, str)
        assert ds.__version__ == metadata.version("dynamic-sound")

    def test_package_api_modules(self):
        public_modules = [
            "acoustics",
            "environment",
            "microphones",
            "sources",
            "generators"
        ]
        for module_name in public_modules:
            assert hasattr(ds, module_name)
            module = getattr(ds, module_name)
            assert isinstance(module, types.ModuleType)

    def test_package_api_classes(self):
        public_classes = [
            "Path",
            "Simulation"
        ]
        for class_name in public_classes:
            assert hasattr(ds, class_name)
            cls = getattr(ds, class_name)
            assert inspect.isclass(cls)
