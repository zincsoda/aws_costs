#!/usr/bin/env python3
import boto3
from datetime import date, timedelta

# ANSI color codes for highlighting
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_YELLOW = '\033[93m'

def format_currency(amount, color=None):
    """Format currency with highlighting"""
    if color is None:
        color = Colors.CYAN
    return f"{color}{Colors.BOLD}${amount:,.2f}{Colors.RESET}"

def format_percentage(percentage, color=None):
    """Format percentage with appropriate color based on value"""
    if color is None:
        if percentage > 0:
            color = Colors.BRIGHT_RED  # Red for increases
        elif percentage < 0:
            color = Colors.BRIGHT_GREEN  # Green for decreases
        else:
            color = Colors.YELLOW  # Yellow for no change
    
    sign = "+" if percentage > 0 else ""
    return f"{color}{Colors.BOLD}{sign}{percentage:+.2f}%{Colors.RESET}"

def get_date_ranges():
    today = date.today()
    start_of_this_month = today.replace(day=1)
    start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
    end_of_last_month = start_of_this_month  # Use start of this month as exclusive end date

    return {
        "current_month_to_date": (start_of_this_month.isoformat(), today.isoformat()),
        "last_month_same_period": (start_of_last_month.isoformat(), (start_of_last_month + timedelta(days=today.day)).isoformat()),
        "last_month_total": (start_of_last_month.isoformat(), end_of_last_month.isoformat()),
        "current_month_forecast": (max(today, start_of_this_month).isoformat(), (start_of_this_month + timedelta(days=32)).replace(day=1).isoformat())
    }

def get_cost_and_usage(client, start_date, end_date):
    response = client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"]
    )
    total_cost = sum(float(item['Total']['UnblendedCost']['Amount']) for item in response['ResultsByTime'])
    return total_cost

def get_forecast(client, start_date, end_date):
    response = client.get_cost_forecast(
        TimePeriod={"Start": start_date, "End": end_date},
        Metric="UNBLENDED_COST",
        Granularity="MONTHLY"
    )
    return float(response['ForecastResultsByTime'][0]['MeanValue'])

def main():
    # Initialize Cost Explorer client
    client = boto3.client('ce', region_name='us-east-1')
    date_ranges = get_date_ranges()

    # Get costs
    mtd_cost = get_cost_and_usage(client, *date_ranges["current_month_to_date"])
    last_month_same_period_cost = get_cost_and_usage(client, *date_ranges["last_month_same_period"])
    last_month_total_cost = get_cost_and_usage(client, *date_ranges["last_month_total"])
    forecasted_cost = get_forecast(client, *date_ranges["current_month_forecast"])

    # Calculate percentages
    mtd_comparison = ((mtd_cost - last_month_same_period_cost) / last_month_same_period_cost) * 100 if last_month_same_period_cost else 0
    total_comparison = ((forecasted_cost - last_month_total_cost) / last_month_total_cost) * 100 if last_month_total_cost else 0

    # Print results
    print(f"\n{Colors.BOLD}{Colors.BLUE}================= AWS COST SUMMARY ================={Colors.RESET}")
    print(f"📅 Month-to-date cost: {format_currency(mtd_cost)}")
    print(f"   ↳ {format_percentage(mtd_comparison)} compared to last month for the same period")
    print(f"   ↳ Last month's cost for the same period: {format_currency(last_month_same_period_cost, Colors.YELLOW)}\n")

    print(f"🔮 Total forecasted cost for current month: {format_currency(forecasted_cost, Colors.MAGENTA)}")
    print(f"   ↳ {format_percentage(total_comparison)} compared to last month's total costs")
    print(f"   ↳ Last month's total cost: {format_currency(last_month_total_cost, Colors.YELLOW)}")
    print(f"{Colors.BOLD}{Colors.BLUE}===================================================={Colors.RESET}\n")

if __name__ == "__main__":
    main()
