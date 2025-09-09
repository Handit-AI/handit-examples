"""CSV processing utilities."""

import io
import csv
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import re


def parse_csv_to_dataframe(csv_content: str) -> pd.DataFrame:
    """Parse CSV content to pandas DataFrame."""
    try:
        # Try to read CSV with pandas
        df = pd.read_csv(io.StringIO(csv_content))
        return df
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return pd.DataFrame()


def detect_csv_structure(csv_content: str) -> Dict[str, Any]:
    """Detect the structure of a CSV file.
    
    Returns information about columns, data types, and potential format.
    """
    df = parse_csv_to_dataframe(csv_content)
    
    if df.empty:
        return {"error": "Unable to parse CSV"}
    
    structure = {
        "rows": len(df),
        "columns": list(df.columns),
        "column_types": {},
        "sample_data": {},
        "detected_type": None  # Will be "bank_statement", "transactions", etc.
    }
    
    # Analyze each column
    for col in df.columns:
        # Get column type
        dtype = str(df[col].dtype)
        structure["column_types"][col] = dtype
        
        # Get sample values (first 3 non-null values)
        sample = df[col].dropna().head(3).tolist()
        structure["sample_data"][col] = sample
    
    # Try to detect document type based on columns
    columns_lower = [col.lower() for col in df.columns]
    
    # Check for bank statement patterns
    bank_keywords = ["date", "description", "amount", "balance", "debit", "credit", "transaction"]
    bank_matches = sum(1 for kw in bank_keywords if any(kw in col for col in columns_lower))
    
    if bank_matches >= 3:
        structure["detected_type"] = "bank_statement"
    elif "salary" in " ".join(columns_lower) or "gross" in " ".join(columns_lower):
        structure["detected_type"] = "payroll"
    else:
        structure["detected_type"] = "unknown"
    
    return structure


def extract_transactions_from_csv(csv_content: str) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """Extract transactions from a bank statement CSV.
    
    Returns:
        Tuple of (transactions list, summary dict with opening/closing balance)
    """
    df = parse_csv_to_dataframe(csv_content)
    
    if df.empty:
        return [], {}
    
    transactions = []
    summary = {
        "opening_balance": 0.0,
        "closing_balance": 0.0,
        "total_credits": 0.0,
        "total_debits": 0.0
    }
    
    # Try to identify columns
    columns_lower = {col: col.lower() for col in df.columns}
    
    # Find date column
    date_col = None
    for col, col_lower in columns_lower.items():
        if "date" in col_lower:
            date_col = col
            break
    
    # Find description column
    desc_col = None
    for col, col_lower in columns_lower.items():
        if "description" in col_lower or "desc" in col_lower or "memo" in col_lower:
            desc_col = col
            break
    
    # Find amount columns (could be single amount or separate debit/credit)
    amount_col = None
    debit_col = None
    credit_col = None
    balance_col = None
    
    for col, col_lower in columns_lower.items():
        if "amount" in col_lower and not amount_col:
            amount_col = col
        elif "debit" in col_lower:
            debit_col = col
        elif "credit" in col_lower:
            credit_col = col
        elif "balance" in col_lower:
            balance_col = col
    
    # Extract transactions
    for idx, row in df.iterrows():
        transaction = {}
        
        # Date
        if date_col:
            try:
                # Parse date flexibly
                date_str = str(row[date_col])
                transaction["date"] = pd.to_datetime(date_str).date()
            except:
                transaction["date"] = None
        
        # Description
        if desc_col:
            transaction["description"] = str(row[desc_col])
        else:
            transaction["description"] = ""
        
        # Amount (handle different formats)
        if amount_col:
            try:
                amount = float(str(row[amount_col]).replace("$", "").replace(",", ""))
                transaction["amount"] = amount
            except:
                transaction["amount"] = 0.0
        elif debit_col and credit_col:
            try:
                debit = float(str(row[debit_col]).replace("$", "").replace(",", "")) if pd.notna(row[debit_col]) else 0
                credit = float(str(row[credit_col]).replace("$", "").replace(",", "")) if pd.notna(row[credit_col]) else 0
                transaction["amount"] = credit - debit  # Credits positive, debits negative
            except:
                transaction["amount"] = 0.0
        else:
            transaction["amount"] = 0.0
        
        # Track totals
        if transaction["amount"] > 0:
            summary["total_credits"] += transaction["amount"]
        else:
            summary["total_debits"] += abs(transaction["amount"])
        
        transactions.append(transaction)
    
    # Get opening and closing balance
    if balance_col and not df.empty:
        try:
            # Opening balance is first row's balance minus first transaction
            first_balance = float(str(df.iloc[0][balance_col]).replace("$", "").replace(",", ""))
            first_transaction = transactions[0]["amount"] if transactions else 0
            summary["opening_balance"] = first_balance - first_transaction
            
            # Closing balance is last row's balance
            summary["closing_balance"] = float(str(df.iloc[-1][balance_col]).replace("$", "").replace(",", ""))
        except:
            pass
    
    return transactions, summary


def categorize_transaction(description: str) -> str:
    """Categorize a transaction based on its description.
    
    Returns one of the predefined categories.
    """
    description_lower = description.lower()
    
    # Define category patterns
    patterns = {
        "salary": ["salary", "payroll", "wages", "direct deposit", "employer"],
        "housing": ["rent", "mortgage", "lease", "apartment", "housing"],
        "utilities": ["electric", "gas", "water", "internet", "phone", "utility", "cable"],
        "groceries": ["grocery", "supermarket", "walmart", "target", "kroger", "safeway", "whole foods"],
        "dining": ["restaurant", "cafe", "coffee", "mcdonald", "starbucks", "pizza", "food delivery"],
        "transport": ["uber", "lyft", "gas station", "fuel", "parking", "transit", "metro"],
        "insurance": ["insurance", "geico", "allstate", "progressive"],
        "healthcare": ["pharmacy", "doctor", "hospital", "medical", "dental", "health"],
        "subscriptions": ["netflix", "spotify", "amazon prime", "subscription", "membership"],
        "education": ["tuition", "school", "university", "college", "education"],
        "debt_repayment": ["loan payment", "credit card payment", "payment to", "capital one"],
        "cash": ["atm", "cash withdrawal", "withdrawal"],
        "fees": ["fee", "charge", "penalty", "overdraft"],
        "gambling": ["casino", "lottery", "betting", "gambling", "poker"],
        "transfer": ["transfer", "zelle", "venmo", "paypal", "wire"]
    }
    
    for category, keywords in patterns.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    
    return "other"