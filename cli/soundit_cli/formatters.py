"""
Output formatters for CLI
"""
import json
import csv
import sys
from typing import List, Dict, Any
from datetime import datetime


def format_table(data: List[Dict[str, Any]], columns: List[str] = None) -> str:
    """Format data as a table"""
    if not data:
        return "No data found."
    
    # Auto-detect columns from first item
    if columns is None:
        columns = list(data[0].keys())
    
    # Calculate column widths
    widths = {}
    for col in columns:
        header_len = len(str(col))
        max_data_len = max(len(str(row.get(col, ""))) for row in data)
        widths[col] = max(header_len, max_data_len) + 2
    
    # Build table
    lines = []
    
    # Header
    header = "|".join(f" {str(col).upper():<{widths[col]-1}}" for col in columns)
    lines.append(header)
    lines.append("-" * len(header))
    
    # Rows
    for row in data:
        row_str = "|".join(
            f" {str(row.get(col, '')):<{widths[col]-1}}" 
            for col in columns
        )
        lines.append(row_str)
    
    return "\n".join(lines)


def format_json(data: Any) -> str:
    """Format data as JSON"""
    return json.dumps(data, indent=2, default=str)


def format_csv(data: List[Dict[str, Any]], columns: List[str] = None) -> str:
    """Format data as CSV"""
    if not data:
        return ""
    
    if columns is None:
        columns = list(data[0].keys())
    
    output = []
    writer = csv.DictWriter(sys.stdout, fieldnames=columns, extrasaction='ignore')
    
    # Capture output
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    for row in data:
        writer.writerow({k: v for k, v in row.items() if k in columns})
    
    return buf.getvalue()


def format_summary(stats: Dict[str, Any]) -> str:
    """Format dashboard statistics"""
    lines = [
        "=" * 50,
        "         SOUND IT PLATFORM STATISTICS",
        "=" * 50,
        "",
        f"  Total Users:          {stats.get('total_users', 0):,}",
        f"  Total Businesses:     {stats.get('total_businesses', 0):,}",
        f"  Total Artists:        {stats.get('total_artists', 0):,}",
        f"  Total Events:         {stats.get('total_events', 0):,}",
        f"  Total Tickets Sold:   {stats.get('total_tickets_sold', 0):,}",
        f"  Total Revenue:        ${stats.get('total_revenue', 0):,.2f}",
        "",
        "  Pending Actions:",
        f"    - Payouts:          {stats.get('pending_payouts', 0)}",
        f"    - Verifications:    {stats.get('pending_verifications', 0)}",
        "",
        "=" * 50,
    ]
    return "\n".join(lines)


def format_user(user: Dict[str, Any]) -> str:
    """Format single user details"""
    lines = [
        "=" * 50,
        "              USER DETAILS",
        "=" * 50,
        "",
        f"  ID:           {user.get('id')}",
        f"  Name:         {user.get('first_name', '')} {user.get('last_name', '')}",
        f"  Email:        {user.get('email', 'N/A')}",
        f"  Phone:        {user.get('phone', 'N/A')}",
        f"  Role:         {user.get('role', 'N/A')}",
        f"  Status:       {user.get('status', 'N/A')}",
        f"  Verified:     {user.get('is_verified', False)}",
        f"  City:         {user.get('city', 'N/A')}",
        f"  Created:      {user.get('created_at', 'N/A')}",
        "",
        "=" * 50,
    ]
    return "\n".join(lines)


def format_event(event: Dict[str, Any]) -> str:
    """Format single event details"""
    lines = [
        "=" * 50,
        "              EVENT DETAILS",
        "=" * 50,
        "",
        f"  ID:           {event.get('id')}",
        f"  Title:        {event.get('title', 'N/A')}",
        f"  Status:       {event.get('status', 'N/A')}",
        f"  Date:         {event.get('start_date', 'N/A')}",
        f"  City:         {event.get('city', 'N/A')}",
        f"  Venue:        {event.get('venue_name', event.get('venue', {}).get('name', 'N/A'))}",
        f"  Organizer:    {event.get('organizer_name', 'N/A')}",
        "",
        f"  Description:",
        f"  {event.get('description', 'N/A')[:200]}...",
        "",
        "=" * 50,
    ]
    return "\n".join(lines)


def output(data: Any, format_type: str = "table", columns: List[str] = None):
    """Output data in specified format"""
    if format_type == "json":
        print(format_json(data))
    elif format_type == "csv":
        if isinstance(data, list):
            print(format_csv(data, columns))
        else:
            print(format_json(data))
    else:  # table
        if isinstance(data, list):
            print(format_table(data, columns))
        elif isinstance(data, dict):
            # Single item, convert to list
            print(format_table([data], columns))
        else:
            print(data)
