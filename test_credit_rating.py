import unittest
import json
from pydantic import ValidationError
from credit_rating import calculate_credit_rating_in_batches  # Import the function from your module

class TestCreditRating(unittest.TestCase):

    def test_valid_mortgages(self):
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
        self.assertEqual(calculate_credit_rating_in_batches(valid_json), "AAA")

    def test_invalid_credit_score(self):
        """Test with an invalid credit score (> 850)"""
        invalid_json = json.dumps({
            "mortgages": [
                {
                    "credit_score": 900,  # Invalid (> 850)
                    "loan_amount": 200000,
                    "property_value": 250000,
                    "annual_income": 60000,
                    "debt_amount": 20000,
                    "loan_type": "fixed",
                    "property_type": "single_family"
                }
            ]
        })
        response = calculate_credit_rating_in_batches(invalid_json)
        self.assertIn("400 Bad Request", response)

    def test_invalid_negative_loan_amount(self):
        """Test with a negative loan amount"""
        invalid_json = json.dumps({
            "mortgages": [
                {
                    "credit_score": 720,
                    "loan_amount": -150000,  # Invalid (< 0)
                    "property_value": 175000,
                    "annual_income": 45000,
                    "debt_amount": 10000,
                    "loan_type": "adjustable",
                    "property_type": "condo"
                }
            ]
        })
        response = calculate_credit_rating_in_batches(invalid_json)
        self.assertIn("400 Bad Request", response)

    def test_missing_required_field(self):
        """Test with missing required fields (loan_amount)"""
        invalid_json = json.dumps({
            "mortgages": [
                {
                    "credit_score": 720,
                    "property_value": 175000,  # Missing loan_amount
                    "annual_income": 45000,
                    "debt_amount": 10000,
                    "loan_type": "adjustable",
                    "property_type": "condo"
                }
            ]
        })
        response = calculate_credit_rating_in_batches(invalid_json)
        self.assertIn("400 Bad Request", response)
        self.assertIn("loan_amount", response)  # Should indicate missing field

    def test_low_risk_mortgages(self):
        """Test low risk mortgages that should get AAA"""
        test_json = json.dumps({
            "mortgages": [
                {
                    "credit_score": 800,
                    "loan_amount": 100000,
                    "property_value": 250000,  # LTV = 40%
                    "annual_income": 100000,
                    "debt_amount": 10000,  # DTI = 10%
                    "loan_type": "fixed",
                    "property_type": "single_family"
                }
            ]
        })
        self.assertEqual(calculate_credit_rating_in_batches(test_json), "AAA")  # Highly secure rating

    def test_extreme_low_credit_score(self):
        """Test mortgages with very low credit scores < 650"""
        test_json = json.dumps({
          "mortgages": [
    {
        "credit_score": 600,
        "loan_amount": 180000,
        "property_value": 190000,  
        "annual_income": 45000,
        "debt_amount": 15000,
        "loan_type": "adjustable",
        "property_type": "condo"
    }
]
        })
        self.assertEqual(calculate_credit_rating_in_batches(test_json), "C")  # Highly speculative

    def test_average_credit_score_adjustment(self):
        """Test average credit score adjustment logic"""
        test_json = json.dumps({
            "mortgages": [
               {
        "credit_score": 710,
        "loan_amount": 200000,
        "property_value": 220000, 
        "annual_income": 70000,
        "debt_amount": 25000,
        "loan_type": "fixed",
        "property_type": "single_family"
    },
    {
        "credit_score": 620,
        "loan_amount": 150000,
        "property_value": 180000,
        "annual_income": 50000,
        "debt_amount": 20000,
        "loan_type": "adjustable",
        "property_type": "condo"
    }
            ]
        })
        self.assertEqual(calculate_credit_rating_in_batches(test_json), "BBB")  # Medium risk

    def test_empty_mortgages_list(self):
        """Test empty mortgage list should return an invalid message"""
        empty_json = json.dumps({"mortgages": []})
        self.assertEqual(calculate_credit_rating_in_batches(empty_json), "Invalid: No mortgages provided")

    def test_large_data_set(self):
        """Test handling of large dataset (scalability)"""
        large_data = {"mortgages": [
            {
                "credit_score": 720,
                "loan_amount": 100000 + i * 1000,
                "property_value": 150000 + i * 2000,
                "annual_income": 60000 + i * 500,
                "debt_amount": 10000 + i * 100,
                "loan_type": "fixed" if i % 2 == 0 else "adjustable",
                "property_type": "single_family" if i % 3 == 0 else "condo"
            } for i in range(1000)  # 1000 mortgage entries
        ]}
        large_json = json.dumps(large_data)
        self.assertIn(calculate_credit_rating_in_batches(large_json), ["AAA", "BBB", "C"])  # Should return a valid rating

if __name__ == "__main__":
    unittest.main()
