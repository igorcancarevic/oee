import streamlit as st
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="OEE Profit Leak Analyzer | The Value Stack", layout="wide")

# Title & Brand Intro
st.title("🏭 OEE & Profit Leak Analyzer")
st.markdown("""
*Insights by Igor Čančarević*

In the world of high-stakes manufacturing, OEE (Overall Equipment Effectiveness) is the ultimate metric for efficiency. 
But to truly move the needle, we must translate these percentages into the language of business: **Cash Flow.**
""")

st.divider()

# Sidebar for User Inputs
st.sidebar.header("🛠️ Input Parameters")

with st.sidebar:
    st.subheader("1. Financial Context")
    unit_price = st.number_input("Profit per Good Unit (€)", value=15.0, step=1.0)
    
    st.subheader("2. Time & Downtime")
    planned_time = st.number_input("Planned Production Time (min)", value=480, help="Shift length minus planned breaks.")
    downtime = st.number_input("Unplanned Downtime (min)", value=45, help="Breakdowns, setups, or waiting for materials.")
    
    st.subheader("3. Production Data")
    ideal_cycle_time = st.number_input("Ideal Cycle Time (sec/unit)", value=4.5, help="The theoretical fastest time to produce one unit.")
    total_units = st.number_input("Total Units Produced (inc. scrap)", value=5200)
    good_units = st.number_input("Good Units (Quality Output)", value=5000)

# --- THE CALCULATIONS ---

# A: Availability
actual_runtime = planned_time - downtime
availability = actual_runtime / planned_time if planned_time > 0 else 0

# P: Performance
# Performance = (Ideal Cycle Time * Total Count) / Run Time
performance = (total_units * ideal_cycle_time) / (actual_runtime * 60) if actual_runtime > 0 else 0
performance = min(performance, 1.0) # Caps at 100% for visualization

# Q: Quality
quality = good_units / total_units if total_units > 0 else 0

# OEE Result
oee = availability * performance * quality

# Financials: The Profit Leak
theoretical_max_output = (planned_time * 60) / ideal_cycle_time
lost_units = theoretical_max_output - good_units
profit_leak = lost_units * unit_price

# --- UI DISPLAY ---

# Dashboard Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Overall OEE", f"{oee:.1%}")
m2.metric("Availability (A)", f"{availability:.1%}")
m3.metric("Performance (P)", f"{performance:.1%}")
m4.metric("Quality (Q)", f"{quality:.1%}")

st.divider()

# Visualization & Summary
c1, c2 = st.columns([2, 1])

with c1:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = oee * 100,
        title = {'text': "Current OEE Score (%)", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 60], 'color': "#ffcccb"},
                {'range': [60, 85], 'color': "#fff4cc"},
                {'range': [85, 100], 'color': "#d1f2eb"}],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': 85} # World Class Benchmark
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.error(f"### 💸 Total Profit Leak: €{profit_leak:,.2f}")
    st.markdown(f"""
    **Analysis for this shift:**
    * **Lost Opportunity:** {int(lost_units)} units that could have been sold.
    * **Primary Bottleneck:** { "Downtime" if availability < performance and availability < quality else "Speed Loss" if performance < quality else "Quality Defects" }
    
    *Pragmatic view: Every minute of downtime cost you €{ (theoretical_max_output/planned_time) * unit_price :.2f}.*
    """)

# --- THE EDUCATIONAL SECTION (The Math) ---
st.divider()
with st.expander("📝 The Value Stack Methodology: How we calculate this"):
    st.write("To understand where value is lost, we break the production process into three distinct layers:")
    
    st.latex(r"OEE = \text{Availability} \times \text{Performance} \times \text{Quality}")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.subheader("1. Availability")
        st.write("Measures losses due to unplanned stops.")
        st.latex(r"A = \frac{\text{Planned Time} - \text{Downtime}}{\text{Planned Time}}")
        
    with col_b:
        st.subheader("2. Performance")
        st.write("Measures losses due to running slower than the ideal speed.")
        st.latex(r"P = \frac{\text{Total Units} \times \text{Ideal Cycle Time}}{\text{Actual Run Time}}")
        
    with col_c:
        st.subheader("3. Quality")
        st.write("Measures losses due to scrap and rework.")
        st.latex(r"Q = \frac{\text{Good Units}}{\text{Total Units Produced}}")

    st.markdown("---")
    st.subheader("The Economic Calculation (Profit Leak)")
    st.write("We don't just look at what happened; we look at the **Opportunity Cost**. We compare your actual good output against the theoretical maximum output of the planned time.")
    st.latex(r"\text{Profit Leak} = \left( \frac{\text{Planned Time}}{\text{Ideal Cycle Time}} - \text{Good Units} \right) \times \text{Profit per Unit}")

st.info("💡 **Pro-Tip:** Don't chase 100%. In many industries, the cost of reaching 100% OEE is higher than the profit it generates. Aim for 'World Class' (85%) and then optimize for stability.")
