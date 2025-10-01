#!/usr/bin/env python3
import boto3
from datetime import date, timedelta
from calendar import month_name

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

def get_last_6_months_ranges():
    """Get date ranges for the last 6 months"""
    today = date.today()
    ranges = []
    
    for i in range(6):
        # Calculate the start of the month (i months ago)
        if today.month - i <= 0:
            year = today.year - 1
            month = 12 + (today.month - i)
        else:
            year = today.year
            month = today.month - i
        
        start_of_month = date(year, month, 1)
        
        # Calculate the end of the month (start of next month)
        if month == 12:
            end_of_month = date(year + 1, 1, 1)
        else:
            end_of_month = date(year, month + 1, 1)
        
        ranges.append({
            'start': start_of_month.isoformat(),
            'end': end_of_month.isoformat(),
            'month_name': month_name[month],
            'year': year,
            'month': month
        })
    
    return ranges

def get_cost_and_usage(client, start_date, end_date):
    """Get cost and usage data for a given date range"""
    try:
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"]
        )
        
        if response['ResultsByTime']:
            total_cost = sum(float(item['Total']['UnblendedCost']['Amount']) for item in response['ResultsByTime'])
            return total_cost
        else:
            return 0.0
    except Exception as e:
        print(f"Error getting cost data for {start_date} to {end_date}: {e}")
        return 0.0

def calculate_statistics(costs):
    """Calculate summary statistics from the cost data"""
    if not costs:
        return {}
    
    total_cost = sum(costs)
    avg_cost = total_cost / len(costs)
    min_cost = min(costs)
    max_cost = max(costs)
    
    # Calculate month-over-month changes
    changes = []
    for i in range(1, len(costs)):
        if costs[i-1] > 0:
            change = ((costs[i] - costs[i-1]) / costs[i-1]) * 100
        else:
            change = 0
        changes.append(change)
    
    avg_change = sum(changes) / len(changes) if changes else 0
    
    return {
        'total': total_cost,
        'average': avg_cost,
        'minimum': min_cost,
        'maximum': max_cost,
        'avg_change': avg_change,
        'changes': changes
    }

def main():
    # Initialize Cost Explorer client
    client = boto3.client('ce', region_name='us-east-1')
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}================= AWS HISTORICAL COSTS (Last 6 Months) ================={Colors.RESET}")
    
    # Get date ranges for last 6 months
    month_ranges = get_last_6_months_ranges()
    costs = []
    
    # Get costs for each month
    for i, month_range in enumerate(month_ranges):
        cost = get_cost_and_usage(client, month_range['start'], month_range['end'])
        costs.append(cost)
        
        # Format month display
        month_display = f"{month_range['month_name']} {month_range['year']}"
        
        # Add trend indicator
        trend = ""
        if i > 0:
            prev_cost = costs[i-1]
            if prev_cost > 0:
                change_pct = ((cost - prev_cost) / prev_cost) * 100
                if change_pct > 5:
                    trend = f" {Colors.RED}↗{Colors.RESET}"
                elif change_pct < -5:
                    trend = f" {Colors.GREEN}↘{Colors.RESET}"
                else:
                    trend = f" {Colors.YELLOW}→{Colors.RESET}"
        
        print(f"📅 {month_display:15} {format_currency(cost)}{trend}")
    
    # Calculate and display statistics
    stats = calculate_statistics(costs)
    
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}📊 SUMMARY STATISTICS{Colors.RESET}")
    print(f"💰 Total cost (6 months): {format_currency(stats['total'], Colors.MAGENTA)}")
    print(f"📈 Average monthly cost: {format_currency(stats['average'], Colors.CYAN)}")
    print(f"📉 Lowest month: {format_currency(stats['minimum'], Colors.GREEN)}")
    print(f"📈 Highest month: {format_currency(stats['maximum'], Colors.RED)}")
    
    if stats['avg_change'] != 0:
        print(f"📊 Average month-over-month change: {format_percentage(stats['avg_change'])}")
    
    # Show trend analysis
    print(f"\n{Colors.BOLD}{Colors.YELLOW}📈 TREND ANALYSIS{Colors.RESET}")
    recent_3_months = costs[:3]
    older_3_months = costs[3:6]
    
    if older_3_months and recent_3_months:
        recent_avg = sum(recent_3_months) / len(recent_3_months)
        older_avg = sum(older_3_months) / len(older_3_months)
        
        if older_avg > 0:
            trend_change = ((recent_avg - older_avg) / older_avg) * 100
            print(f"Recent 3 months vs older 3 months: {format_percentage(trend_change)}")
            
            if trend_change > 10:
                print(f"{Colors.RED}⚠️  Costs are trending upward significantly{Colors.RESET}")
            elif trend_change < -10:
                print(f"{Colors.GREEN}✅ Costs are trending downward significantly{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}📊 Costs are relatively stable{Colors.RESET}")
    
    print(f"{Colors.BOLD}{Colors.BLUE}================================================================{Colors.RESET}\n")

if __name__ == "__main__":
    main()
