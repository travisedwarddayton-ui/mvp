if mode == "Overview":
    section_header("Nursing Informatics: Why It Matters", "From early computers to mobile health and AI", "📘")

    st.write("""
    Nursing Informatics (NI) is not just about computers — it’s about **improving how nurses think, document, and care** 
    using information and technology. Every nurse today, whether in a rural clinic or teaching hospital, interacts with data daily.

    Learning NI helps you:
    - **Make better decisions**: Turn raw observations into insights that guide patient care.
    - **Save time and reduce errors**: Learn how good data entry, standardized terms, and usability design make care safer.
    - **Improve communication**: Use digital tools to connect with other healthcare workers, labs, and patients faster.
    - **Stay relevant**: Modern hospitals expect nurses to work with EHRs, mobile apps, and AI-assisted devices.
    - **Advance your career**: Informatics is now a recognized nursing specialty with global demand for data-savvy nurses.
    - **Strengthen local healthcare**: Nigerian nurses using open-source and low-cost digital tools can bridge resource gaps and lead innovation.
    """)

    col1, col2 = st.columns([1,1])
    with col1:
        section_header("Learning Objectives", icon="🎯")
        bullet([
            "Recall major time periods and milestones in NI.",
            "Differentiate system software, utilities, and applications.",
            "Explain DIKW and where nursing tasks fit in the data pipeline.",
            "Recognize EHR usability principles and patient portal roles.",
            "Identify use-cases for wearables, mHealth, and open-source tools.",
            "Understand how informatics supports safer, smarter nursing."
        ])
    with col2:
        section_header("Why It Matters in Nigeria", icon="🌍")
        bullet([
            "Healthcare facilities are moving toward digital record keeping.",
            "Mobile-based mHealth tools are already used in community care.",
            "Low-cost open-source systems (like OpenMRS) need nurse leadership.",
            "AI and data skills are becoming essential for nursing research and management.",
            "Nurses with informatics knowledge can improve both patient safety and documentation quality."
        ])
    tag_pills(["HIT", "EHR", "mHealth", "Open Source", "DIKW", "Usability", "Career Growth", "Patient Safety"])
