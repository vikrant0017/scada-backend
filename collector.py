"""Collect data and feed it to the API"""
# from generate_samples import generate_json_payload

import time
import httpx
import json
import logging

import os

SURYALOG_SECRET = os.environ.get("SURYALOG_SECRET")
SURYALOG_PLANT = os.environ.get("SURYALOG_PLANT")

logging.basicConfig(level=logging.INFO)


def load_json_file(file_name):
    with open(file_name) as f:
        return json.load(f)


sample_response = load_json_file("./samples/suryalog-api-response.json")
device_mapping = load_json_file("device_mapping.json")
device_param_mapping = load_json_file("suryalog_mapping.json")
payload_tags = load_json_file("payload_tags.json")


def ingest(timestamp=int(time.time())):
    rem = timestamp % 300
    stime = timestamp - rem
    etime = stime + 300
    print(stime, etime)

    json_payload = {
        "secret": SURYALOG_SECRET,
        "plant": SURYALOG_PLANT,
        "format": "std",
        "for": "data",
        "stime": stime,
        "etime": etime,
    }

    response = httpx.post(
        "https://master.suryalog.com/api/get_datalog_v1.php", json=json_payload
    )

    json_content = json.loads(response.content)
    if not json_content["result"] == 0:
        logging.error(f"Invalid result {json_content['result']}")
        exit(1)
    if not json_content["data"]:
        logging.error("Missing data in response")
        exit(1)
    if not isinstance(json_content["data"], dict):
        logging.error(f"Invalid data type {type(json_content['data']).__name__}")
        exit(1)

    logging.info(
        f"Data collection from {json_payload['stime']} to {json_payload['etime']}: {json_content['cmsg']} ({response.status_code}); Server Time: {json_content['server_time']}; Data Count: {len(json_content['data'].keys())}"
    )

    device_data_at_interval = json_content["data"]

    UID = "SLM00E923M"
    count = 1
    for sensor_time in device_data_at_interval:
        point_device_data = device_data_at_interval[sensor_time]
        formatted_data = {}

        for device_name in point_device_data:
            device_type = device_mapping[device_name]
            param_map = device_param_mapping[device_type]
            device_tags = payload_tags[device_type]
            specific_device_data = point_device_data[device_name]
            device_payload_data = []
            if device_type not in formatted_data:
                formatted_data[device_type] = []
            for param in device_tags:
                if param == "devType":
                    device_payload_data.append(device_name)
                    continue

                if param == "devName":
                    device_payload_data.append(device_name)
                    continue

                if param in param_map:
                    mapped_param = param_map[param]
                    # Here we are fetching the mapped param from the actual data response
                    device_payload_data.append(
                        specific_device_data.get(mapped_param, None)
                    )
                else:
                    # Since there is no mapping found for param, just make it None which will be null inJSON
                    device_payload_data.append(None)

            formatted_data[device_type].append(device_payload_data)

        payload = {
            "Tags": payload_tags,
            "Data": formatted_data,
            "UID": UID,
            "Timestamp": int(sensor_time),
        }

        with open(f"payload_{count}.json", "w") as f:
            json.dump(payload, f, indent=4)
            count += 1

        r = httpx.post(
            "http://localhost:8000/api/v1/data/", json=payload
        )  # must be JSON serializable
        logging.info(
            f"Sent payload for timestamp {sensor_time}: Response {r.status_code} {r.text}"
        )


while True:
    timestamp = int(time.time())
    ingest(timestamp - 300)  # Prev 5 min
    time.sleep(300)
