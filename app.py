
import streamlit as st
from pathlib import Path
import html

st.set_page_config(
    page_title="BakeWise | Smarter Baking",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CONFIGURATION
# =========================================================

logo_path = Path(__file__).parent / "bakewise_logo.png"
is_logged_in = st.session_state.get("logged_in", False)

# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --cream: #FAF5ED;
        --paper: #FFFCF7;
        --brown: #482B20;
        --muted: #82695B;
        --terracotta: #A94327;
        --terracotta-dark: #84351F;
        --border: #E9DCCB;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 90% 0%, #F2DFCC 0%, transparent 35%),
            linear-gradient(180deg, #FAF5ED 0%, #F8F2E8 100%);
        color: var(--brown);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(250, 245, 237, 0.88);
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }

    h1, h2, h3 {
        color: var(--brown) !important;
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.8px;
    }

    p {
        color: #71594B;
        line-height: 1.7;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #F0E5D6;
        border-right: 1px solid #E4D3C0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--brown) !important;
    }

    section[data-testid="stSidebar"] a {
        border-radius: 10px;
    }

    /* Hero */
    .hero-shell {
        background: rgba(255, 252, 247, 0.78);
        border: 1px solid #E9D7C3;
        border-radius: 25px;
        padding: 27px;
        box-shadow: 0 15px 45px rgba(87, 52, 32, 0.055);
        margin-bottom: 22px;
    }

    .eyebrow {
        color: var(--terracotta);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .hero-tag {
        display: inline-block;
        background: #F5E7D8;
        color: #98452D;
        border: 1px solid #EAD2BE;
        padding: 7px 11px;
        border-radius: 100px;
        font-size: 0.67rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 16px;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: clamp(2rem, 3vw, 2.85rem);
        font-weight: 800;
        letter-spacing: -1.8px;
        line-height: 1.12;
        color: #482B20;
        margin: 0 0 15px 0;
    }

    .hero-copy {
        color: #71594B;
        font-size: 0.98rem;
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .trust-line {
        color: #8C7462;
        font-size: 0.78rem;
        margin-top: 13px;
    }

    /* Feature cards */
    .feature-card {
        height: 100%;
        min-height: 160px;
        box-sizing: border-box;
        padding: 21px;
        background: rgba(255, 252, 247, 0.94);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 6px 20px rgba(87, 52, 32, 0.035);
    }

    .feature-icon {
        display: inline-flex;
        width: 42px;
        height: 42px;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: #F5E5D6;
        font-size: 20px;
        margin-bottom: 13px;
    }

    .feature-title {
        color: var(--brown);
        font-family: 'Manrope', sans-serif;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .feature-description {
        color: var(--muted);
        font-size: 0.86rem;
        line-height: 1.65;
    }

    /* Welcome panel */
    .welcome-panel {
        background: linear-gradient(120deg, #482B20, #75412E);
        padding: 26px 29px;
        border-radius: 20px;
        color: #FFF8EF;
        margin-bottom: 23px;
        box-shadow: 0 12px 28px rgba(72, 43, 32, 0.12);
    }

    .welcome-panel h2 {
        color: #FFF8EF !important;
        margin: 0 0 7px 0;
    }

    .welcome-panel p {
        color: #F1DCCD;
        margin-bottom: 0;
    }

    /* Buttons: explicit high contrast */
    div.stButton > button {
        min-height: 50px;
        border-radius: 12px;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.92rem;
        font-weight: 800;
        transition: all 0.18s ease;
    }

    div.stButton > button[kind="primary"] {
        background: #A94327 !important;
        color: #FFFFFF !important;
        border: 1px solid #A94327 !important;
        box-shadow: 0 5px 14px rgba(169, 67, 39, 0.17);
    }

    div.stButton > button[kind="primary"] p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #84351F !important;
        border-color: #84351F !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }

    div.stButton > button[kind="primary"]:hover p {
        color: #FFFFFF !important;
    }

    div.stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #84351F !important;
        border: 1px solid #A94327 !important;
    }

    div.stButton > button[kind="secondary"] p {
        color: #84351F !important;
        font-weight: 800 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: #F8EADF !important;
        border-color: #84351F !important;
        transform: translateY(-1px);
    }

    div[data-testid="stMetric"] {
        background: #FFFCF7;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 18px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: #E7D9C8;
    }

    .footer {
        text-align: center;
        color: #A18A78;
        font-size: 0.73rem;
        padding-top: 25px;
        letter-spacing: 1px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-shell {
            padding: 16px;
            border-radius: 18px;
        }

        .hero-title {
            font-size: 2rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# LANDING PAGE — LOGIN ACTIONS AT THE TOP
# =========================================================

if not is_logged_in:

    with st.container():
        st.markdown('<div class="hero-shell">', unsafe_allow_html=True)

        logo_col, content_col = st.columns(
            [1.05, 1],
            gap="large",
            vertical_alignment="center",
        )

        with logo_col:
            if logo_path.exists():
                st.image(
                    str(logo_path),
                    use_container_width=True,
                )
            else:
                st.markdown(
                    """
                    <h1 style="text-align:center;color:#482B20;">
                        BakeWise
                    </h1>
                    """,
                    unsafe_allow_html=True,
                )
                st.warning(
                    "Place bakewise_logo.png beside app.py "
                    "to display your logo."
                )

        with content_col:
            st.markdown(
                """
                <div class="hero-tag">
                    ✦ INTELLIGENT BAKERY PLANNING
                </div>

                <div class="hero-title">
                    Your next great bake starts with a smarter decision.
                </div>

                <div class="hero-copy">
                    Forecast demand, plan production, and reduce
                    unnecessary waste with AI-powered insights
                    built for your bakery.
                </div>
                """,
                unsafe_allow_html=True,
            )

            login_col, account_col = st.columns(
                2,
                gap="small",
            )

            with login_col:
                if st.button(
                    "Sign In  →",
                    type="primary",
                    use_container_width=True,
                    key="hero_sign_in",
                ):
                    st.switch_page("pages/login.py")

            with account_col:
                if st.button(
                    "Create Account",
                    type="secondary",
                    use_container_width=True,
                    key="hero_create_account",
                ):
                    st.switch_page("pages/login.py")

            st.markdown(
                '<div class="trust-line">'
                'Your bakery workspace starts here.'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # FEATURES
    # =====================================================

    st.markdown(
        '<div class="eyebrow">BUILT FOR BETTER BAKING</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h2 style="font-size:1.9rem;margin:0 0 8px 0;">
            Less guesswork. More great bakes.
        </h2>

        <p style="max-width:760px;margin-bottom:22px;">
            Make production planning more informed, consistent,
            and data-driven with tools designed around your bakery.
        </p>
        """,
        unsafe_allow_html=True,
    )

    feature1, feature2, feature3 = st.columns(3, gap="medium")

    with feature1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🔮</div>
                <div class="feature-title">Predict demand</div>
                <div class="feature-description">
                    Use historical sales patterns and demand
                    signals to plan what to prepare.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🌾</div>
                <div class="feature-title">Reduce waste</div>
                <div class="feature-description">
                    Make more informed production decisions
                    and avoid unnecessary overproduction.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Learn from sales</div>
                <div class="feature-description">
                    Track actual demand and build a stronger
                    foundation for future forecasts.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="footer">
            BAKEWISE &nbsp;•&nbsp; SMARTER BAKING, BETTER DECISIONS
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LOGGED-IN WORKSPACE
# =========================================================

else:

    name = html.escape(
        str(st.session_state.get("user_name", "there"))
    )

    st.markdown(
        f"""
        <div class="welcome-panel">
            <div class="eyebrow" style="color:#F1B99C;">
                YOUR BAKERY WORKSPACE
            </div>
            <h2>Welcome back, {name} 👋</h2>
            <p>
                Your bakery, your numbers, your next great batch.
                Let's make today count.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="eyebrow">YOUR CONTROL CENTRE</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Everything you need to bake smarter.")

    st.write(
        "Use the sidebar to access demand forecasts, daily "
        "production entries, your bakery profile, and model "
        "management."
    )

    st.write("")

    feature1, feature2, feature3 = st.columns(3, gap="medium")

    with feature1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Demand forecasting</div>
                <div class="feature-description">
                    Estimate upcoming demand and plan production
                    with more confidence.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🥐</div>
                <div class="feature-title">Daily production</div>
                <div class="feature-description">
                    Record production and sales to understand
                    what your customers actually buy.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">Model management</div>
                <div class="feature-description">
                    Manage your forecasting workflow as your
                    bakery's data grows.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.divider()

    left, right = st.columns([3, 1])

    with left:
        st.caption(
            "Keep recording actual demand to compare forecasts "
            "against real bakery performance."
        )

    with right:
        if st.button(
            "Log Out  ↗",
            type="secondary",
            use_container_width=True,
        ):
            st.session_state["logged_in"] = False
            st.session_state.pop("user_email", None)
            st.session_state.pop("user_name", None)
            st.rerun()
