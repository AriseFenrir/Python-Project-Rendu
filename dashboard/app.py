import os
import time

import httpx
import pandas as pd
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")

st.set_page_config(page_title="DevOps Monitor", layout="wide")
st.title("DevOps Monitoring Dashboard")

auto_refresh = st.sidebar.toggle("Auto-refresh", value=True)

tab_metrics, tab_servers = st.tabs(["Metrics", "Servers"])

with tab_metrics:
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = []

    try:
        response = httpx.get(f"{API_BASE_URL}/metrics", timeout=5)
        data = response.json()
        st.session_state.metrics_history.append(data)
        st.session_state.metrics_history = st.session_state.metrics_history[-60:]
    except Exception:
        data = None
        st.warning("Could not connect to API")

    if data:
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU", f"{data['cpu_percent']:.1f}%")
        col2.metric("Memory", f"{data['memory_percent']:.1f}%")
        col3.metric("Disk", f"{data['disk_percent']:.1f}%")

        if len(st.session_state.metrics_history) > 1:
            df = pd.DataFrame(st.session_state.metrics_history)
            st.line_chart(df[["cpu_percent", "memory_percent", "disk_percent"]])

with tab_servers:
    try:
        response = httpx.get(f"{API_BASE_URL}/servers", timeout=5)
        server_list = response.json()
    except Exception:
        server_list = []
        st.warning("Could not connect to API")

    if server_list:
        df = pd.DataFrame(server_list)

        def color_status(val):
            colors = {
                "UP": "background-color: #28a745; color: white",
                "DOWN": "background-color: #dc3545; color: white",
                "DEGRADED": "background-color: #ffc107; color: black",
                "UNKNOWN": "background-color: #6c757d; color: white",
            }
            return colors.get(val, "")

        styled = df.style.map(color_status, subset=["status"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.info("No servers registered yet")

    st.subheader("Register a Server")
    with st.form("add_server"):
        name = st.text_input("Server Name")
        host = st.text_input("Host")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8000)
        submitted = st.form_submit_button("Register")
        if submitted and name and host:
            try:
                resp = httpx.post(
                    f"{API_BASE_URL}/servers",
                    json={"name": name, "host": host, "port": int(port)},
                    headers={"X-API-Key": API_KEY},
                    timeout=5,
                )
                if resp.status_code == 201:
                    st.success(f"Server '{name}' registered!")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

if auto_refresh:
    time.sleep(1)
    st.rerun()
