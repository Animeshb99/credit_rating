import json
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal

# Define a Pydantic model for a single mortgage
class Mortgage(BaseModel):
    credit_score: int = Field(..., ge=300, le=850, description="Credit score must be between 300 and 850")
    loan_amount: float = Field(..., gt=0, description="Loan amount must be greater than 0")
    property_value: float = Field(..., gt=0, description="Property value must be greater than 0")
    annual_income: float = Field(..., gt=0, description="Annual income must be greater than 0")
    debt_amount: float = Field(..., ge=0, description="Debt amount must be non-negative")
    loan_type: Literal["fixed", "adjustable"]
    property_type: Literal["single_family", "condo"]

# Define a model to handle multiple mortgages
class RMBS(BaseModel):
    mortgages: List[Mortgage]

def calculate_ltv(loan_amount, property_value):
    return loan_amount / property_value

def calculate_dti(debt_amount, annual_income):
    return debt_amount / annual_income

def calculate_mortgage_risk(mortgage: Mortgage):
    risk_score = 0

    # 1️Loan-to-Value (LTV) Ratio
    ltv = calculate_ltv(mortgage.loan_amount, mortgage.property_value)
    if ltv > 0.9:
        risk_score += 2
    elif ltv > 0.8:
        risk_score += 1

    # 2️ Debt-to-Income (DTI) Ratio
    dti = calculate_dti(mortgage.debt_amount, mortgage.annual_income)
    if dti > 0.5:
        risk_score += 2
    elif dti > 0.4:
        risk_score += 1

    # 3️ Credit Score Impact
    if mortgage.credit_score >= 700:
        risk_score -= 1
    elif mortgage.credit_score < 650:
        risk_score += 1

    # 4 Loan Type Impact
    if mortgage.loan_type == "fixed":
        risk_score -= 1
    elif mortgage.loan_type == "adjustable":
        risk_score += 1

    # 5️ Property Type Impact
    if mortgage.property_type == "condo":
        risk_score += 1 

    return risk_score

def calculate_credit_rating_in_batches(json_input, batch_size=10000):
    """Process mortgages in batches to optimize performance."""
    try:
        # Parse and validate input using Pydantic
        if not json.loads(json_input).get('mortgages'):
            return "Invalid: No mortgages provided"
        rmbs = RMBS.model_validate_json(json_input)
    except ValidationError as e:
        error_details = []
        for err in e.errors():
            if err["type"] == "missing":
                error_details.append(f"Missing field: {err['loc'][-1]}")
            else:
                error_details.append(f"Invalid {err['loc'][-1]}: {err['msg']}")
        return "400 Bad Request\n" + "\n".join(error_details)

    total_risk_score = 0
    total_credit_score = 0
    count = 0

    # Process data in batches
    for i in range(0, len(rmbs.mortgages), batch_size):
        batch = rmbs.mortgages[i : i + batch_size]
        for mortgage in batch:
            total_risk_score += calculate_mortgage_risk(mortgage)
            total_credit_score += mortgage.credit_score
            count += 1

    # Adjust risk score based on average credit score
    avg_credit_score = total_credit_score / count if count else 0
    if avg_credit_score >= 700:
        total_risk_score -= 1
    elif avg_credit_score < 650:
        total_risk_score += 1

    # Final Credit Rating
    return "AAA" if total_risk_score <= 2 else "BBB" if total_risk_score <= 5 else "C"

# Example Usage
valid_json = json.dumps({
    "mortgages": [
        {
            "credit_score": 750,
            "loan_amount": 200000,
            "property_value": 250000,
            "annual_income": 60000,
            "debt_amount": 20000,
            "loan_type": "fixed",
            "property_type": "single_family"
        },
        {
            "credit_score": 680,
            "loan_amount": 150000,
            "property_value": 175000,
            "annual_income": 45000,
            "debt_amount": 10000,
            "loan_type": "adjustable",
            "property_type": "condo"
        }
    ]
})

invalid_json = json.dumps({
    "mortgages": [
        {
            "credit_score": 900,  # Invalid credit score (> 850)
            "loan_amount": 200000,
            "property_value": 250000,
            "annual_income": 60000,
            "debt_amount": 20000,
            "loan_type": "fixed",
            "property_type": "single_family"
        }
    ]
})


print(calculate_credit_rating_in_batches(invalid_json))  # Expected output: 400 Bad Request error message
