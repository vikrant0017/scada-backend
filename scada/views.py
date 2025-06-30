from enum import StrEnum

from rest_framework import status
from rest_framework.exceptions import UnsupportedMediaType, ValidationError
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from .models import SCB, Inverter, Plant, Weather
from .serializers import (
    InverterSerializer,
    MeterSerializer,
    PlantSerializer,
    SCBSerializer,
    WeatherSerializer,
)

class DeviceType(StrEnum): 
    PLANT    = "Plant"
    METER    = "Meter"
    INVERTER = "Inverter"
    WEATHER  = "Weather"
    SCB      = "SCB"


SERIALIZER_MAPPING = {
    DeviceType.INVERTER: InverterSerializer,
    DeviceType.METER   : MeterSerializer,
    DeviceType.WEATHER : WeatherSerializer,
    DeviceType.SCB     : SCBSerializer,
    DeviceType.PLANT   : SCBSerializer,
}


class DataView(APIView):
    def post(self, request):
        # Validate Content Type
        content_type = request.content_type
        if content_type != "application/json":
            raise UnsupportedMediaType(content_type)

        # Validate all required top-level attributes exist in JSON payload 
        req_body = request.data
        missing_attrs = self._validate_attributes(
            req_body, ["Timestamp", "UID", "Data", "Tags"]
        )
        if len(missing_attrs):
            raise ValidationError({"missing_required_attributes": missing_attrs})

        # Validate and persist data into its corresponding tables
        device_data = req_body["Data"]
        device_tags = req_body["Tags"]
        extra_fields = {"timestamp": req_body["Timestamp"], "uid": req_body["UID"]}

        errors = {}
        for device_type in DeviceType:
            if device_type in device_data:
                errs = self._process_device_data(
                    device_data[device_type],
                    device_tags[device_type],
                    SERIALIZER_MAPPING[device_type],
                    extra_fields,
                )

                if len(errs):
                    errors[device_type] = errs

        if errors:
            return Response(errors, status=status.HTTP_206_PARTIAL_CONTENT)

        return Response(status=status.HTTP_201_CREATED)

    def _validate_attributes(self, data, attrs):
        return [attr for attr in attrs if attr not in data]

    def _process_device_data(
        self,
        device_data: list[list],
        fields: list[str],
        Serializer: ModelSerializer,
        extra_fields: dict,
    ):
        errs = []
        for idx, data in enumerate(device_data):
            if len(fields) != len(data):
                errs.append(f"[Index: {idx}] Tags and data length mismatch.")
                continue

            data = dict(zip(fields, data))
            data.update(extra_fields)
            s = Serializer(data=data)
            if not s.is_valid():
                errs.append(f"[Index: {idx}] {s.errors}")
                continue
            s.save()

        return errs


class InverterDetailView(APIView):
    def get(self, request, devName):
        inverter = Inverter.objects.filter(devName=devName)
        serializer = InverterSerializer(inverter, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlantDataView(APIView):
    def get(self, request, uid):
        inverter = Inverter.objects.filter(uid=uid)
        plant = Plant.objects.filter(uid=uid)
        weather = Weather.objects.filter(uid=uid)
        scb = SCB.objects.filter(uid=uid).select_related()

        inverter_serializer = InverterSerializer(inverter, many=True)
        plant_serializer = PlantSerializer(plant, many=True)
        weather_serializer = WeatherSerializer(weather, many=True)
        scb_serializer = SCBSerializer(scb, many=True)

        return Response(
            {
                "Plant": plant_serializer.data,
                "Inverter": inverter_serializer.data,
                "Weather": weather_serializer.data,
                "SCB": scb_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
