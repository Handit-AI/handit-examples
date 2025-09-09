"""Test script for the loan risk workflow."""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.risk_analysis_workflow.workflow import run_workflow


def create_test_files():
    """Create mock test files for demonstration."""
    # Mock ID document (as text for demo)
    id_content = b"""
    DRIVER LICENSE
    
    Name: John Michael Smith
    License Number: D123456789
    Date of Birth: 1985-03-15
    Address: 123 Main Street, San Francisco, CA 94102
    Issue Date: 2020-01-15
    Expiry Date: 2025-01-15
    """
    
    # Mock payslip (as text for demo)
    payslip_content = b"""
    PAYSLIP
    
    Employee: John M. Smith
    Employee ID: EMP001234
    
    Employer: Tech Solutions Inc.
    Period: 2024-01-01 to 2024-01-31
    
    Gross Pay: $8,500.00
    Federal Tax: $1,700.00
    State Tax: $425.00
    Social Security: $527.00
    Medicare: $123.25
    401k: $425.00
    Health Insurance: $200.00
    
    Total Deductions: $3,400.25
    Net Pay: $5,099.75
    
    YTD Gross: $8,500.00
    YTD Net: $5,099.75
    """
    
    # Mock bank statement CSV
    bank_csv_content = b"""Date,Description,Amount,Balance
2024-01-01,Opening Balance,0,5000.00
2024-01-05,Tech Solutions Inc. Payroll,5099.75,10099.75
2024-01-07,Rent Payment,-2000.00,8099.75
2024-01-10,Grocery Store,-150.00,7949.75
2024-01-12,Electric Bill,-120.00,7829.75
2024-01-15,Restaurant,-45.00,7784.75
2024-01-20,Gas Station,-60.00,7724.75
2024-01-25,Online Shopping,-200.00,7524.75
2024-01-31,Closing Balance,0,7524.75"""
    
    return [
        {
            "content": id_content,
            "type": "pdf",  # Pretending it's a PDF
            "name": "drivers_license.pdf"
        },
        {
            "content": payslip_content,
            "type": "pdf",  # Pretending it's a PDF
            "name": "payslip_jan2024.pdf"
        },
        {
            "content": bank_csv_content,
            "type": "csv",
            "name": "bank_statement_jan2024.csv"
        }
    ]


def test_workflow():
    """Test the complete workflow."""
    print("\n" + "="*70)
    print(" LOAN RISK WORKFLOW TEST")
    print("="*70)
    
    # Create test files
    files = create_test_files()
    
    # Create test messages
    messages = [
        {
            "role": "user",
            "content": "Please review my loan application documents."
        }
    ]
    
    # Create test options
    options = {
        "country": "US",
        "currency": "USD"
    }
    
    print(f"\nTest Setup:")
    print(f"- Files: {[f['name'] for f in files]}")
    print(f"- Messages: {len(messages)}")
    print(f"- Options: {options}")
    
    try:
        # Run workflow
        result = run_workflow(
            files=files,
            messages=messages,
            options=options
        )
        
        # Print results
        print("\n" + "="*70)
        print(" WORKFLOW RESULTS")
        print("="*70)
        
        print(f"\nRisk Assessment:")
        print(f"- Score: {result.get('risk_score', 'N/A')}")
        print(f"- Tier: {result.get('risk_tier', 'N/A')}")
        print(f"- Decision: {result.get('final_recommendation', {}).get('decision', 'N/A')}")
        
        print(f"\nTop Reasons:")
        for i, reason in enumerate(result.get('reasons', [])[:5], 1):
            print(f"{i}. {reason}")
        
        print(f"\nDocument Types Identified:")
        for idx, doc_type in result.get('doc_types', {}).items():
            print(f"- File {idx}: {doc_type}")
        
        print(f"\nChecks Performed: {len(result.get('checks', []))}")
        
        print(f"\nAssistant Response:")
        print(f'"{result.get("assistant_message", "No response generated")}"')
        
        # Save full results to file
        output_file = "test_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nFull results saved to {output_file}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Test completed successfully!")
    return True


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Run test
    success = test_workflow()
    sys.exit(0 if success else 1)