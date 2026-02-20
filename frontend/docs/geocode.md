# Reverse Geocode

Convert latitude/longitude coordinates to a city and province/state using Google's Geocoding API.

**No authentication required.**

## Get Location Name

```
GET /api/businesses/geocode/?lat={lat}&lng={lng}
```

| Param | Type | Description |
|-------|------|-------------|
| `lat` | float | Latitude (required) |
| `lng` | float | Longitude (required) |

**Response:**

```json
{
  "city": "Toronto",
  "province": "Ontario",
  "province_code": "ON",
  "country": "Canada",
  "country_code": "CA",
  "formatted_address": "Toronto, ON, Canada"
}
```

| Field | Description |
|-------|-------------|
| `city` | City / locality name |
| `province` | Full province or state name |
| `province_code` | Short code (e.g. `ON`, `CA`, `NY`) |
| `country` | Full country name |
| `country_code` | ISO 2-letter code (e.g. `CA`, `US`) |
| `formatted_address` | Google's formatted address string |

**Error responses:**

| Status | Reason |
|--------|--------|
| 400 | Missing or invalid `lat`/`lng` parameters |
| 404 | No locality found for the given coordinates |
| 502 | Google Geocoding API error |

## Client Usage

```js
import { reverseGeocode } from './api/client'

const { data } = await reverseGeocode(43.651, -79.347)
console.log(data.city)           // "Toronto"
console.log(data.province_code)  // "ON"
console.log(data.country)        // "Canada"
```
