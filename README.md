# credit_rating

Credit Rating System - Readme
Overview
This system calculates credit ratings for Residential Mortgage-Backed Securities (RMBS) based on mortgage attributes. The implementation includes robust error handling and batch processing capabilities for large datasets.

Key Features
1. Enhanced Error Handling
The system provides detailed validation errors for:

Missing required fields

Invalid field values (out of range)

Empty mortgage lists

Malformed JSON input

Error Types Handled:

400 Bad Request for validation errors

Invalid: No mortgages provided for empty lists

Specific field-level error messages

2. Batch Processing
The system processes mortgages in configurable batches to:

Optimize memory usage

Handle large datasets efficiently

Maintain performance with thousands of mortgages

Default batch size: 10,000 mortgages (configurable)

Validation Rules
Mortgage Model Requirements
All fields are strictly validated:

python
Copy
credit_score: int (300-850)  # Required
loan_amount: float (>0)      # Required
property_value: float (>0)   # Required
annual_income: float (>0)    # Required
debt_amount: float (>=0)     # Required
loan_type: "fixed"|"adjustable"  # Required
property_type: "single_family"|"condo"  # Required
Special Cases
Empty mortgages list returns specific error message

Missing top-level "mortgages" key is treated as invalid input

All field validations are performed before processing

Error Response Format
For validation errors, the system returns:

Copy
400 Bad Request
Missing field: field_name
Invalid field_name: error_description
Testing
The test suite verifies:

Valid mortgage calculations

Various error conditions

Empty list handling

Large dataset processing

Edge cases (minimum/maximum values)

Example Test Cases:

Valid mortgages → "AAA"/"BBB"/"C" rating

Invalid credit score → 400 error

Missing required field → 400 error with details

Empty list → "Invalid: No mortgages provided"

1000+ mortgages → proper rating returned

Usage Example
python
Copy
from credit_rating import calculate_credit_rating_in_batches

# Process valid mortgages
rating = calculate_credit_rating_in_batches(valid_json)
print(f"Credit Rating: {rating}")

# Handle errors
try:
    calculate_credit_rating_in_batches(invalid_json)
except ValueError as e:
    print(f"Error: {e}")
Performance Considerations
Batch processing prevents memory overload

Validation happens before processing

Complex calculations are optimized

Suitable for both small and large datasets

Future Enhancements
Additional property types

More granular risk scoring

Database integration

Async processing

Custom batch size configuration
