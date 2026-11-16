# Flask ADS-B Data API

## Description

This project implements an API using Python Flask that accesses ADS-B data stored in a MySQL database.

The API provides three methods to retrieve aircraft datapoints, count datapoints within a geographic polygon, and calculate average ground speed for each flight.

The database table used is `class_datapoints`.

## Technologies Used

- Python
- Flask
- MySQL
- PyMySQL
- PyYAML

## Database Table

The API uses the following MySQL table:

`class_datapoints`

| Field | Type |
|---|---|
| dpid | int |
| date_time | datetime |
| hex | varchar(30) |
| flight_num | varchar(25) |
| squawk | int |
| lat | decimal(10,7) |
| lon | decimal(10,7) |
| geo_point | point |
| fid | int |
| gs | decimal(7,2) |
| alt_gps | int |
| alt_baro | int |
| cat | varchar(10) |
| track | decimal(10,3) |
| nav_heading | decimal(10,2) |

## API Authentication

All API requests must include a key parameter.

The valid API key is:

`123`

Requests without the correct key will not be fulfilled.

## API Methods

All three methods use the HTTP GET method.

### 1. Get Data

**Endpoint:**

`/getData`

**Example request:**

```http
/getData?key={key}&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15
```

**Parameters:**

| Parameter | Description | Required |
|---|---|---|
| key | API authentication key | Yes |
| start | Starting date and time | Yes |
| end | Ending date and time | Yes |

**Description:**

Returns a list of ADS-B datapoints between the specified start and end dates.

The maximum number of returned datapoints is 500.

### 2. Count In Polygon

**Endpoint:**

`/countInPolygon`

**Example request:**

```http
/countInPolygon?key={key}&polygon=-74 42,-75 39,-74 41,-74 42
```

**Parameters:**

| Parameter | Description | Required |
|---|---|---|
| key | API authentication key | Yes |
| polygon | List of longitude and latitude coordinate pairs | Yes |

**Description:**

Returns the count of ADS-B datapoints located inside the specified geographic polygon.

The polygon coordinates are supplied as longitude and latitude pairs.

### 3. Get Average Speed By Flight

**Endpoint:**

`/getAvgSpeedByFlight`

**Example request:**

```http
/getAvgSpeedByFlight?key={key}&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00
```

**Parameters:**

| Parameter | Description | Required |
|---|---|---|
| key | API authentication key | Yes |
| start | Starting date and time | No |
| end | Ending date and time | No |

**Description:**

Calculates the average ground speed (`gs`) for each flight, grouped by `flight_num`, over the specified time period.

Start and end dates are optional. If provided, both dates must be included.

The maximum number of returned results is 500.

## API Response

All API responses contain the following top-level keys:

| Key | Description |
|---|---|
| code | Indicates whether the request was successful. `1` = successful, `0` = failed. |
| msg | Message describing the result or reason for failure. |
| req | Identifies the requested API method. |

## Running the API

Run the Flask application using:

```bash
python app.py
```
