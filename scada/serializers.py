import copy
from typing import override
from rest_framework import serializers
from scada.models import Inverter, Plant, Meter, Weather, SCB, SCBString


# Prevents type coersion to string
class StrictCharField(serializers.CharField):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("invalid", input=data)
        return super().to_internal_value(data)


class InverterSerializer(serializers.ModelSerializer):
    uid = StrictCharField()
    devName = StrictCharField()
    devType = StrictCharField()

    class Meta:
        model = Inverter
        exclude = ["id"]


class PlantSerializer(serializers.ModelSerializer):
    uid = StrictCharField()
    devName = StrictCharField()
    devType = StrictCharField()

    class Meta:
        model = Plant
        exclude = ["id"]


class MeterSerializer(serializers.ModelSerializer):
    uid = StrictCharField()
    devName = StrictCharField()
    devType = StrictCharField()

    class Meta:
        model = Meter
        exclude = ["id"]


class WeatherSerializer(serializers.ModelSerializer):
    uid = StrictCharField()
    devName = StrictCharField()
    devType = StrictCharField()

    class Meta:
        model = Weather
        exclude = ["id"]


class SCBStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = SCBString
        exclude = ["id", "scb"]


class SCBSerializer(serializers.ModelSerializer):
    uid = StrictCharField()
    devName = StrictCharField()
    devType = StrictCharField()
    strings = SCBStringSerializer(many=False, read_only=False)

    class Meta:
        model = SCB
        exclude = ["id"]

    def __init__(self, *args, **kwargs):
        """Transforms the flat SCB+string data into a nested object
        so that the string related attributes are grouped under the
        key 'strings'. This is because the `strings` field is defined
        as a nested serializer (`SCBStringSerializer`) which takes
        care of serialization in that specific format.
        """
        if "data" in kwargs:
            kwargs["data"] = self._transform_data(kwargs["data"])

        super().__init__(*args, **kwargs)

    def _transform_data(self, data):
        data = copy.deepcopy(data)

        if "strings" not in data:
            data["strings"] = {}

        string_fields = [
            f.name for f in SCBString._meta.get_fields() if f.name not in ["id", "scb"]
        ]

        for field_name in string_fields:
            if field_name in data:
                data["strings"][field_name] = data.pop(field_name)

        return data

    @override
    def create(self, validated_data):
        strings_data = validated_data.pop("strings")
        scb = SCB.objects.create(**validated_data)
        SCBString.objects.create(scb=scb, **strings_data)
        return scb

    @override
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        strings = representation.pop("strings")
        representation.update(strings)
        return representation
