# AWS Cost Information Script

A simple Python script that retrieves and displays your AWS costs with beautiful color-coded highlighting. Get insights into your current month-to-date spending, forecasts, and comparisons with previous months.

## ✨ Features

- 📊 **Month-to-date cost tracking** - See how much you've spent this month so far
- 🔮 **Cost forecasting** - Get predictions for your total monthly spend
- 📈 **Period-over-period comparisons** - Compare current spending with the same period last month
- 🎨 **Color-coded highlighting** - Easy-to-read output with intuitive color coding
- 💰 **Professional formatting** - Clean, formatted currency and percentage displays

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- AWS CLI configured with appropriate permissions
- Required AWS IAM permissions (see [Permissions](#permissions) section)

### Installation

1. Clone or download this repository:
```bash
git clone <your-repo-url>
cd aws_costs
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install boto3
```

### Usage

Simply run the script:
```bash
python aws_cost_info.py
```

## 📋 Sample Output

```
================= AWS COST SUMMARY =================
📅 Month-to-date cost: $1,234.56
   ↳ +15.3% compared to last month for the same period
   ↳ Last month's cost for the same period: $1,071.23

🔮 Total forecasted cost for current month: $3,456.78
   ↳ +8.7% compared to last month's total costs
   ↳ Last month's total cost: $3,180.45
====================================================
```

## 🔧 Configuration

### AWS Credentials

The script uses the default AWS credential chain. Ensure your credentials are configured via:

1. **AWS CLI**: `aws configure`
2. **Environment variables**: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
3. **IAM roles** (if running on EC2)
4. **AWS credentials file**: `~/.aws/credentials`

### Region

The script is configured to use `us-east-1` by default. To change this, modify line 71 in the script:

```python
client = boto3.client('ce', region_name='your-preferred-region')
```

## 🔐 Permissions

Your AWS credentials need the following IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetCostForecast"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"NoCredentialsError"**: Ensure AWS credentials are properly configured
2. **"AccessDenied"**: Check that your IAM user/role has the required permissions
3. **"InvalidParameter"**: Verify that Cost Explorer is enabled in your AWS account
4. **No data returned**: Cost data may take up to 24 hours to appear

### Enabling Cost Explorer

If you get permission errors, you may need to enable AWS Cost Explorer:

1. Go to the AWS Billing Console
2. Navigate to "Cost Explorer"
3. Click "Enable Cost Explorer"
4. Wait up to 24 hours for data to become available

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting](#troubleshooting) section
2. Review AWS Cost Explorer documentation
3. Open an issue in this repository

---

**Note**: This script uses the AWS Cost Explorer API, which may incur small charges for API calls. The costs are typically negligible for most use cases.
