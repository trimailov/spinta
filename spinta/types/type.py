import copy
import pathlib

from spinta.types import Type, NA
from spinta.commands import Command


class Array(Type):
    metadata = {
        'name': 'array',
    }


class ManifestLoad(Command):
    metadata = {
        'name': 'manifest.load',
    }

    def execute(self):
        assert isinstance(self.args.data, dict)

        for name, params in self.obj.metadata.properties.items():
            if name in self.args.data and self.args.data[name] is not NA:
                value = self.args.data[name]
            else:
                # Get default value.
                default = params.get('default', NA)
                if isinstance(default, (list, dict)):
                    value = copy.deepcopy(default)
                else:
                    value = default

                # Check if value is required.
                if params.get('required', False) and value is NA:
                    self.error(f"Parameter {name!r} is required for {self.obj}.")

                # If value is not given, set it to None.
                if value is NA:
                    value = None

            value_type = params.get('type')

            if value_type is not None and not isinstance(value_type, str):
                self.error(f"Unknown data type: {value_type!r} of {name!r} property.")

            if value_type == 'path' and isinstance(value, str):
                value = pathlib.Path(value)

            if value_type == 'object' and value is not None and not isinstance(value, dict):
                self.error(f"Expected 'dict' type for {name!r}, got {value.__class__.__name__!r}.")

            # Set parameter on the spec object.
            setattr(self.obj, name, value)

        unknown_keys = set(self.args.data.keys()) - set(self.obj.metadata.properties.keys())
        if unknown_keys:
            keys = '\n  - '.join(unknown_keys)
            self.error(f"Unknown parameters:\n  - {keys}")


class PrepareType(Command):
    metadata = {
        'name': 'prepare.type',
    }

    def execute(self):
        for name, params in self.obj.metadata.properties.items():
            value = getattr(self.obj, name)
            type = params.get('type')
            if type:
                if type not in self.store.types:
                    self.error(f"Unknown type {type!r} for {name!r}.")
                value = self.run(self.load({'type': type, 'parent': self.obj}, bare=True), {
                    'prepare': {
                        'obj': self.obj,
                        'prop': name,
                        'value': value,
                    },
                })
                setattr(self.obj, name, value)


class Prepare(Command):
    metadata = {
        'name': 'prepare',
    }

    def execute(self):
        return self.args.value


class Serialize(Command):
    metadata = {
        'name': 'serialize',
    }

    def execute(self):
        output = {}
        for k, v in self.obj.metadata.properties.items():
            v = getattr(self.obj, k, NA)
            if v is NA:
                continue
            output[k] = v
        return output
