# Indian Cities Route Optimizer & Dijkstra's Visualization

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0.0-brightgreen)

## Overview

This project is a web application that allows users to find the shortest path between Indian cities using Dijkstra's algorithm. It provides a visualization of the algorithm's process and displays the optimal route on an interactive map.

## Features

- **Route Optimization**: Calculate the shortest path between two cities.
- **Interactive Map**: Visualize the route on a map using Folium.
- **Graph Visualization**: View and interact with the graph representation of cities and routes.
- **Save & Load Graphs**: Save and load custom graphs for future use.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/indian-route-optimizer.git
   cd indian-route-optimizer
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Streamlit app:**

   ```bash
   streamlit run route_optimization.py
   ```

2. **Open your browser** and go to `http://localhost:8501` to view the app.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [Folium](https://python-visualization.github.io/folium/)
- [NetworkX](https://networkx.org/)

## Contact

For any questions or suggestions, please contact [dev.dhruvin.0.1@gmail.com](mailto:yourname@example.com).
