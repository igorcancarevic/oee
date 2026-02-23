import streamlit as st
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="OEE Profit Leak Analyzer | The Value Stack", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# Title & Context
st.title("🏭 OEE & Profit Leak Analyzer")
st.markdown("""
### Stop measuring percentages, start measuring money.
*Notes from the field by Igor Čančarević*

In most factories, Overall Equipment Effectiveness (OEE) is treated as a dry technical KPI. But for an economist in an engineer's shoes, OEE is a **financial diagnostic tool**. Every 1% lost is money leaking from your balance sheet.
""")

# Sidebar Inputs
st.sidebar.header("🛠️ Production Parameters")

with st.sidebar:
    st.subheader("Financial Context")
    unit_price = st.number_input("Profit per Good Unit (€)", value=10.0, step=1.0)
    
    st.subheader("Shift Logistics")
    planned_time = st.number_input("Planned Production Time (min)", value=480, help="Total shift time minus planned breaks.")
    downtime = st.number_input("Unplanned Downtime (min)", value=60, help="Breakdowns, setup times, or waiting for materials.")
    
    st.subheader("Engineering Specs")
    ideal_cycle_time = st.number_input("Ideal Cycle Time (sec/unit)", value=5.0, help="The theoretical fastest time to produce one unit.")
    total_units = st.number_input("Total Units Produced (inc. scrap)", value=4500)
    good_units = st.number_input("Good Units (Quality Output)", value=4300)

# 1. The Math (The Engine)
actual_runtime = planned_time - downtime
availability = actual_runtime / planned_time if planned_time > 0 else 0

# Performance calculation
ideal_run_rate = 60 / (ideal_cycle_time / 60) 
performance = (total_units * ideal_cycle_time) / (actual_runtime * 60) if actual_runtime > 0 else 0
performance = min(performance, 1.0) # Caps it at 100% for realistic visualization

# Quality calculation
quality = good_units / total_units if total_units > 0 else 0

# OEE calculation
oee = availability * performance * quality

# 2. The Economics (The Profit Leak)
potential_units = (planned_time * 60) / ideal_cycle_time
lost_units = potential_units - good_units
profit_leak = lost_units * unit_price

# 3. UI - Metrics Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall OEE", f"{oee:.1%}")
col2.metric("Availability", f"{availability:.1%}")
col3.metric("Performance", f"{performance:.1%}")
col4.metric("Quality", f"{quality:.1%}")

st.divider()

# 4. Visualization
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = oee * 100,
    title = {'text': "OEE Score (%)", 'font': {'size': 24}},
    gauge = {
        'axis': {'range': [None, 100], 'tickwidth': 1},
        'bar': {'color': "#1f77b4"},
        'steps': [
            {'range': [0, 40], 'color': "#ff4b4b"},
            {'range': [40, 75], 'color': "#ffa500"},
            {'range': [75, 100], 'color': "#00cc96"}],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': 85} # World Class Benchmark
    }
))

c1, c2 = st.columns([2, 1])
with c1:
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.error(f"### 💸 Total Profit Leak: €{profit_leak:,.2f}")
    st.write(f"""
    **Why is this happening?**
    During this shift, you failed to capture **{int(lost_units)} potential units**. 
    
    At €{unit_price} profit per unit, your breakdown of loss is:
    - **Availability Loss:** {downtime} minutes of idle machines.
    - **Performance Loss:** Running at {performance:.1%}, likely due to minor stops or slow cycles.
    - **Quality Loss:** {total_units - good_units} units of scrap material.
    """)

st.info("💡 **Value Stack Perspective:** Improving OEE by just 5% often yields more profit than buying a brand new production line. Optimization is the highest-margin activity in your business.")
