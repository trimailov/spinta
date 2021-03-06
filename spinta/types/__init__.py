class _NA:

    def __repr__(self):
        return 'NA'


NA = _NA()


class MetaData:

    def __init__(self, cls):
        self.cls = cls
        self.metadata = cls.metadata
        self.name = self.metadata['name']
        self.bases = self._get_bases()
        self.properties = self._get_properties()

    def _get_bases(self):
        bases = []
        for cls in self.cls.mro():
            if hasattr(cls, 'metadata'):
                bases.append(cls)
            else:
                break
        return bases

    def _get_properties(self):
        properties = {}
        for cls in reversed(self.bases):
            if isinstance(cls.metadata, dict):
                properties.update(cls.metadata.get('properties', {}))
            else:
                properties.update(cls.metadata.metadata.get('properties', {}))
        return properties


class MetaClass(type):

    def __new__(cls, name, bases, attrs):
        assert 'metadata' in attrs
        assert isinstance(attrs['metadata'], (dict, MetaData))
        assert isinstance(attrs['metadata'], dict) and 'name' in attrs['metadata']
        cls = super().__new__(cls, name, bases, attrs)
        cls.metadata = MetaData(cls)
        return cls


class Type(metaclass=MetaClass):
    metadata = {
        'name': None,
        'properties': {
            'type': {'type': 'string', 'required': True},
            'name': {'type': 'string', 'required': True},
            'title': {'type': 'string'},
            'description': {'type': 'string', 'default': ''},
            'parent': {'type': None},
        },
    }

    type = None
    name = None

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(type={self.type}, name={self.name})"
