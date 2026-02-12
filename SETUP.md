# Setup Guide

## Quick Setup (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/counterfactual-quantum-communication.git
cd counterfactual-quantum-communication
```

### 2. Create Virtual Environment (Recommended)
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n qcomm python=3.10
conda activate qcomm
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Simulation
```bash
python counterfactual_simulation.py
```

**Expected output:**
- Console output with measurement statistics
- `counterfactual_results.png` saved to current directory

### 5. Generate Network Diagrams
```bash
python network_visualization.py
```

**Expected output:**
- `network_visualization.png`
- `schematic_diagram.png`

## Verification

Check that everything works:

```bash
# Should print simulation results
python counterfactual_simulation.py

# Should create visualization files
ls -l *.png
```

## Google Colab (No Installation Required)

Upload the notebooks to Google Colab:

1. Go to [Google Colab](https://colab.research.google.com/)
2. Upload `counterfactual_simulation.py`
3. Add at the top:
   ```python
   !pip install qiskit qiskit-aer matplotlib
   ```
4. Run all cells

## Jupyter Notebook

```bash
# Install Jupyter
pip install jupyter

# Create notebook
jupyter notebook

# In notebook:
!pip install qiskit qiskit-aer matplotlib
```

Then copy code from `.py` files into cells.

## Troubleshooting

### Issue: Module not found
```bash
pip install --upgrade qiskit qiskit-aer
```

### Issue: Matplotlib backend error
Add to top of script:
```python
import matplotlib
matplotlib.use('Agg')
```

### Issue: Permission denied
```bash
chmod +x counterfactual_simulation.py
```

## Running on IBM Quantum Hardware

1. Create account at [quantum-computing.ibm.com](https://quantum-computing.ibm.com/)
2. Get your API token
3. Add to script:
```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(channel="ibm_quantum", token="YOUR_TOKEN")
backend = service.least_busy(operational=True, simulator=False)
```

## System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- Any OS (Windows, macOS, Linux)

**Recommended:**
- Python 3.10+
- 4GB+ RAM
- Modern CPU (simulation is CPU-intensive)

## Next Steps

- Read the [README.md](README.md) for theory and usage
- Check [examples/](examples/) for sample outputs
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/counterfactual-quantum-communication/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/counterfactual-quantum-communication/discussions)
- **Email:** your.email@example.com
