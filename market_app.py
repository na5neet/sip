import streamlit as st
import pandas as pd
import os
from datetime import datetime
from write_to_storage_account import upload_dataframe_with_sas

# Configuration: List of markets and parameters (can be loaded from a config file)
CHANNELS = ['Retail', 'MONT']
MARKETS = ['Diu','Karnataka','Maharashtra','Odisha','Meghalaya','Uttar Pradesh','Daman','Himachal Pradesh','Arunachal Pradesh','Haryana','Delhi','West Bengal','Goa','Silvassa','Jharkhand','Jammu & Kashmir','Assam','Mumbai','Chandigarh','Sikkim','Madhya Pradesh','Pondicherry','Punjab','Tripura','Uttranchal','Rajasthan','Kerala','Telangana','Tamil Nadu']
PARAMETERS = ['Total Volume','Segment Volume (Premium / Mainstream, Economy)','Brand Volume','Pack Volume','SKU Volume','Multi-brand Volume','Total State Volume Achievement','Segment level state volume achievement','Total Region Volume Achievement','Segment level Region volume achievement','Net contribution Total','Net contribution for a segment','NC / Case at a category level','NC / Case at a region level','NC / Case at a brand level','NC / Case at a SKU level','NC / Case at a Brand Portfolio level','NC / Case at a state level','Volume Growth','Value Growth','Segment volume growth','Brand volume growth','Net Contribution growth','Brand Distribution','SKU Distribution','PICOS adherence','SKU / Outlet','Increase of SKU / Outlet (+1, +2)','Facings of a brand','Cold facing (MSL)','Warm facing (MSL)','POSM Deployment','Cooler Deployment','Draught Distribution','Absolute Market Share','Market share gain','Total Cooler Purity','Premium Purity','Qualifier 1 (Visits)','Qualifier 2 (Outlet coverage)','Menu Card availability (Brand wise)','Menu Card Price proper indexing']
DESIGNATIONS = ['ASM', 'ASE', 'STSE', 'TSE']

# Data storage for user session
if 'user_data' not in st.session_state:
    st.session_state.user_data = {market: {param: {"JTSE": {"100%": "", "115%": "", "Comments": "", "Channel": "", "Designation": ""}, "Executive": {"100%": "", "115%": "", "Comments": "", "Channel": "", "Designation": ""}} for param in PARAMETERS} for market in MARKETS}
    st.session_state.selected_channel = ""
    st.session_state.selected_designation = ""

# Function to load previous month data
def load_previous_month_data(selected_market, selected_parameters):
    today = datetime.now()
    first_day_this_month = datetime(today.year, today.month, 1)
    last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
    prev_month_folder = last_day_prev_month.strftime("%m%Y")

    if os.path.exists(prev_month_folder):
        previous_data = []
        for file in os.listdir(prev_month_folder):
            if file.endswith(".csv"):
                file_path = os.path.join(prev_month_folder, file)
                df = pd.read_csv(file_path)
                filtered_data = df[(df["Market"] == selected_market) & (df["Parameter"].isin(selected_parameters))]
                previous_data.append(filtered_data)
        if previous_data:
            return pd.concat(previous_data)
    return pd.DataFrame()

