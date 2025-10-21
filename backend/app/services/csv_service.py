# backend/app/services/csv_service.py
"""
CSV analysis service using pandas + Google Gemini AI.
Provides intelligent data analysis with visualizations.
"""
import pandas as pd
import io
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import Dict
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    logger.info("✅ Gemini client configured for CSV analysis")
else:
    client = None
    logger.warning("⚠️ GOOGLE_API_KEY not configured for CSV analysis")


async def analyze_csv(csv_content: str, prompt: str) -> Dict:
    """
    Analyze CSV data using pandas + Gemini AI.
    """
    try:
        # Try robust CSV parsing with multiple fallback strategies
        df = _parse_csv_robust(csv_content)
        
        logger.info(f"📊 CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info(f"📋 Columns: {', '.join(df.columns.tolist())}")
        
        prompt_lower = prompt.lower()
        
        # Handle specific requests
        if any(word in prompt_lower for word in ["plot", "histogram", "chart", "graph", "visualize"]):
            summary, plot = _generate_plot(df, prompt)
            return {"summary": summary, "plot_base64": plot}
        
        elif "summarize" in prompt_lower or "summary" in prompt_lower or "overview" in prompt_lower:
            summary = _generate_summary(df)
            return {"summary": summary, "plot_base64": None}
        
        elif "stat" in prompt_lower or "statistics" in prompt_lower:
            summary = _generate_statistics(df)
            return {"summary": summary, "plot_base64": None}
        
        elif "missing" in prompt_lower or "null" in prompt_lower:
            summary = _analyze_missing_values(df)
            return {"summary": summary, "plot_base64": None}
        
        else:
            # Use Gemini AI for custom analysis
            summary = await _ai_analyze_csv(df, prompt)
            return {"summary": summary, "plot_base64": None}
        
    except Exception as e:
        logger.error(f"❌ CSV analysis error: {e}")
        return {
            "summary": f"⚠️ Error analyzing CSV: {str(e)}",
            "plot_base64": None
        }


def _parse_csv_robust(csv_content: str) -> pd.DataFrame:
    """
    Robust CSV parser that tries multiple strategies.
    """
    # Strategy 1: Standard parsing
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        logger.info("✅ CSV parsed successfully (standard)")
        return df
    except Exception as e1:
        logger.warning(f"Standard parsing failed: {e1}")
    
    # Strategy 2: Skip bad lines
    try:
        df = pd.read_csv(
            io.StringIO(csv_content),
            on_bad_lines='skip',
            engine='python'
        )
        logger.info("✅ CSV parsed (skipped bad lines)")
        return df
    except Exception as e2:
        logger.warning(f"Skip bad lines failed: {e2}")
    
    # Strategy 3: Try different separators
    for sep in [',', ';', '\t', '|']:
        try:
            df = pd.read_csv(
                io.StringIO(csv_content),
                sep=sep,
                on_bad_lines='skip',
                engine='python'
            )
            if df.shape[1] > 1:  # Valid if more than one column
                logger.info(f"✅ CSV parsed (separator: '{sep}')")
                return df
        except:
            continue
    
    # Strategy 4: Last resort - very lenient parsing
    try:
        df = pd.read_csv(
            io.StringIO(csv_content),
            on_bad_lines='skip',
            engine='python',
            encoding_errors='ignore',
            quoting=3  # QUOTE_NONE
        )
        logger.info("✅ CSV parsed (lenient mode)")
        return df
    except Exception as e4:
        logger.error(f"All parsing strategies failed: {e4}")
        raise Exception(f"Could not parse CSV file. Please ensure it's a valid CSV format.")


def _generate_summary(df: pd.DataFrame) -> str:
    """Generate basic summary of the dataset."""
    try:
        summary_parts = [
            "## 📊 Dataset Summary\n",
            f"**Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns\n",
            f"**Columns:** {', '.join(df.columns.tolist())}\n",
            "\n### Sample Data (First 5 Rows)\n",
            "```",
            df.head().to_string(),
            "```\n",
            "\n### Data Types\n",
            "```",
            df.dtypes.to_string(),
            "```"
        ]
        
        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def _generate_statistics(df: pd.DataFrame) -> str:
    """Generate statistical summary."""
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_cols:
            return "⚠️ No numeric columns found in the dataset."
        
        stats = df[numeric_cols].describe()
        
        summary_parts = [
            "## 📈 Statistical Summary\n",
            f"**Numeric Columns:** {len(numeric_cols)}\n",
            "\n```",
            stats.to_string(),
            "```"
        ]
        
        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error generating statistics: {str(e)}"


def _analyze_missing_values(df: pd.DataFrame) -> str:
    """Analyze missing values in the dataset."""
    try:
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        
        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing Values': missing.values,
            'Percentage': missing_pct.values.round(2)
        })
        
        missing_df = missing_df[missing_df['Missing Values'] > 0].sort_values('Missing Values', ascending=False)
        
        if len(missing_df) == 0:
            return "## ✅ Data Quality\n\n**No missing values found!** The dataset is complete."
        
        summary_parts = [
            "## 🔍 Missing Values Analysis\n",
            f"**Total Columns with Missing Data:** {len(missing_df)}\n",
            f"**Total Missing Values:** {int(missing_df['Missing Values'].sum()):,}\n",
            "\n### Detailed Breakdown\n",
            "```",
            missing_df.to_string(index=False),
            "```"
        ]
        
        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error analyzing missing values: {str(e)}"


