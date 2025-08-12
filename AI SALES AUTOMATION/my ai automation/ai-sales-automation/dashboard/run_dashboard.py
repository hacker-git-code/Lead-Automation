#!/usr/bin/env python3
"""
Run the AI Sales Automation Dashboard
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("../logs", exist_ok=True)

    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))

    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)