# Streamlit app
def main():
    current_month = datetime.now().strftime("%b-%Y")

    st.markdown(f"<h1 style='text-align: center;'>Build Your SIP</h1>", unsafe_allow_html=True)

    # Display tile for current SIP month
    st.markdown(f"<h3 style='text-align: left;'>SIP Month: {current_month}</h3>", unsafe_allow_html=True)

    # Subtitle for Market selection
    st.subheader("Market")
    selected_market = st.selectbox("Market", MARKETS)

    # Dropdown for Channel selection
    st.subheader("Channel")
    selected_channel = st.selectbox("Channel", CHANNELS)

    # Dropdown for Designation selection
    st.subheader("Designation")
    selected_designation = st.selectbox("Designation", DESIGNATIONS)

    # Multi-select box for parameter selection
    st.subheader("Select Parameters to Enter Weightage")
    selected_parameters = st.multiselect("Select Parameters", PARAMETERS)

    if not selected_market or not selected_parameters or not selected_channel or not selected_designation:
        st.error("Market, Channel, Designation, and Parameters selection are mandatory.")
        return

    # Load previous month data into the text inputs
    previous_data = load_previous_month_data(selected_market, selected_parameters)

    # Weightage input for selected parameters with tabs for JTSE and Executive
    if selected_parameters:
        st.subheader("Enter Weightage for Selected Parameters")
        st.markdown("<p style='font-size: 12px; color: gray;'>The numbers populated here are coming from the previous month selection.</p>", unsafe_allow_html=True)
        tabs = st.tabs(["JTSE", "Executive"])

        for group, tab in zip(["JTSE", "Executive"], tabs):
            with tab:
                with st.form(key=f"weightage_form_{group}"):
                    for parameter in selected_parameters:
                        # Fetch previous values if available
                        prev_100 = ""
                        prev_115 = ""
                        prev_comments = ""
                        if not previous_data.empty:
                            filtered = previous_data[(previous_data["Parameter"] == parameter) & (previous_data["Group"] == group)]
                            if not filtered.empty:
                                prev_100 = filtered.iloc[0]["100% Achievement"]
                                prev_115 = filtered.iloc[0]["115% Achievement"]
                                prev_comments = filtered.iloc[0].get("Comments", "")

                        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                        with col1:
                            st.write(parameter)
                        with col2:
                            weight_100 = st.number_input("100% Achievement", key=f"{selected_market}_{parameter}_{group}_100", value=float(prev_100) if prev_100 else 0.0, step=0.1, format="%.2f")
                            st.session_state.user_data[selected_market][parameter][group]["100%"] = weight_100
                        with col3:
                            weight_115 = st.number_input("115% Achievement", key=f"{selected_market}_{parameter}_{group}_115", value=float(prev_115) if prev_115 else 0.0, step=0.1, format="%.2f")
                            st.session_state.user_data[selected_market][parameter][group]["115%"] = weight_115
                        with col4:
                            comments = st.text_area("Additional Comments", key=f"{selected_market}_{parameter}_{group}_comments", value=prev_comments, help="Provide any additional comments (optional).")
                            st.session_state.user_data[selected_market][parameter][group]["Comments"] = comments

                        # Store the selected channel and designation for each parameter
                        st.session_state.user_data[selected_market][parameter][group]["Channel"] = selected_channel
                        st.session_state.user_data[selected_market][parameter][group]["Designation"] = selected_designation

                    submit_button = st.form_submit_button(label="Update Data")

    # Show current data matrix with filter option
    st.subheader("Your Selection")
    data = []
    for market, params in st.session_state.user_data.items():
        for param, groups in params.items():
            for group, weightages in groups.items():
                # Ensure 100% and 115% fields are numeric
                try:
                    weight_100 = float(weightages["100%"] if weightages["100%"] else 0.0)
                    weight_115 = float(weightages["115%"] if weightages["115%"] else 0.0)
                except ValueError:
                    weight_100, weight_115 = 0.0, 0.0  # Fallback for invalid values
                comments = weightages["Comments"] if weightages["Comments"] else ""
                channel = weightages["Channel"] if weightages["Channel"] else selected_channel
                designation = weightages["Designation"] if weightages["Designation"] else selected_designation

                data.append({
                    "Market": market,
                    "Parameter": param,
                    "Group": group,
                    "100% Achievement": weight_100,
                    "115% Achievement": weight_115,
                    "Comments": comments,
                    "Channel": channel,
                    "Designation": designation
                })

    # Convert data to DataFrame and enforce numeric types
    df_display = pd.DataFrame(data)
    if not df_display.empty:
        # Enforce numeric columns for compatibility
        df_display["100% Achievement"] = pd.to_numeric(df_display["100% Achievement"], errors='coerce').fillna(0.0)
        df_display["115% Achievement"] = pd.to_numeric(df_display["115% Achievement"], errors='coerce').fillna(0.0)

        df_display.index += 1  # Make row numbers start from 1

        # Adding filtering capability
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col1:
            selected_market_filter = st.selectbox("Market", ["All"] + MARKETS)
        with col2:
            selected_parameter_filter = st.selectbox("Parameter", ["All"] + PARAMETERS)
        with col3:
            selected_group_filter = st.selectbox("Group", ["All", "JTSE", "Executive"])
        with col4:
            selected_channel_filter = st.selectbox("Channel", ["All"] + CHANNELS)
        with col5:
            selected_designation_filter = st.selectbox("Designation", ["All"] + DESIGNATIONS)

        # Apply filters
        if selected_market_filter != "All":
            df_display = df_display[df_display["Market"] == selected_market_filter]
        if selected_parameter_filter != "All":
            df_display = df_display[df_display["Parameter"] == selected_parameter_filter]
        if selected_group_filter != "All":
            df_display = df_display[df_display["Group"] == selected_group_filter]
        if selected_channel_filter != "All":
            df_display = df_display[df_display["Channel"] == selected_channel_filter]
        if selected_designation_filter != "All":
            df_display = df_display[df_display["Designation"] == selected_designation_filter]

        st.dataframe(df_display, use_container_width=True)

    # Submit button
    if st.button("Submit All Data"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        month_folder = datetime.now().strftime("%m%Y")
        if not os.path.exists(month_folder):
            os.makedirs(month_folder)
        csv_file = os.path.join(month_folder, f"user_selections_{timestamp}.csv")
        df_to_save = pd.DataFrame([{"Market": market, "Parameter": param, "Group": group, "100% Achievement": weightages["100%"], "115% Achievement": weightages["115%"], "Comments": weightages["Comments"], "Channel": weightages["Channel"], "Designation": weightages["Designation"]} 
                                   for market, params in st.session_state.user_data.items() 
                                   for param, groups in params.items()
                                   for group, weightages in groups.items() if weightages["100%"] or weightages["115%"]])
        upload_dataframe_with_sas(df = df_to_save,file_name = csv_file)
        #df_to_save.to_csv(csv_file, index=False)
        st.success(f"All data has been saved successfully to {csv_file}!")

if __name__ == "__main__":
    main()
