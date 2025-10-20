# backend/app/utils/plots.py
"""
Plot utilities - Convert matplotlib figures to base64 strings.
"""
import base64
from io import BytesIO
import matplotlib.pyplot as plt


def fig_to_base64(fig: plt.Figure) -> str:
    """
    Convert a matplotlib figure to base64-encoded PNG string.
    
    TODO: Add error handling for invalid figures
    TODO: Support different output formats (PNG, SVG)
    TODO: Add compression options for large plots
    
    Args:
        fig: Matplotlib figure object
        
    Returns:
        Base64-encoded string of the PNG image
        
    Example:
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        base64_str = fig_to_base64(fig)
        # Use in HTML: <img src="data:image/png;base64,{base64_str}" />
    """
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    return image_base64