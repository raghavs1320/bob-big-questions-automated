"""Ultra-minimalist, pure-white styling and typography for Daily Dose Studio."""

PURE_WHITE_CSS = """
<style>
    /* 1. Global Reset to Pure Clean White */
    .stApp {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif !important;
    }

    /* 2. Hide default Streamlit clutter (clean app look) */
    #MainMenu, footer, header {
        visibility: hidden;
    }

    /* 3. Header & Typography */
    .studio-header {
        text-align: center;
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .studio-title {
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: #111827 !important;
        margin-bottom: 0.3rem !important;
    }
    .studio-subtitle {
        font-size: 1.05rem !important;
        font-weight: 400 !important;
        color: #6B7280 !important;
        margin-bottom: 1.5rem !important;
    }

    /* 4. Minimalist White Cards */
    .studio-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px 0 rgba(0, 0, 0, 0.02);
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
    }

    /* 5. Big Action Button (Apple Pill Style) */
    div.stButton > button {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: 9999px !important;
        padding: 0.8rem 2.2rem !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #2563EB !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.25) !important;
    }

    /* 6. Friendly Status Progress Box */
    .status-box {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        font-size: 1.05rem;
        color: #1F2937;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* 7. Clean Form Inputs */
    .stSelectbox, .stRadio, .stFileUploader {
        color: #111827 !important;
    }
</style>
"""

