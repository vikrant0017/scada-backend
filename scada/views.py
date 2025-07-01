from enum import StrEnum

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import UnsupportedMediaType, ValidationError
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from .models import SCB, Inverter, Plant, Weather
from .serializers import (
    DataViewRequestSerializer,
    DataViewResponseSerializer,
    InverterSerializer,
    MeterSerializer,
    PlantDataResponseSerializer,
    PlantSerializer,
    SCBSerializer,
    WeatherSerializer,
)


class DeviceType(StrEnum):
    PLANT = "Plant"
    METER = "Meter"
    INVERTER = "Inverter"
    WEATHER = "Weather"
    SCB = "SCB"


SERIALIZER_MAPPING = {
    DeviceType.INVERTER: InverterSerializer,
    DeviceType.METER: MeterSerializer,
    DeviceType.WEATHER: WeatherSerializer,
    DeviceType.SCB: SCBSerializer,
    DeviceType.PLANT: PlantSerializer,
}


@extend_schema(
    request=DataViewRequestSerializer,
    responses={201: DataViewResponseSerializer, 206: DataViewResponseSerializer},
)
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
            return Response(
                {"detail": "Partial success", "errors": errors},
                status=status.HTTP_206_PARTIAL_CONTENT,
            )

        return Response(
            {"detail": "Data created successfully"}, status=status.HTTP_201_CREATED
        )

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


@extend_schema(responses=InverterSerializer(many=True))
class InverterDetailView(APIView):
    def get(self, request, devName):
        inverter = Inverter.objects.filter(devName=devName)
        serializer = InverterSerializer(inverter, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(responses=PlantDataResponseSerializer)
class PlantDataView(APIView):

    def get(self, request, uid):
        data = {
            "Plant": self._get_latest_device_data(Plant, uid),
            "Inverter": self._get_latest_device_data(Inverter, uid),
            "Weather": self._get_latest_device_data(Weather, uid),
            "SCB": self._get_latest_device_data(SCB, uid, select_related=True),
        }

        # Use the response serializer to handle the serialization
        serializer = PlantDataResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_latest_device_data(self, model, uid, select_related=False):
        """function to get the latest record for each device type and name."""
        queryset = model.objects.filter(uid=uid)
        if select_related:
            queryset = queryset.select_related()
            
        return (
            queryset
            .annotate(
                row_number=Window(
                    expression=RowNumber(),
                    partition_by=[F("devType"), F("devName")],
                    order_by=F("timestamp").desc(),
                )
            )
            .filter(row_number=1)
        )
