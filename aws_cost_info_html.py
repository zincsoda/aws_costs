#!/usr/bin/env python3
import boto3
import os
from datetime import date, timedelta, datetime
from aws_cost_info import get_date_ranges, get_cost_and_usage, get_forecast

def format_currency_html(amount, color=None):
    """Format currency with HTML styling"""
    if color is None:
        color = "#00ffff"  # Cyan
    return f'<span style="color: {color}; font-weight: bold;">${amount:,.2f}</span>'

def format_percentage_html(percentage, color=None):
    """Format percentage with appropriate color based on value"""
    if color is None:
        if percentage > 0:
            color = "#ff5555"  # Bright red for increases
        elif percentage < 0:
            color = "#55ff55"  # Bright green for decreases
        else:
            color = "#ffff55"  # Yellow for no change
    
    sign = "+" if percentage > 0 else ""
    return f'<span style="color: {color}; font-weight: bold;">{sign}{percentage:+.2f}%</span>'

def generate_html(mtd_cost, last_month_same_period_cost, last_month_total_cost, 
                  forecasted_cost, mtd_comparison, total_comparison, last_update_date):
    """Generate HTML page with cost information"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Cost Summary</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: #000000;
            color: #ffffff;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'Courier New', monospace;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            padding: 30px;
        }}
        
        .cost-section {{
            margin-bottom: 25px;
            padding: 15px;
            border-left: 3px solid #5555ff;
        }}
        
        .cost-label {{
            font-size: 18px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .cost-value {{
            font-size: 28px;
            margin: 10px 0;
        }}
        
        .comparison {{
            margin-top: 8px;
            margin-left: 20px;
            font-size: 14px;
            color: #cccccc;
        }}
        
        .comparison-item {{
            margin: 5px 0;
        }}
        
        .emoji {{
            font-size: 20px;
        }}
        
        .update-date {{
            text-align: right;
            margin-top: 30px;
            padding-top: 15px;
            color: #666666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="cost-section">
            <div class="cost-label">
                <span class="emoji">📅</span>
                <span>Month-to-date cost:</span>
            </div>
            <div class="cost-value">
                {format_currency_html(mtd_cost)}
            </div>
            <div class="comparison">
                <div class="comparison-item">
                    ↳ {format_percentage_html(mtd_comparison)} compared to last month for the same period
                </div>
                <div class="comparison-item">
                    ↳ Last month's cost for the same period: {format_currency_html(last_month_same_period_cost, "#ffff55")}
                </div>
            </div>
        </div>
        
        <div class="cost-section">
            <div class="cost-label">
                <span class="emoji">🔮</span>
                <span>Total forecasted cost for current month:</span>
            </div>
            <div class="cost-value">
                {format_currency_html(forecasted_cost, "#ff55ff")}
            </div>
            <div class="comparison">
                <div class="comparison-item">
                    ↳ {format_percentage_html(total_comparison)} compared to last month's total costs
                </div>
                <div class="comparison-item">
                    ↳ Last month's total cost: {format_currency_html(last_month_total_cost, "#ffff55")}
                </div>
            </div>
        </div>
        
        <div class="update-date">
            Last updated: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    return html_content

def main():
    """Generate HTML report"""
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

    # Generate HTML
    last_update_date = datetime.now()
    html_content = generate_html(
        mtd_cost, 
        last_month_same_period_cost, 
        last_month_total_cost,
        forecasted_cost, 
        mtd_comparison, 
        total_comparison,
        last_update_date
    )
    
    # Create output directory if it doesn't exist
    output_dir = "html"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write to file
    output_file = os.path.join(output_dir, "index.html")
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {output_file}")

if __name__ == "__main__":
    main()

