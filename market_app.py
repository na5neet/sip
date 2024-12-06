import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuration: List of markets and parameters (can be loaded from a config file)
MARKETS = ['Diu','Karnataka','Maharashtra','Odisha','Meghalaya','Uttar Pradesh','Daman','Himachal Pradesh','Arunachal Pradesh','Haryana','Delhi','West Bengal','Goa','Silvassa','Jharkhand','Jammu & Kashmir','Assam','Mumbai','Chandigarh','Sikkim','Madhya Pradesh','Pondicherry','Punjab','Tripura','Uttranchal','Rajasthan','Kerala','Telangana','Tamil Nadu']
PARAMETERS = ['Total Volume','Segment Volume (Premium / Mainstream, Economy)','Brand Volume','Pack Volume','SKU Volume','Multi-brand Volume','Total State Volume Achievement','Segment level state volume achievement','Total Region Volume Achievement','Segment level Region volume achievement','Net contribution Total','Net contribution for a segment','NC / Case at a category level','NC / Case at a region level','NC / Case at a brand level','NC / Case at a SKU level','NC / Case at a Brand Portfolio level','NC / Case at a state level','Volume Growth','Value Growth','Segment volume growth','Brand volume growth','Net Contribution growth','Brand Distribution','SKU Distribution','PICOS adherence','SKU / Outlet','Increase of SKU / Outlet (+1, +2)','Facings of a brand','Cold facing (MSL)','Warm facing (MSL)','POSM Deployment','Cooler Deployment','Draught Distribution','Absolute Market Share','Market share gain','Total Cooler Purity','Premium Purity','Qualifier 1 (Visits)','Qualifier 2 (Outlet coverage)','Menu Card availability (Brand wise)','Menu Card Price proper indexing']

# Data storage for user session
if 'user_data' not in st.session_state:
    st.session_state.user_data = {market: {param: {"JTSE": {"100%": "", "115%": ""}, "Executive": {"100%": "", "115%": ""}} for param in PARAMETERS} for market in MARKETS}

# Streamlit app
def main():

    st.markdown("<h1 style='text-align: center;'>Build Your SIP</h1>", unsafe_allow_html=True)

    # Subtitle for Market selection
    st.subheader("Market")
    selected_market = st.selectbox("Select Market", MARKETS)

    # Multi-select box for parameter selection
    st.subheader("Select Parameters to Enter Weightage")
    selected_parameters = st.multiselect("Select Parameters", PARAMETERS)

    # Weightage input for selected parameters with tabs for JTSE and Executive
    if selected_parameters:
        st.subheader("Enter Weightage for Selected Parameters")
        tabs = st.tabs(["JTSE", "Executive"])

        for group, tab in zip(["JTSE", "Executive"], tabs):
            with tab:
                with st.form(key=f"weightage_form_{group}"):
                    weightage_data = []
                    for parameter in selected_parameters:
                        col1, col2, col3 = st.columns([2, 2, 2])
                        with col1:
                            st.write(parameter)
                        with col2:
                            weight_100 = st.text_input(f"100% Achievement for {parameter}", key=f"{selected_market}_{parameter}_{group}_100", value=st.session_state.user_data[selected_market][parameter][group]["100%"])
                            st.session_state.user_data[selected_market][parameter][group]["100%"] = weight_100
                        with col3:
                            weight_115 = st.text_input(f"115% Achievement for {parameter}", key=f"{selected_market}_{parameter}_{group}_115", value=st.session_state.user_data[selected_market][parameter][group]["115%"])
                            st.session_state.user_data[selected_market][parameter][group]["115%"] = weight_115
                    submit_button = st.form_submit_button(label="Update Data")

    # Show current data matrix with filter option
    st.subheader("Your Selection")
    data = []
    for market, params in st.session_state.user_data.items():
        for param, groups in params.items():
            for group, weightages in groups.items():
                data.append({"Market": market, "Parameter": param, "Group": group, "100% Achievement": weightages["100%"], "115% Achievement": weightages["115%"]})
    df_display = pd.DataFrame(data)
    if not df_display.empty:
        df_display.index += 1  # Make row numbers start from 1
        # Adding filtering capability
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            selected_market_filter = st.selectbox("Filter by Market", ["All"] + MARKETS)
        with col2:
            selected_parameter_filter = st.selectbox("Filter by Parameter", ["All"] + PARAMETERS)
        with col3:
            selected_group_filter = st.selectbox("Filter by Group", ["All", "JTSE", "Executive"])

        if selected_market_filter != "All":
            df_display = df_display[df_display["Market"] == selected_market_filter]
        if selected_parameter_filter != "All":
            df_display = df_display[df_display["Parameter"] == selected_parameter_filter]
        if selected_group_filter != "All":
            df_display = df_display[df_display["Group"] == selected_group_filter]

        st.dataframe(df_display, use_container_width=True)

    # Submit button
    if st.button("Submit All Data"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"user_selections_{timestamp}.csv"
        df_to_save = pd.DataFrame([{"Market": market, "Parameter": param, "Group": group, "100% Achievement": weightages["100%"], "115% Achievement": weightages["115%"]} 
                                   for market, params in st.session_state.user_data.items() 
                                   for param, groups in params.items()
                                   for group, weightages in groups.items() if weightages["100%"] or weightages["115%"]])
        df_to_save.to_csv(csv_file, index=False)
        st.success(f"All data has been saved successfully to {csv_file}!")

if __name__ == "__main__":
    main()
