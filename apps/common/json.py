import json

from django.core.serializers.json import DjangoJSONEncoder


class JsonUtil:
    @classmethod
    def dumps(cls, data):
        return json.dumps(data, ensure_ascii=False, cls=DjangoJSONEncoder)

    @classmethod
    def loads(cls, data):
        return json.loads(data)
