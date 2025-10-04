# app_current_state.py
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Current State: Vendor Cloud Silos", layout="wide")

st.title("Current State of Radiology Imaging Data")
st.caption("Each vendor cloud is its own silo with archives and data spread across them. "
           "Radiologists must know *which vendor cloud* to search in, making priors hard to find.")

# Vendors
vendors = [
    "GE Healthcare Cloud",
    "Philips HealthSuite",
    "Agfa Enterprise Imaging",
    "Sectra PACS Cloud",
    "Merative (Merge) Cloud",
    "Ambra Health Cloud",
    "Life Image Exchange"
]

# Create graph
G = nx.Graph()

# Add vendor nodes
for v in vendors:
    G.add_node(v, type="vendor")

# Add some patient studies randomly distributed
patients = [f"Study {i}" for i in range(1, 16)]
for p in patients:
    v = random.choice(vendors)
    G.add_node(p, type="study")
    G.add_edge(p, v)

# Draw the graph
fig, ax = plt.subplots(figsize=(12, 8))

pos = nx.spring_layout(G, seed=42, k=1.5)

vendor_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "vendor"]
study_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "study"]

nx.draw_networkx_nodes(G, pos, nodelist=vendor_nodes, node_size=2500, node_color="#4A90E2", alpha=0.9, ax=ax)
nx.draw_networkx_nodes(G, pos, nodelist=study_nodes, node_size=800, node_color="#F5A623", alpha=0.8, ax=ax)
nx.draw_networkx_edges(G, pos, width=2, alpha=0.4, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=10, font_color="white", ax=ax)

st.pyplot(fig)

st.markdown("""
### Key Problem
- Each vendor has **its own cloud archive**.  
- Patient studies are scattered across **GE, Philips, Agfa, Sectra, Merative, Ambra, Life Image**, etc.  
- To find priors, radiologists must **know which vendor** the study lives in.  
- This fragmentation leads to **delays, duplicate scans, and inefficiency**.
""")
