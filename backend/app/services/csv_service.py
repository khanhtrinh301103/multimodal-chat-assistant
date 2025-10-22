# backend/app/services/csv_service.py
"""
CSV analysis service using pandas + Claude 3.5 Sonnet AI.
Clean, simple, relies on AI intelligence for flexibility.
"""
import pandas as pd
import io
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import asyncio
from io import BytesIO
from typing import Dict, List
import anthropic
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
from app.models.dto import CsvChatMessage

load_dotenv()
logger = logging.getLogger(__name__)

# Claude configuration for free-tier accounts
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
if ANTHROPIC_API_KEY:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    logger.info("✅ Claude Haiku 3.5 configured for CSV analysis")
else:
    client = None
    logger.warning("⚠️ ANTHROPIC_API_KEY not configured for CSV analysis")

# Use available model from your Free Tier plan
MODEL_NAME = "claude-3-5-haiku-latest"  # Free-tier model, fast and light
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
MAX_TOKENS = 4096




# ============================================
# IN-MEMORY SESSION STORAGE
# ============================================
csv_sessions = {}


def _generate_session_id() -> str:
    """Generate unique session ID"""
    return f"csv_{uuid.uuid4().hex[:12]}"


# ============================================
# AI HELPER WITH RETRY LOGIC
# ============================================

async def _call_ai_with_retry(prompt: str) -> str:
    """
    Call Claude AI with automatic retry on failures.
    """
    if not client:
        return _simple_fallback_message()
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"🤖 Claude 3.5 Sonnet: Attempt {attempt + 1}/{MAX_RETRIES}")
            
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            logger.info("✅ Claude response received successfully")
            return message.content[0].text.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Claude error (attempt {attempt + 1}): {error_msg}")
            
            # Check if it's a retryable error (529, rate_limit, overloaded)
            is_retryable = any(code in error_msg for code in ["529", "overloaded", "rate_limit", "500", "503"])
            
            if is_retryable and attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue
            
            # If not retryable or last attempt, use fallback
            logger.warning("⚠️ All retries exhausted, using simple fallback")
            return _simple_fallback_message()
    
    return _simple_fallback_message()


def _simple_fallback_message() -> str:
    """Simple fallback when AI is unavailable"""
    return """I'm currently unable to connect to the AI service. However, I can still help you with basic operations:

Try asking:
- "Show me statistics"
- "What columns have missing values?"
- "Show me the first 10 rows"

Or wait a moment and try your question again."""


# ============================================
# SESSION MANAGEMENT FUNCTIONS
# ============================================

async def create_csv_session(
    csv_content: str,
    source_type: str,
    source_value: str,
    initial_message: str
) -> Dict:
    """Create a new CSV chat session."""
    try:
        df = _parse_csv_robust(csv_content)
        session_id = _generate_session_id()
        
        csv_info = {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "source_type": source_type,
            "source_value": source_value
        }
        
        # Get AI's initial response with retry
        initial_analysis = await _ai_initial_analysis(df, initial_message)
        
        conversation_history = [
            CsvChatMessage(role="user", content=initial_message, timestamp=datetime.now()),
            CsvChatMessage(role="assistant", content=initial_analysis, timestamp=datetime.now())
        ]
        
        csv_sessions[session_id] = {
            "df": df,
            "csv_content": csv_content,
            "conversation_history": conversation_history,
            "csv_info": csv_info,
            "created_at": datetime.now()
        }
        
        logger.info(f"✅ Created session: {session_id} ({df.shape[0]} rows, {df.shape[1]} cols)")
        
        return {
            "session_id": session_id,
            "message": f"CSV loaded successfully! {df.shape[0]} rows and {df.shape[1]} columns.",
            "csv_info": csv_info
        }
        
    except Exception as e:
        logger.error(f"❌ Session creation failed: {e}")
        raise Exception(f"Failed to create session: {str(e)}")


