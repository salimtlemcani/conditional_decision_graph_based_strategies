# Trading Strategy Builder

Welcome to the **Trading Strategy Builder**, a Streamlit-based application that allows users to create, visualize, and 
run custom trading strategies using a decision tree approach. This tool integrates with the SigTech platform to execute 
strategies and analyze their performance.

It specialises in path-dependant strategies (`sig.DynamicStrategy`) based on conditions set by indicators (such as RSI, cumulative returns and 
others).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Manage Conditions](#manage-conditions)
  - [Manage Actions](#manage-actions)
  - [View Specifications](#view-specifications)
  - [Visualize Decision Tree](#visualize-decision-tree)
  - [My Strategies](#my-strategies)
- [Project Structure](#project-structure)
- [Customization](#customization)
- [License](#license)

## Features

- **Interactive GUI**: Use Streamlit to interactively manage conditions and actions for your trading strategy.
- **Decision Tree Visualization**: Visualize your strategy's decision tree using Graphviz.
- **Strategy Execution**: Run your strategy using historical data through the SigTech platform.
- **Performance Analysis**: View and analyze the performance of your strategies with customizable plots.
- **Strategy Management**: Save and load multiple strategies for comparison and further analysis.

## Installation

### Prerequisites

- Python 3.7 or higher
- [SigTech Python Framework](https://sigtech.com/)
- Required Python packages listed in `requirements.txt`

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/salimtlemcani/conditional_decision_graph_based_strategies.git
   cd conditional_decision_graph_based_strategies
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up SigTech Environment**

   - Ensure you have access to the SigTech platform.

[//]: # (   - Configure your API keys and environment variables as per SigTech's documentation.)

## Getting Started

1. **Navigate to the Project Directory**

   ```bash
   cd conditional_decision_graph_based_strategies
   ```

2. **Run the Streamlit Application**

   ```bash
   streamlit run app.py
   ```

3. **Access the App**

   - Open your web browser and go to the localhost port shown in your console (likely `http://localhost:8501`)

## Usage

The application is divided into several sections accessible from the sidebar:

### Manage Conditions

- **Add New Condition**: Define new conditions based on indicators like RSI, Volatility, or Cumulative Return.
- **Edit Existing Conditions**: Modify or update existing conditions.

### Manage Actions

- **Add New Action**: Define new actions specifying ETF allocations.
- **Edit Existing Actions**: Modify or update existing actions.

### View Specifications

- **Conditions**: View all defined conditions in JSON format.
- **Actions**: View all defined actions in JSON format.
- **Download Specifications**: Download conditions and actions as JSON files.

### Visualize Decision Tree

- **Decision Tree Visualization**: Generate and view the decision tree based on your conditions and actions using Graphviz.

### My Strategies

- **Run New Strategy**: Execute your strategy over a specified date range and initial cash amount.
- **View Saved Strategies**: View and analyze the performance of saved strategies.

## Project Structure

```
conditional_decision_graph_based_strategies/
├── app.py                   # Main Streamlit application
├── strategy_builder.py      # Builds the decision tree from specifications
├── strategy_execution.py    # Contains the basket creation method
├── helper.py                # Utility functions for indicators and comparisons
├── conditions.json          # JSON file storing condition specifications
├── actions.json             # JSON file storing action specifications
├── strategies/              # Directory to store saved strategy objects
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Customization

- **Indicators**: Extend `helper.py` to include additional financial indicators as needed.
- **ETFs**: Modify the list of ETFs in `app.py` to include those relevant to your strategies.
- **Visualization**: Customize the plotting functions in `app.py` to adjust the appearance of performance graphs.

---

*Note: This application requires access to the SigTech platform. Ensure you have the necessary permissions and 
credentials to use their services.*