# SCADA Data Collection and API Service

This project is a Django-based application designed to collect and manage data from various SCADA (Supervisory Control and Data Acquisition) devices. It provides a RESTful API for receiving time-series data from devices such as meters, inverters, weather stations, and string combiner boxes (SCBs). The application validates the incoming data, stores it in a structured database, and offers endpoints to retrieve the collected information.

## Installation

To get the project up and running on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vikrant0017/scada-backend.git
   cd django-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   # or for windows
   venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Optional: Create a superuser (for Django admin):**
   ```bash  
   python manage.py createsuperuser
   ```


## API 
The API is accessible at `http://127.0.0.1:8000`.

### Testing with Postman
You can test the API endpoints using our Postman collection. Since the API runs on your local server, you'll need to use the Postman desktop application (browser version won't work with localhost).

[![Run in Postman](https://run.pstmn.io/button.svg)](https://www.postman.com/payload-participant-67764480/my-workspace/collection/bq86ffg/scada-rest-api)

Click the "Run in Postman" button to open the collection in Postman and fork the collection to your workspace to use it. This will allow you to easily test the API endpoints and explore the request/response formats.

**Note:** Make sure your local development server is running before testing the endpoints in Postman.

### Documentation (SwaggerUI)

- **Endpoint:** `/api/schema/swagger-ui/`
- **Method:** `GET`
- **Description:** Interactive API documentation where you can explore and test all available API endpoints. The documentation is automatically generated from the API schema and provides detailed information about request/response formats, parameters, and example requests.

### Endpoints

#### 1. Post Data

- **Endpoint:** `api/v1/data/`
- **Method:** `POST`
- **Description:** Submits data from various devices. The request body must be in `application/json` format.
- **Request Body Example:**
  ```json
  {
      "Timestamp": 1625097600,
      "UID": "plant-001",
      "Data": {
          "Inverter": [
              ["inv-001", 230.5, 5.2, ...],
              ["inv-002", 231.0, 5.1, ...]
          ],
          "Meter": [
              ["mtr-001", 12345.67, ...]
          ]
      },
      "Tags": {
          "Inverter": ["devName", "_inv_vin", "_inv_lin", ...],
          "Meter": ["devName", "_mtr_whtot", ...]
      }
  }
  ```
- **Responses:**
  - `201 Created`: Data successfully created.
  - `206 Partial Content`: Some data was processed successfully, but errors occurred with other parts.
  - `400 Bad Request`: Validation error, such as missing attributes.
  - `415 Unsupported Media Type`: Invalid content type.



#### 2. Get Inverter Details

- **Endpoint:** `/api/v1/inverter/<devName>/`
- **Method:** `GET`
- **Description:** Retrieves all data records for a specific inverter.
- **Response:** A JSON array of inverter data objects.

#### 3. Get Plant Data

- **Endpoint:** `/api/v1/plant/<uid>/`
- **Method:** `GET`
- **Description:** Retrieves the latest data for all devices associated with a specific plant UID.
- **Response:** A JSON object containing the latest data for each device type within the plant.


## Sample Data Generation

The project includes a `generate-samples.py` script that helps generate sample JSON payloads for testing the API endpoints. The script creates test data that matches the expected schema of the API.

### Features
- Creates properly formatted JSON payloads that match the API's expected schema
- Includes device names and types based on the SuryaLog API Guide Document.
- Supports custom UID and timestamp values

### Usage

1. **Basic Usage** (uses default values):
   ```bash
   python generate-samples.py
   ```

2. **Custom UID and Timestamp**:
   ```bash
   python generate-samples.py [--uid <uid>] [--timestamp <timestamp>]
   ```


## Data Models

The application uses the following Django models to structure the data:

- `Plant`: General plant information.
- `Meter`: Data from energy meters.
- `Inverter`: Data from solar inverters.
- `Weather`: Data from weather stations.
- `SCB`: Data from string combiner boxes.
- `SCBString`: Detailed string-level data for SCBs.

## Dependencies

The project relies on the following major packages:

- `Django`: The web framework for the application.
- `djangorestframework`: A powerful toolkit for building Web APIs.
- `drf-spectacular`: Generates OpenAPI 3 schemas for Django REST Framework.
