# PMS Integration

This project demonstrates a robust Django-based integration framework for consuming, validating, transforming, and exposing hotel booking data from external PMS (Property Management Systems). It is designed with maintainability, configurability, and separation of concerns in mind.

---

## Data Modeling Strategy

Represents the real-world relationships between Hotels, Rooms, Guests, and their associated Bookings. The schema supports multi-tenancy and extensible configuration.

### Entity Relationships

```text
Hotel
├── Has one PMSConfig (PMS type + version)
├── Has many Bookings
├── Has many Rooms

PMSConfig (Schema Configurations)
├── Defines field mappings, status mappings
└── Can be reused by multiple Hotels using the same PMS provider/version

Room
├── Belongs to a Hotel
└── Can be linked to many Bookings

Guest
└── Referenced by Booking (non-unique model for simplicity, scoped per booking)

Booking
├── Belongs to Hotel
├── References Guest (inline or as a model)
└── References Room
```

This relational model is designed to:

* Fully isolate data per hotel
* Track and validate bookings with contextual PMS rules
* Support real-world flexibility in PMS schemas across clients

---

## Configurable Mapping & Validation

Every PMS version comes with a dedicated **JSON configuration file** that defines:

* `field_mappings`: Using JSONPath, template-based strings, and transformation functions (e.g. `parse_date`, `map_status`)
* `status_mappings`: Maps external PMS status codes to internal enums
* `validation_rules`:

  * Required fields
  * Field-level validation (type, format, min/max, enum)
  * Business rules (e.g. max booking duration)

### Why Config-Driven?

* No code changes when PMS schemas evolve — **just update JSON**
* ➕ Easy onboarding of new PMS system

---

## Validation Pipeline

A multi-stage validation system ensures that only clean, meaningful data is ingested:

1. **Raw Schema Validation**

   * JSONSchema validation if schema is provided
2. **Business Rule Validation**

   * Required fields, enums, date consistency, amounts, etc.
3. **Sanitization**

   * Trimming strings, escaping special characters, converting empty to `None`

Robust error types are used for clarity and separation:

* `PMSConnectionError`
* `PMSDataValidationError`
* `PMSBusinessRuleError`
* `PMSMappingError`

---

## Periodic Data Sync (Background Ingestion)

Instead of querying the PMS in real-time, a background job periodically fetches booking data for each hotel from its configured PMS, validates and stores it locally.

### Why Background Sync?

* **Performance**: API responses are instant (served from DB)
* **Resilience**: API works even if PMS is down
* **Freshness**: Periodic bulk UPSERT ensures up-to-date records (some latency)
* **Parallel Processing**: Bookings can be ingested per hotel in parallel

### Ingestion Pipeline

```text
for each Hotel:
    1. Load PMSConfig (based on PMS type/version)
    2. Fetch raw data (currently via mocked PMSClient)
    3. Validate schema, business logic
    4. Map to internal DTOs
    5. upsert into DB
```

---

##  API Endpoint

```
GET /api/integrations/pms/bookings/
```

Returns all ingested and validated booking data.

---

## Test Coverage

Critical components are tested with unit tests: 

* Mapper transformation logic
* Validation stages
* API endpoint response
* Error cases (invalid data, schema violations)

---

## Areas for Future Improvement
- Bulk insert optimization for Booking ingestion (currently done per record)
- Full test suite with edge case coverage
- Admin UI for PMS config upload (optional)

--- 
**Raushan Kumar** 