async def chat_with_csv(session_id: str, user_message: str) -> Dict:
    """Continue conversation in an existing CSV session."""
    session = csv_sessions.get(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    
    df = session["df"]
    conversation_history = session["conversation_history"]
    
    try:
        user_msg = CsvChatMessage(role="user", content=user_message, timestamp=datetime.now())
        conversation_history.append(user_msg)
        
        logger.info(f"💬 Processing message: {user_message[:50]}...")
        
        # Check if user wants a plot
        needs_plot = any(word in user_message.lower() for word in [
            "plot", "graph", "chart", "visualize", "histogram", "show distribution"
        ])
        
        if needs_plot:
            analysis, plot_base64 = await _ai_analyze_with_plot(df, user_message, conversation_history[:-1])
            assistant_msg = CsvChatMessage(
                role="assistant",
                content=analysis,
                plot_base64=plot_base64,
                timestamp=datetime.now()
            )
            conversation_history.append(assistant_msg)
            
            return {
                "session_id": session_id,
                "reply": analysis,
                "plot_base64": plot_base64,
                "conversation_history": conversation_history
            }
        else:
            analysis = await _ai_conversational_analysis(df, user_message, conversation_history[:-1])
            assistant_msg = CsvChatMessage(role="assistant", content=analysis, timestamp=datetime.now())
            conversation_history.append(assistant_msg)
            
            return {
                "session_id": session_id,
                "reply": analysis,
                "plot_base64": None,
                "conversation_history": conversation_history
            }
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise Exception(f"Chat failed: {str(e)}")


def get_session_info(session_id: str) -> Dict:
    """Get information about a session."""
    session = csv_sessions.get(session_id)
    if not session:
        return None
    
    return {
        "session_id": session_id,
        "csv_info": session["csv_info"],
        "conversation_history": session["conversation_history"],
        "created_at": session["created_at"].isoformat()
    }


# ============================================
# AI ANALYSIS FUNCTIONS
# ============================================

async def _ai_initial_analysis(df: pd.DataFrame, initial_message: str) -> str:
    """AI generates initial analysis/overview of the CSV."""
    prompt = f"""You are a helpful data analysis assistant. A user has just uploaded a CSV file.

Dataset Information:
- Rows: {df.shape[0]:,}
- Columns: {df.shape[1]}
- Column Names: {', '.join(df.columns.tolist())}

Data Types:
{df.dtypes.to_string()}

First 5 Rows:
{df.head().to_string()}

Statistical Summary:
{df.describe().to_string()}

User's Initial Message: "{initial_message}"

Provide a friendly, informative overview. Include:
1. Brief summary of what the data contains
2. Key observations
3. Suggestions for analyses

Use markdown formatting."""
    
    return await _call_ai_with_retry(prompt)


async def _ai_conversational_analysis(
    df: pd.DataFrame,
    user_message: str,
    conversation_history: List[CsvChatMessage]
) -> str:
    """AI analyzes CSV with full conversation context."""
    context = _build_conversation_context(conversation_history)
    
    prompt = f"""You are a helpful data analysis assistant having a conversation about a CSV dataset.

Dataset Information:
- Rows: {df.shape[0]:,}
- Columns: {df.shape[1]}
- Column Names: {', '.join(df.columns.tolist())}

Data Sample:
{df.head(10).to_string()}

Statistical Summary:
{df.describe().to_string()}

Previous Conversation:
{context}

User's Current Question: "{user_message}"

Analyze the data and answer the user's question. Consider:
1. Conversation history - reference previous questions if relevant
2. Be specific with numbers and examples from actual data
3. If asked to compare or find patterns, do thorough analysis
4. Use markdown formatting
5. Be conversational and friendly

Provide a clear, detailed response."""
    
    return await _call_ai_with_retry(prompt)


async def _ai_analyze_with_plot(
    df: pd.DataFrame,
    user_message: str,
    conversation_history: List[CsvChatMessage]
) -> tuple:
    """AI analyzes and generates a plot based on user request."""
    try:
        plot_base64 = await _generate_smart_plot(df, user_message)
        
        if not plot_base64:
            return ("⚠️ Could not generate the requested plot.", None)
        
        context = _build_conversation_context(conversation_history)
        
        prompt = f"""You've created a visualization for the user.

Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}

Previous Conversation:
{context}

User's Request: "{user_message}"

A visualization has been created. Provide:
1. Brief description of what the plot shows
2. Key insights or patterns
3. Interesting observations

Keep it concise. Use markdown."""
        
        analysis = await _call_ai_with_retry(prompt)
        return (analysis, plot_base64)
        
    except Exception as e:
        logger.error(f"❌ Plot generation error: {e}")
        return (f"⚠️ Error generating plot: {str(e)}", None)


async def _generate_smart_plot(df: pd.DataFrame, user_message: str) -> str:
    """Intelligently generate plot based on user request."""
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return None
        
        # Detect column
        column_to_plot = None
        for col in df.columns:
            if col.lower() in user_message.lower() and col in numeric_cols:
                column_to_plot = col
                break
        
        if not column_to_plot:
            column_to_plot = numeric_cols[0]
        
        logger.info(f"📊 Creating plot for: {column_to_plot}")
        
        plt.figure(figsize=(10, 6))
        data = df[column_to_plot].dropna()
        
        # Choose plot type
        if any(word in user_message.lower() for word in ["scatter", "correlation"]) and len(numeric_cols) >= 2:
            plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6)
            plt.xlabel(numeric_cols[0])
            plt.ylabel(numeric_cols[1])
            plt.title(f'Scatter: {numeric_cols[0]} vs {numeric_cols[1]}')
        elif any(word in user_message.lower() for word in ["line", "trend"]):
            plt.plot(data.values, linewidth=2)
            plt.xlabel('Index')
            plt.ylabel(column_to_plot)
            plt.title(f'Trend: {column_to_plot}')
        else:
            plt.hist(data, bins=min(30, len(data.unique())), edgecolor='black', alpha=0.7)
            plt.xlabel(column_to_plot)
            plt.ylabel('Frequency')
            plt.title(f'Distribution of {column_to_plot}')
        
        plt.grid(axis='y', alpha=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return plot_base64
        
    except Exception as e:
        logger.error(f"❌ Plot error: {e}")
        return None


def _build_conversation_context(history: List[CsvChatMessage]) -> str:
    """Build conversation context string."""
    if not history:
        return "No previous conversation."
    
    context_parts = []
    for msg in history[-5:]:
        role = "User" if msg.role == "user" else "Assistant"
        context_parts.append(f"{role}: {msg.content}")
    
    return "\n".join(context_parts)


# ============================================
# UTILITIES
# ============================================

def _parse_csv_robust(csv_content: str) -> pd.DataFrame:
    """Robust CSV parser with multiple strategies."""
    try:
        return pd.read_csv(io.StringIO(csv_content))
    except:
        pass
    
    try:
        return pd.read_csv(io.StringIO(csv_content), on_bad_lines='skip', engine='python')
    except:
        pass
    
    for sep in [',', ';', '\t', '|']:
        try:
            df = pd.read_csv(io.StringIO(csv_content), sep=sep, on_bad_lines='skip', engine='python')
            if df.shape[1] > 1:
                return df
        except:
            continue
    
    raise Exception("Could not parse CSV file")


# ============================================
# BACKWARD COMPATIBILITY (Original endpoints)
# ============================================

async def analyze_csv(csv_content: str, prompt: str) -> Dict:
    """Single-shot CSV analysis (backward compatible)."""
    try:
        df = _parse_csv_robust(csv_content)
        
        ai_prompt = f"""Analyze this CSV dataset:

Shape: {df.shape[0]:,} rows × {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}

Data Types:
{df.dtypes.to_string()}

First 10 Rows:
{df.head(10).to_string()}

Statistics:
{df.describe().to_string()}

Question: {prompt}

Provide clear analysis with markdown formatting."""
        
        summary = await _call_ai_with_retry(ai_prompt)
        return {"summary": summary, "plot_base64": None}
        
    except Exception as e:
        logger.error(f"❌ CSV analysis error: {e}")
        return {"summary": f"⚠️ Error: {str(e)}", "plot_base64": None}