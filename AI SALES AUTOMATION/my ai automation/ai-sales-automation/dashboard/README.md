# AI Sales Automation Dashboard

A web-based dashboard to monitor and visualize the AI Sales Automation system.

## Features

- Real-time overview of leads, outreach, and deals
- Visual sales funnel
- Lead location distribution charts
- Outreach activity tracking
- Content schedule management

## Installation

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure the parent system is properly configured with the required API credentials.

## Usage

### Standalone Mode

Run the dashboard directly:
```bash
python run_dashboard.py
```

This will start the dashboard on http://localhost:5000

### Integrated Mode

Run the dashboard as part of the main automation system:
```bash
cd ..
python main.py --dashboard
```

You can also combine with other operations:
```bash
python main.py --task leads --dashboard
```

## Dashboard Sections

1. **Overview**: Summary metrics and key performance indicators
2. **Leads**: Detailed lead management and analytics
3. **Outreach**: Social media outreach tracking
4. **Deals**: Payment and sales pipeline
5. **Content**: Content posting schedule and performance

## Customization

You can customize the dashboard by editing the following files:
- `templates/index.html`: Dashboard UI
- `app.py`: API endpoints and data processing

## Troubleshooting

If the dashboard fails to start:
1. Check that all dependencies are installed
2. Verify that the parent directories are properly set up
3. Check the logs in `../logs/dashboard.log`
