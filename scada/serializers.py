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

    # Convert boolean fields to integers (1/0) for API response
    _inv_stat = serializers.SerializerMethodField()
    _inv_event = serializers.SerializerMethodField()
    _inv_alarm1 = serializers.SerializerMethodField()
    _inv_error1 = serializers.SerializerMethodField()

    class Meta:
        model = Inverter
        exclude = ["id"]

    def get__inv_stat(self, obj):
        return 1 if obj._inv_stat else 0

    def get__inv_event(self, obj):
        return 1 if obj._inv_event else 0

    def get__inv_alarm1(self, obj):
        return 1 if obj._inv_alarm1 else 0

    def get__inv_error1(self, obj):
        return 1 if obj._inv_error1 else 0 
    

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


class DataViewRequestSerializer(serializers.Serializer):
    class TagsSerializer(serializers.Serializer):
        Inverter = serializers.ListField(child=serializers.CharField(), required=False)
        Meter = serializers.ListField(child=serializers.CharField(), required=False)
        Weather = serializers.ListField(child=serializers.CharField(), required=False)
        SCB = serializers.ListField(child=serializers.CharField(), required=False)
        Plant = serializers.ListField(child=serializers.CharField(), required=False)

    class DataSerializer(serializers.Serializer):
        Inverter = serializers.ListField(
            child=serializers.ListField(child=serializers.CharField(), allow_empty=True),
            required=False,

        )
        Meter = serializers.ListField(
            child=serializers.ListField(child=serializers.CharField(), allow_empty=True),
            required=False,
        )
        Weather = serializers.ListField(
            child=serializers.ListField(child=serializers.CharField(), allow_empty=True),
            required=False,
        )
        SCB = serializers.ListField(
            child=serializers.ListField(child=serializers.CharField(), allow_empty=True),
            required=False,
        )
        Plant = serializers.ListField(
            child=serializers.ListField(child=serializers.CharField(), allow_empty=True),
            required=False,
        )

    Tags = TagsSerializer()
    Data = DataSerializer()
    Timestamp = serializers.IntegerField()
    UID = serializers.CharField()


class PlantDataResponseSerializer(serializers.Serializer):
    Plant = PlantSerializer(many=True)
    Inverter = InverterSerializer(many=True)
    Weather = WeatherSerializer(many=True)
    SCB = SCBSerializer(many=True)


class DataViewResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Success or error message", required=False)
    errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
        help_text="Dictionary of errors by device type, if any",
    )
