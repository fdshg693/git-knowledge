# PyScript Basic Usage and Configuration

## Installation and Setup

### 1. CDN Integration (Recommended for Beginners)

The simplest way to get started with PyScript is using the CDN:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My PyScript App</title>
    
    <!-- PyScript CSS -->
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    
    <!-- PyScript JS -->
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
</head>
<body>
    <h1>Hello PyScript!</h1>
    
    <!-- Python code block -->
    <py-script>
        print("Hello from Python!")
    </py-script>
</body>
</html>
```

### 2. Local Installation

For development and offline use:

```bash
# Download PyScript files
wget https://github.com/pyscript/pyscript/releases/download/2024.1.1/pyscript-2024.1.1.tar.gz
tar -xzf pyscript-2024.1.1.tar.gz

# Or clone the repository
git clone https://github.com/pyscript/pyscript.git
```

### 3. Package Manager Integration

```bash
# Using npm
npm install @pyscript/core

# Using yarn
yarn add @pyscript/core
```

## Core HTML Tags

### 1. `<py-script>` Tag

Executes Python code when the page loads:

```html
<py-script>
    import datetime
    
    current_time = datetime.datetime.now()
    print(f"Page loaded at: {current_time}")
    
    # Access DOM elements
    from pyscript import document
    heading = document.querySelector("h1")
    heading.innerText = "Updated by Python!"
</py-script>
```

### 2. `<py-repl>` Tag

Creates an interactive Python REPL:

```html
<py-repl auto-generate="true"></py-repl>
```

### 3. `<py-config>` Tag

Configures PyScript environment:

```html
<py-config>
    packages = ["numpy", "matplotlib", "pandas"]
    
    [[files]]
    "./data.py" = """
def process_data():
    return "Processed data"
    """
</py-config>
```

## Configuration Options

### 1. Package Management

```html
<py-config>
    # Standard packages from PyPI
    packages = [
        "numpy",
        "pandas", 
        "matplotlib",
        "requests",
        "pillow"
    ]
    
    # Custom packages with versions
    packages = [
        "numpy==1.24.3",
        "pandas>=1.5.0",
        "matplotlib"
    ]
</py-config>
```

### 2. Loading External Python Files

```html
<py-config>
    [[files]]
    "./utils.py" = """
def helper_function():
    return "Helper result"
    """
    
    "./config.py" = """
API_KEY = "your-api-key"
DEBUG = True
    """
</py-config>
```

### 3. Terminal Configuration

```html
<py-config>
    [terminal]
    auto-generate = true
    docked = true
</py-config>
```

### 4. Interpreter Settings

```html
<py-config>
    [interpreter]
    src = "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"
    name = "pyodide-0.24.1"
    lang = "python"
</py-config>
```

## Environment Setup Patterns

### 1. Development Environment

```html
<py-config>
    # Development packages
    packages = ["numpy", "pandas", "matplotlib", "seaborn"]
    
    # Enable terminal for debugging
    [terminal]
    auto-generate = true
    docked = true
    
    # Development-specific files
    [[files]]
    "./debug.py" = """
import sys
import traceback

def debug_info():
    print(f"Python version: {sys.version}")
    print(f"Available modules: {sys.modules.keys()}")
    """
</py-config>

<py-script>
    from debug import debug_info
    debug_info()
</py-script>
```

### 2. Data Science Environment

```html
<py-config>
    packages = [
        "numpy",
        "pandas", 
        "matplotlib",
        "seaborn",
        "plotly",
        "scikit-learn"
    ]
    
    [[files]]
    "./data_utils.py" = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_sample_data():
    return pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100)
    })
    
def create_plot(data):
    plt.figure(figsize=(10, 6))
    plt.scatter(data['x'], data['y'])
    plt.title('Sample Data Plot')
    return plt
    """
</py-config>
```

### 3. Production Environment

```html
<py-config>
    # Minimal packages for production
    packages = ["requests"]
    
    # Disable terminal in production
    [terminal]
    auto-generate = false
    
    # Production configuration
    [[files]]
    "./config.py" = """
PRODUCTION = True
API_ENDPOINT = "https://api.production.com"
CACHE_ENABLED = True
    """
</py-config>
```

## Loading Strategies

### 1. Lazy Loading

```html
<py-script>
    # Only import when needed
    def load_heavy_packages():
        import numpy as np
        import pandas as pd
        return np, pd
    
    # Use on demand
    def process_data():
        np, pd = load_heavy_packages()
        # Process with packages
</py-script>
```

### 2. Progressive Enhancement

```html
<!-- Basic functionality first -->
<py-script>
    print("Basic functionality loaded")
</py-script>

<!-- Enhanced features after basic load -->
<py-script>
    import asyncio
    
    async def load_advanced_features():
        # Load heavy packages asynchronously
        import numpy as np
        import matplotlib.pyplot as plt
        print("Advanced features loaded")
    
    # Run after basic setup
    asyncio.create_task(load_advanced_features())
</py-script>
```

### 3. Modular Configuration

```html
<py-config>
    # Base configuration
    packages = ["requests"]
    
    [[files]]
    "./base.py" = """
# Core functionality
def api_call(endpoint):
    import requests
    return requests.get(endpoint)
    """
    
    "./advanced.py" = """
# Advanced features (loaded conditionally)
def data_analysis():
    try:
        import pandas as pd
        import numpy as np
        # Advanced analysis
    except ImportError:
        print("Advanced packages not available")
    """
</py-config>
```

## Performance Optimization

### 1. Selective Package Loading

```html
<py-config>
    # Only load what you need
    packages = ["numpy"]  # Instead of full scipy stack
</py-config>
```

### 2. Code Splitting

```html
<!-- Critical code first -->
<py-script>
    # Essential functionality
    def core_function():
        return "Core result"
</py-script>

<!-- Non-critical code later -->
<py-script>
    # Optional enhancements
    def optional_feature():
        return "Optional result"
</py-script>
```

### 3. Caching Configuration

```html
<py-config>
    [interpreter]
    # Enable caching for faster subsequent loads
    cache = true
</py-config>
```

## Common Configuration Patterns

### 1. Multi-page Application

```html
<!-- shared-config.html -->
<py-config>
    packages = ["numpy", "pandas"]
    
    [[files]]
    "./shared.py" = """
# Shared utilities across pages
def format_data(data):
    return data.to_string()
    """
</py-config>
```

### 2. Widget-based Layout

```html
<py-config>
    packages = ["matplotlib"]
    
    [[files]]
    "./widgets.py" = """
class DataWidget:
    def __init__(self, container_id):
        self.container = container_id
    
    def render(self, data):
        # Render widget
        pass
    """
</py-config>
```

This configuration guide provides the foundation for setting up PyScript in various scenarios, from simple experiments to complex applications.