async def _ai_analyze_csv(df: pd.DataFrame, prompt: str) -> str:
    """Use Gemini AI to analyze CSV."""
    if not client:
        return _pandas_fallback_analysis(df, prompt)
    
    try:
        data_summary = f"""Analyze this dataset:

Shape: {df.shape[0]:,} rows × {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}

Data Types:
{df.dtypes.to_string()}

First 10 Rows:
{df.head(10).to_string()}

Statistics:
{df.describe().to_string()}

Question: {prompt}

Provide clear analysis with markdown formatting.
"""
        
        logger.info(f"🤖 Calling Gemini for CSV analysis...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=data_summary
        )
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"❌ Gemini error: {e}")
        return _pandas_fallback_analysis(df, prompt)


def _pandas_fallback_analysis(df: pd.DataFrame, prompt: str) -> str:
    """Fallback analysis."""
    return f"""## 📊 Dataset Overview

**Rows:** {df.shape[0]:,}
**Columns:** {df.shape[1]}
**Names:** {', '.join(df.columns.tolist())}

### Quick Statistics
```
{df.describe().to_string()}
```
"""


def _generate_plot(df: pd.DataFrame, prompt: str) -> tuple:
    """Generate visualization."""
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_cols:
            return ("⚠️ No numeric columns available for plotting.", None)
        
        # Choose column to plot
        col_to_plot = numeric_cols[0]
        for col in df.columns:
            if col.lower() in prompt.lower() and col in numeric_cols:
                col_to_plot = col
                break
        
        logger.info(f"📊 Generating plot for column: {col_to_plot}")
        
        # Create histogram
        plt.figure(figsize=(10, 6))
        data = df[col_to_plot].dropna()
        
        plt.hist(data, bins=min(30, len(data.unique())), edgecolor='black', alpha=0.7, color='#2E86AB')
        plt.title(f'Distribution of {col_to_plot}', fontsize=14, fontweight='bold')
        plt.xlabel(col_to_plot, fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        summary = f"""## 📊 Histogram: {col_to_plot}

**Statistics:**
- Count: {len(data):,} values
- Mean: {data.mean():.2f}
- Median: {data.median():.2f}
- Std Dev: {data.std():.2f}
- Min: {data.min():.2f}
- Max: {data.max():.2f}

The histogram below shows the distribution of values.
"""
        
        return (summary, plot_base64)
        
    except Exception as e:
        logger.error(f"❌ Plot error: {e}")
        return (f"⚠️ Error generating plot: {str(e)}", None)
