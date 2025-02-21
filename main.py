import streamlit as st
import pandas as pd
import zipfile
import io
from api_handler import validate_api_key, get_samples
from data_processor import process_sample_data
import time

st.set_page_config(
    page_title="Arboreal Data Downloader",
    page_icon="🌲",
    layout="wide"
)

st.title("🌲 Arboreal Data Downloader")

st.markdown("""
This application allows you to download data from the Arboreal API. 
Simply enter your API key and click the download button to receive your data as a ZIP file.
""")

# API Key input
api_key = st.text_input("Enter your Arboreal API Key", type="password", 
                        help="Your API key should start with 'Key '")

if st.button("Download Data", disabled=not api_key):
    if not validate_api_key(api_key):
        st.error("Invalid API key format. The key should start with 'Key '")
    else:
        try:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Fetch samples
            status_text.text("Fetching sample data...")
            progress_bar.progress(10)
            
            samples_df = get_samples(api_key)
            if samples_df is None:
                st.error("Failed to fetch samples. Please check your API key and try again.")
                st.stop()
                
            progress_bar.progress(30)
            status_text.text("Processing sample data...")
            
            # Process the data
            dfs = process_sample_data(api_key, samples_df, status_text, progress_bar)
            
            if dfs is None:
                st.error("Failed to process sample data")
                st.stop()
            
            progress_bar.progress(90)
            status_text.text("Creating ZIP file...")
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add each DataFrame to the ZIP as a CSV
                for name, df in dfs.items():
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    zip_file.writestr(f"{name}.csv", csv_buffer.getvalue())
            
            progress_bar.progress(100)
            status_text.text("Download ready!")
            
            # Offer the ZIP file for download
            st.download_button(
                label="📥 Download ZIP File",
                data=zip_buffer.getvalue(),
                file_name="arboreal_data.zip",
                mime="application/zip"
            )
            
            # Display summary
            st.success(f"""
            Download package contains:
            - {len(dfs['Samples'])} sample plots
            - {len(dfs['Trees'])} trees
            - {len(dfs['Stems'])} stems
            - {len(dfs['Heights'])} height measurements
            - {len(dfs['Calculations'])} calculations
            """)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
