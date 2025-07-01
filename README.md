# SCADA Data Collection and API Service

This project is a Django-based application designed to collect and manage data from various SCADA (Supervisory Control and Data Acquisition) devices. It provides a RESTful API for receiving time-series data from devices such as meters, inverters, weather stations, and string combiner boxes (SCBs). The application validates the incoming data, stores it in a structured database, and offers endpoints to retrieve the collected information.

## Features

- **Data Ingestion:** A robust endpoint to receive and process JSON payloads containing data from multiple device types in a single request.
- **Data Validation:** Ensures the integrity of incoming data by validating content type, required attributes, and data formats.
- **Partial Success Handling:** In cases of mixed valid and invalid data, the API gracefully handles partial success and provides detailed error feedback.
- **Data Retrieval:** Endpoints to fetch detailed data for specific devices or the latest data for an entire plant.
- **Scalable Architecture:** Built with Django and Django REST Framework, providing a solid foundation for further expansion and development.

## Installation

To get the project up and running on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd django-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
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

   
   


The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

### 1. Post Data

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

### 2. Get Inverter Details

- **Endpoint:** `/api/v1/inverter/<devName>/`
- **Method:** `GET`
- **Description:** Retrieves all data records for a specific inverter.
- **Response:** A JSON array of inverter data objects.

### 3. Get Plant Data

- **Endpoint:** `/api/v1/plant/<uid>/`
- **Method:** `GET`
- **Description:** Retrieves the latest data for all devices associated with a specific plant UID.
- **Response:** A JSON object containing the latest data for each device type within the plant.

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
