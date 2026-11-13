import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Smart XI | Pressure Performance", page_icon="🏏", layout="wide")

NAVY = "#0B132B"
PANEL = "#14213D"
TEAL = "#2EC4B6"
GOLD = "#F4B942"
WHITE = "#FFFFFF"
MUTED = "#C7D0E0"

st.markdown(f"""
<style>
.stApp {{ background: {NAVY}; color: {WHITE}; }}
[data-testid="stSidebar"] {{ background: #101B35; }}
h1,h2,h3,h4,p,li,label {{ color: {WHITE} !important; }}
[data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid #30415F; padding: 15px; border-radius: 12px; }}
[data-testid="stMetricLabel"] p {{ color: {MUTED} !important; font-size: 0.95rem !important; }}
[data-testid="stMetricValue"] {{ color: {WHITE} !important; }}
div[data-testid="stDataFrame"] {{ background: {PANEL}; }}
.stTabs [data-baseweb="tab"] {{ color: {WHITE}; }}
.small-note {{ color: {MUTED}; font-size: 0.9rem; }}
hr {{ border-color: #30415F; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = Path(__file__).parent / "SmartXI_Analysis.xlsx"
    xls = pd.ExcelFile(path)
    return {s: pd.read_excel(path, sheet_name=s) for s in xls.sheet_names}

D = load_data()
bat = D["Top10_Batters"].copy()
bowl = D["Top10_Bowlers"].copy()
all_bat = D["All_Eligible_Batters"].copy()
all_bowl = D["All_Eligible_Bowlers"].copy()

def fmt(df, percent_cols=(), decimals=2):
    out = df.copy()
    for c in percent_cols:
        if c in out:
            out[c] = out[c].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
    return out

def style_fig(fig, height=430):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=NAVY, plot_bgcolor=PANEL,
        font=dict(color=WHITE, size=13), height=height,
        margin=dict(l=30,r=25,t=55,b=35),
        legend=dict(font=dict(color=WHITE)),
        title_font=dict(color=WHITE, size=19)
    )
    fig.update_xaxes(gridcolor="#30415F", zerolinecolor="#52627D")
    fig.update_yaxes(gridcolor="#30415F", zerolinecolor="#52627D")
    return fig

st.sidebar.title("🏏 SMART XI")
st.sidebar.caption("Context-aware player selection")
page = st.sidebar.radio("Navigate", [
    "Overview", "Top 10 Batters", "Top 10 Bowlers",
    "Player Comparison", "Pressure & Benchmarks", "Methodology & Reliability"
])
st.sidebar.markdown("---")
st.sidebar.caption("Source: SmartXI_Analysis.xlsx")
st.sidebar.caption("Rankings and metrics are read directly from the analysis workbook.")

if page == "Overview":
    st.title("SMART XI — Pressure Performance Dashboard")
    st.markdown("**A good player performs well, but a valuable player steps up when the team needs them the most.**")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Ranked batters", len(bat))
    c2.metric("Ranked bowlers", len(bowl))
    c3.metric("Eligible batters", len(all_bat))
    c4.metric("Eligible bowlers", len(all_bowl))
    st.markdown("---")
    left,right = st.columns(2)
    with left:
        st.subheader("Top 10 batter scores")
        f=px.bar(bat.sort_values("final_score", ascending=True), x="final_score", y="striker_name",
                 orientation="h", text="final_score", color_discrete_sequence=[TEAL],
                 labels={"final_score":"Final score","striker_name":"Batter"})
        f.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(style_fig(f, 470), use_container_width=True)
    with right:
        st.subheader("Top 10 bowler scores")
        f=px.bar(bowl.sort_values("final_score", ascending=True), x="final_score", y="bowler_name",
                 orientation="h", text="final_score", color_discrete_sequence=[GOLD],
                 labels={"final_score":"Final score","bowler_name":"Bowler"})
        f.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(style_fig(f, 470), use_container_width=True)
    st.info("This dashboard is an interactive companion to the PDF report. It uses the same workbook outputs; it does not independently recalculate or alter the rankings.")

elif page == "Top 10 Batters":
    st.title("Top 10 Batters")
    st.caption("Rankings and values below are read directly from the Top10_Batters worksheet.")
    cols = ["rank","striker_name","final_score","pressure_runs","pressure_balls","pressure_matches",
            "pressure_sr","normal_sr","adj_pressure_vs_normal","pressure_adj_runs_per100",
            "pressure_dismissal_rate","pressure_dot_pct","consistency_pct"]
    view=bat[cols].copy()
    view.columns=["Rank","Batter","Final score","Pressure runs","Pressure balls","Pressure matches",
                  "Pressure SR","Normal SR","Adjusted pressure vs normal","Adjusted surplus / 100 balls",
                  "Pressure dismissal rate","Pressure dot-ball %","Consistency %"]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.subheader("Pressure strike rate vs normal strike rate")
    long=bat.melt(id_vars="striker_name", value_vars=["pressure_sr","normal_sr"], var_name="Context", value_name="Strike rate")
    long["Context"]=long["Context"].map({"pressure_sr":"Pressure","normal_sr":"Normal"})
    f=px.bar(long, x="striker_name", y="Strike rate", color="Context", barmode="group",
             color_discrete_map={"Pressure":TEAL,"Normal":GOLD},
             labels={"striker_name":"Batter"})
    st.plotly_chart(style_fig(f,500), use_container_width=True)
    st.subheader("Adjusted pressure surplus per 100 balls")
    f=px.bar(bat.sort_values("pressure_adj_runs_per100", ascending=True), x="pressure_adj_runs_per100",
             y="striker_name", orientation="h", color_discrete_sequence=[TEAL],
             labels={"pressure_adj_runs_per100":"Adjusted surplus / 100 balls","striker_name":"Batter"})
    st.plotly_chart(style_fig(f,470), use_container_width=True)

elif page == "Top 10 Bowlers":
    st.title("Top 10 Bowlers")
    st.caption("Rankings and values below are read directly from the Top10_Bowlers worksheet.")
    cols=["rank","bowler_name","final_score","pressure_wickets","pressure_legal_balls","pressure_matches",
          "pressure_economy","normal_economy","pressure_wickets_per100","normal_wickets_per100",
          "pressure_econ_adv","pressure_wicket_adv","pressure_dot_adv_pp","all3_consistency_pct"]
    view=bowl[cols].copy()
    view.columns=["Rank","Bowler","Final score","Pressure wickets","Pressure legal balls","Pressure matches",
                  "Pressure economy","Normal economy","Pressure wickets / 100 balls","Normal wickets / 100 balls",
                  "Economy advantage","Wicket-rate advantage","Dot-ball advantage (pp)","All-three consistency %"]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.subheader("Pressure vs normal wicket rate")
    long=bowl.melt(id_vars="bowler_name", value_vars=["pressure_wickets_per100","normal_wickets_per100"],
                   var_name="Context", value_name="Wickets per 100 legal balls")
    long["Context"]=long["Context"].map({"pressure_wickets_per100":"Pressure","normal_wickets_per100":"Normal"})
    f=px.bar(long,x="bowler_name",y="Wickets per 100 legal balls",color="Context",barmode="group",
             color_discrete_map={"Pressure":TEAL,"Normal":GOLD},labels={"bowler_name":"Bowler"})
    st.plotly_chart(style_fig(f,500), use_container_width=True)
    st.subheader("Pressure economy advantage")
    f=px.bar(bowl.sort_values("pressure_econ_adv",ascending=True),x="pressure_econ_adv",y="bowler_name",
             orientation="h",color_discrete_sequence=[GOLD],
             labels={"pressure_econ_adv":"Economy advantage (runs per over)","bowler_name":"Bowler"})
    st.plotly_chart(style_fig(f,470),use_container_width=True)

elif page == "Player Comparison":
    st.title("Player Comparison")
    kind=st.radio("Player type",["Batters","Bowlers"],horizontal=True)
    if kind=="Batters":
        names=bat["striker_name"].tolist()
        a=st.selectbox("Select batter",names)
        b=st.selectbox("Compare with",names,index=1 if len(names)>1 else 0)
        rows=bat.set_index("striker_name").loc[[a,b]].reset_index()
        metrics=["final_score","pressure_sr","normal_sr","pressure_adj_runs_per100","pressure_dot_pct","consistency_pct"]
        labels=["Final score","Pressure strike rate","Normal strike rate","Adjusted surplus / 100 balls","Pressure dot-ball %","Consistency %"]
        st.dataframe(rows[["striker_name"]+metrics].rename(columns={"striker_name":"Batter","final_score":labels[0],
            "pressure_sr":labels[1],"normal_sr":labels[2],"pressure_adj_runs_per100":labels[3],
            "pressure_dot_pct":labels[4],"consistency_pct":labels[5]}),use_container_width=True,hide_index=True)
        chart=rows.melt(id_vars="striker_name",value_vars=["pressure_sr","normal_sr"],var_name="Context",value_name="Strike rate")
        chart["Context"]=chart["Context"].map({"pressure_sr":"Pressure","normal_sr":"Normal"})
        f=px.bar(chart,x="striker_name",y="Strike rate",color="Context",barmode="group",
                 color_discrete_map={"Pressure":TEAL,"Normal":GOLD})
        st.plotly_chart(style_fig(f),use_container_width=True)
    else:
        names=bowl["bowler_name"].tolist()
        a=st.selectbox("Select bowler",names)
        b=st.selectbox("Compare with",names,index=1 if len(names)>1 else 0)
        rows=bowl.set_index("bowler_name").loc[[a,b]].reset_index()
        cols=["bowler_name","final_score","pressure_economy","normal_economy","pressure_wickets_per100",
              "normal_wickets_per100","pressure_econ_adv","pressure_dot_adv_pp","all3_consistency_pct"]
        labels=["Bowler","Final score","Pressure economy","Normal economy","Pressure wickets / 100 balls",
                "Normal wickets / 100 balls","Economy advantage","Dot-ball advantage (pp)","All-three consistency %"]
        st.dataframe(rows[cols].set_axis(labels,axis=1),use_container_width=True,hide_index=True)
        chart=rows.melt(id_vars="bowler_name",value_vars=["pressure_wickets_per100","normal_wickets_per100"],
                        var_name="Context",value_name="Wickets per 100 legal balls")
        chart["Context"]=chart["Context"].map({"pressure_wickets_per100":"Pressure","normal_wickets_per100":"Normal"})
        f=px.bar(chart,x="bowler_name",y="Wickets per 100 legal balls",color="Context",barmode="group",
                 color_discrete_map={"Pressure":TEAL,"Normal":GOLD})
        st.plotly_chart(style_fig(f),use_container_width=True)

elif page == "Pressure & Benchmarks":
    st.title("Pressure & Benchmarks")
    st.subheader("How pressure deliveries are distributed")
    dist=D["Pressure_Distribution"].copy()
    f=px.bar(dist,x="pressure_reason",y="deliveries",text="pct",color_discrete_sequence=[TEAL],
             labels={"pressure_reason":"Pressure trigger","deliveries":"Deliveries","pct":"Share (%)"})
    f.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
    st.plotly_chart(style_fig(f),use_container_width=True)
    st.subheader("Pressure vs normal performance")
    pvn=D["Pressure_vs_Normal"].copy()
    if "pressure" in pvn.columns:
        pvn["Context"]=pvn["pressure"].astype(str).map({"True":"Pressure","False":"Normal","1":"Pressure","0":"Normal"})
    st.dataframe(pvn,use_container_width=True,hide_index=True)
    st.subheader("Context-specific pressure benchmarks")
    bench=D["Pressure_Benchmarks"].copy()
    st.dataframe(bench,use_container_width=True,hide_index=True)
    st.caption("Benchmarks are split by match format, innings, phase and wicket bucket where those fields are available.")

elif page == "Methodology & Reliability":
    st.title("Methodology & Reliability")
    st.subheader("Pressure definition")
    st.markdown("""
Pressure is identified from the match situation before a delivery. A delivery is treated as pressure when at least one of these conditions applies:
- **Collapse:** five or more wickets have already fallen.
- **End overs:** 30 or fewer scheduled legal balls remain.
- **Chase-rate pressure:** in the second innings, after 12 legal balls, required run rate is at least 2 runs per over above the current run rate.
- **Wicket-and-rate pressure:** in the second innings, after 12 legal balls, four or fewer wickets remain and required run rate is at least the current run rate.

The same pressure framework is used for batters and bowlers.
""")
    st.subheader("Workbook methodology notes")
    st.dataframe(D["Methodology"],use_container_width=True,hide_index=True)
    st.subheader("Data quality checks")
    st.dataframe(D["Data_Quality"],use_container_width=True,hide_index=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Batter confidence intervals")
        st.dataframe(D["Batter_CIs"],use_container_width=True,hide_index=True)
        st.subheader("Batter match consistency")
        st.dataframe(D["Batter_Match_Consistency"],use_container_width=True,hide_index=True)
    with c2:
        st.subheader("Bowler confidence intervals")
        st.dataframe(D["Bowler_CIs"],use_container_width=True,hide_index=True)
        st.subheader("Bowler match consistency")
        st.dataframe(D["Bowler_Match_Consistency"],use_container_width=True,hide_index=True)
    st.subheader("Sensitivity analysis")
    st.markdown("These sheets let reviewers inspect whether rankings or scores change under alternative pressure definitions and sample-weight settings.")
    st.dataframe(D["Pressure_Sensitivity"],use_container_width=True,hide_index=True)
    st.dataframe(D["Sample_Weight_Sensitivity"],use_container_width=True,hide_index=True)
    with st.expander("Additional audit sheets"):
        for sheet in ["Extras_Audit","Source_Version","Score_Reconciliation","Batter_Format_Split","Bowler_Format_Split","Pressure_Innings_Summary"]:
            st.markdown(f"**{sheet}**")
            st.dataframe(D[sheet],use_container_width=True,hide_index=True)

st.markdown("---")
st.markdown('<p class="small-note">Smart XI • Interactive presentation of the analysis workbook. Check the accompanying PDF for the written explanation and interpretation.</p>', unsafe_allow_html=True)
