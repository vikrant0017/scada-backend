from numbers import Number
import os
import sys
import django
import json
import random
import argparse
from django.db import models
from datetime import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"

try:
    django.setup()
except Exception as e:
    print("Error setting up Django:", e)
    sys.exit(1)

# Depends on Django setup
from scada.models import Inverter, SCB, SCBString, Plant, Weather, Meter


dev_types = {
    "Meter": ["SM", "SC", "GM0", "GM1", "DM1", "GM4", "DM4", "MM0", "MM1", "MMn"],
    "Plant": ["PI"],
    "Inverter": [f"I{i}" for i in range(1, 25)],
    "Weather": ["WS"],
    "SCB": [f"S{i}" for i in range(1, 25)],
}

dev_names = {
    "Meter": ["SOLAR_METER", "Main_Meter", "DG_1"],
    "Plant": ["SLM00E923M"],
    "Inverter": [f"Inverter_{i}" for i in range(1, 25)],
    "Weather": ["Digital"],
    "SCB": [f"SCB_{i}" for i in range(1, 25)],
}


def sample_dev(dev_type):
    type_choice = random.choice(dev_types[dev_type])
    if dev_type in ["Inverter", "SCB"]:
        name_choice = dev_names[dev_type][dev_types[dev_type].index(type_choice)]
    else:
        name_choice = random.choice(dev_names[dev_type])
    return type_choice, name_choice


model_map = {
    "Meter": Meter,
    "Plant": Plant,
    "Inverter": Inverter,
    "Weather": Weather,
    "SCB": SCB,
}


def generate_sample(device):
    # Example of generating a model instance
    sample = {}
    if device == "SCB":
        scb_fields = [
            f
            for f in model_map[device]._meta.get_fields()
            if f.name not in ("id", "uid", "scb", "timestamp")
        ]
        scbstring_fields = [
            f for f in SCBString._meta.get_fields() if f.name not in ("id", "scb")
        ]
        fields = scb_fields + scbstring_fields
    else:
        fields = [
            f
            for f in model_map[device]._meta.get_fields()
            if f.name not in ("id", "uid", "scb", "timestamp")
        ]

    for field in fields:
        if field.name in ("id", "uid", "scb", "timestamp"):
            continue

        if isinstance(field, models.CharField) and field.name in ["devType", "devName"]:
            dev_type, dev_name = sample_dev(device)
            sample["devType"] = dev_type
            sample["devName"] = dev_name
            continue

        if isinstance(field, models.IntegerField):
            sample[field.name] = random.randint(0, 100)

        if isinstance(field, models.FloatField):
            sample[field.name] = round(random.uniform(0, 100), 2)

        if isinstance(field, models.BooleanField):
            sample[field.name] = random.choice([1, 0])

    return sample


def generate_samples_for_devices(devices_dict):
    result = {}
    for dev, num_samples in devices_dict.items():
        result[dev] = []
        for _ in range(num_samples):
            sample = generate_sample(dev)
            result[dev].append(sample)
    return result


def generate_json_payload(uid: str, timestamp: int):
    json_payload = {}
    dev_samples = generate_samples_for_devices(
        {
            "Inverter": 5,
            "Plant": 1,
            "Weather": 1,
            "Meter": 5,
            "SCB": 1,
        }
    )

    tags = {}

    for dev, samples in dev_samples.items():
        tags[dev] = list(samples[0].keys())

    data = {}
    for dev, samples in dev_samples.items():
        data[dev] = []
        for sample in samples:
            data[dev].append(list(sample.values()))

    json_payload["Tags"] = tags
    json_payload["Data"] = data
    json_payload["UID"] = uid
    json_payload["Timestamp"] = timestamp

    return json_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid", type=str)
    parser.add_argument("--timestamp", type=int)
    args = parser.parse_args()

    default_uid = "SLM00E923M"
    default_timestamp = int(datetime.now().timestamp())

    json_payload = generate_json_payload(
        uid=args.uid if args.uid else default_uid,
        timestamp=args.timestamp if args.timestamp else default_timestamp,
    )

    sample_number = 1
    samples_dir = "samples"
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir)

    filename = (
        f"sample-{args.timestamp}.json"
        if args.timestamp
        else f"sample-{sample_number}.json"
    )
    while os.path.exists(os.path.join(samples_dir, filename)):
        sample_number += 1
        filename = f"sample-{sample_number}.json"

    with open(os.path.join(samples_dir, filename), "w") as f:
        json.dump(json_payload, f, indent=4)
