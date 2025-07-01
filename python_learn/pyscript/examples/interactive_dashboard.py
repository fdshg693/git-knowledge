#!/usr/bin/env python3
"""
PyScript Interactive Dashboard Example

This example demonstrates creating an interactive data dashboard using PyScript
with real-time data visualization and user interaction.

Features:
- Data loading and processing
- Interactive charts
- Real-time updates
- DOM manipulation
- Event handling
"""

# HTML template that would contain this Python code
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyScript Data Dashboard</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
    <style>
        .dashboard { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .controls { margin: 20px 0; }
        .chart-container { margin: 20px 0; height: 400px; }
        button { margin: 5px; padding: 10px 20px; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>Sales Data Dashboard</h1>
        
        <div class="controls">
            <button id="load-data">Load Data</button>
            <button id="update-chart">Update Chart</button>
            <select id="chart-type">
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="scatter">Scatter Plot</option>
            </select>
        </div>
        
        <div id="data-summary"></div>
        <div id="chart-container" class="chart-container"></div>
        <div id="data-table"></div>
    </div>

    <py-config>
        packages = ["pandas", "numpy", "matplotlib", "plotly"]
    </py-config>

    <py-script>
        # The Python code below would be embedded here
    </py-script>
</body>
</html>
"""

# Python code for PyScript (would be in <py-script> tags)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyscript import document, display
import json
from datetime import datetime, timedelta
import asyncio


class DataDashboard:
    """Interactive data dashboard using PyScript."""

    def __init__(self):
        """Initialize the dashboard."""
        self.data = None
        self.current_chart_type = "line"
        self.setup_event_handlers()
        self.generate_sample_data()

    def generate_sample_data(self):
        """Generate sample sales data for demonstration."""
        # Create sample data
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30), end=datetime.now(), freq="D"
        )

        np.random.seed(42)  # For reproducible results
        sales = np.random.normal(1000, 200, len(dates))
        sales = np.maximum(sales, 0)  # Ensure no negative sales

        # Add some trend
        trend = np.linspace(0, 300, len(dates))
        sales += trend

        # Add some seasonality (weekly pattern)
        weekly_pattern = np.sin(np.arange(len(dates)) * 2 * np.pi / 7) * 100
        sales += weekly_pattern

        self.data = pd.DataFrame(
            {
                "date": dates,
                "sales": sales.round(2),
                "customers": np.random.poisson(50, len(dates)),
                "avg_order_value": (sales / np.random.poisson(50, len(dates))).round(2),
            }
        )

        print("Sample data generated successfully!")
        self.update_data_summary()

    def setup_event_handlers(self):
        """Set up event handlers for interactive elements."""
        # Load data button
        load_btn = document.querySelector("#load-data")
        if load_btn:
            load_btn.addEventListener("click", self.handle_load_data)

        # Update chart button
        update_btn = document.querySelector("#update-chart")
        if update_btn:
            update_btn.addEventListener("click", self.handle_update_chart)

        # Chart type selector
        chart_selector = document.querySelector("#chart-type")
        if chart_selector:
            chart_selector.addEventListener("change", self.handle_chart_type_change)

    def handle_load_data(self, event=None):
        """Handle load data button click."""
        self.generate_sample_data()
        self.create_chart()
        self.display_data_table()
        print("Data loaded and dashboard updated!")

    def handle_update_chart(self, event=None):
        """Handle update chart button click."""
        if self.data is not None:
            self.create_chart()
            print(f"Chart updated with {self.current_chart_type} visualization")

    def handle_chart_type_change(self, event):
        """Handle chart type selection change."""
        self.current_chart_type = event.target.value
        if self.data is not None:
            self.create_chart()
        print(f"Chart type changed to: {self.current_chart_type}")

    def update_data_summary(self):
        """Update the data summary section."""
        if self.data is None:
            return

        summary_html = f"""
        <h3>Data Summary</h3>
        <ul>
            <li><strong>Total Records:</strong> {len(self.data)}</li>
            <li><strong>Date Range:</strong> {self.data['date'].min().strftime('%Y-%m-%d')} to {self.data['date'].max().strftime('%Y-%m-%d')}</li>
            <li><strong>Total Sales:</strong> ${self.data['sales'].sum():,.2f}</li>
            <li><strong>Average Daily Sales:</strong> ${self.data['sales'].mean():,.2f}</li>
            <li><strong>Total Customers:</strong> {self.data['customers'].sum():,}</li>
            <li><strong>Average Order Value:</strong> ${self.data['avg_order_value'].mean():.2f}</li>
        </ul>
        """

        summary_element = document.querySelector("#data-summary")
        if summary_element:
            summary_element.innerHTML = summary_html

    def create_chart(self):
        """Create and display chart based on current chart type."""
        if self.data is None:
            return

        # Clear previous chart
        chart_container = document.querySelector("#chart-container")
        if chart_container:
            chart_container.innerHTML = ""

        plt.clf()  # Clear any existing plots

        if self.current_chart_type == "line":
            self.create_line_chart()
        elif self.current_chart_type == "bar":
            self.create_bar_chart()
        elif self.current_chart_type == "scatter":
            self.create_scatter_plot()

        # Display the plot
        display(plt, target="chart-container")

    def create_line_chart(self):
        """Create a line chart of sales over time."""
        plt.figure(figsize=(12, 6))
        plt.plot(
            self.data["date"],
            self.data["sales"],
            linewidth=2,
            color="#2E86AB",
            marker="o",
            markersize=4,
        )
        plt.title("Daily Sales Trend", fontsize=16, fontweight="bold")
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Sales ($)", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Add trend line
        x_numeric = np.arange(len(self.data))
        z = np.polyfit(x_numeric, self.data["sales"], 1)
        p = np.poly1d(z)
        plt.plot(
            self.data["date"], p(x_numeric), "--", color="red", alpha=0.8, label="Trend"
        )
        plt.legend()

    def create_bar_chart(self):
        """Create a bar chart of weekly sales."""
        # Group by week
        weekly_data = self.data.copy()
        weekly_data["week"] = weekly_data["date"].dt.to_period("W")
        weekly_sales = weekly_data.groupby("week")["sales"].sum()

        plt.figure(figsize=(12, 6))
        bars = plt.bar(
            range(len(weekly_sales)), weekly_sales.values, color="#A23B72", alpha=0.8
        )
        plt.title("Weekly Sales Summary", fontsize=16, fontweight="bold")
        plt.xlabel("Week", fontsize=12)
        plt.ylabel("Total Sales ($)", fontsize=12)
        plt.xticks(
            range(len(weekly_sales)),
            [str(week) for week in weekly_sales.index],
            rotation=45,
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${height:,.0f}",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()

    def create_scatter_plot(self):
        """Create a scatter plot of sales vs customers."""
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(
            self.data["customers"],
            self.data["sales"],
            c=self.data["avg_order_value"],
            cmap="viridis",
            alpha=0.7,
            s=60,
        )
        plt.colorbar(scatter, label="Avg Order Value ($)")
        plt.title("Sales vs Customers Relationship", fontsize=16, fontweight="bold")
        plt.xlabel("Number of Customers", fontsize=12)
        plt.ylabel("Daily Sales ($)", fontsize=12)
        plt.grid(True, alpha=0.3)

        # Add correlation coefficient
        correlation = self.data["customers"].corr(self.data["sales"])
        plt.text(
            0.05,
            0.95,
            f"Correlation: {correlation:.3f}",
            transform=plt.gca().transAxes,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        plt.tight_layout()

    def display_data_table(self):
        """Display data table with latest records."""
        if self.data is None:
            return

        # Show last 10 records
        recent_data = self.data.tail(10).copy()
        recent_data["date"] = recent_data["date"].dt.strftime("%Y-%m-%d")

        table_html = "<h3>Recent Data (Last 10 Days)</h3>"
        table_html += "<table style='width:100%; border-collapse: collapse;'>"
        table_html += "<tr style='background-color: #f2f2f2;'>"
        for col in recent_data.columns:
            table_html += (
                f"<th style='border: 1px solid #ddd; padding: 8px;'>{col.title()}</th>"
            )
        table_html += "</tr>"

        for _, row in recent_data.iterrows():
            table_html += "<tr>"
            for col in recent_data.columns:
                value = row[col]
                if col in ["sales", "avg_order_value"]:
                    value = f"${value:,.2f}"
                elif col == "customers":
                    value = f"{value:,}"
                table_html += (
                    f"<td style='border: 1px solid #ddd; padding: 8px;'>{value}</td>"
                )
            table_html += "</tr>"

        table_html += "</table>"

        table_element = document.querySelector("#data-table")
        if table_element:
            table_element.innerHTML = table_html

    async def auto_refresh(self, interval_seconds=30):
        """Auto-refresh the dashboard every interval_seconds."""
        while True:
            await asyncio.sleep(interval_seconds)
            # Simulate new data point
            if self.data is not None:
                new_date = self.data["date"].max() + timedelta(days=1)
                new_sales = np.random.normal(self.data["sales"].tail(7).mean(), 100)
                new_customers = np.random.poisson(50)
                new_avg_order = new_sales / new_customers

                new_row = pd.DataFrame(
                    {
                        "date": [new_date],
                        "sales": [max(0, new_sales)],
                        "customers": [new_customers],
                        "avg_order_value": [new_avg_order],
                    }
                )

                self.data = pd.concat([self.data, new_row], ignore_index=True)
                self.update_data_summary()
                self.create_chart()
                print(f"Dashboard auto-refreshed at {datetime.now()}")


# Initialize dashboard when PyScript loads
dashboard = DataDashboard()

# Example of how to start auto-refresh (optional)
# asyncio.create_task(dashboard.auto_refresh(60))  # Refresh every minute

print("Interactive Dashboard initialized!")
print("Click 'Load Data' to see the dashboard in action.")
