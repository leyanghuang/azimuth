import streamlit as st
import pandas as pd
import boto3
import io
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Azimuth Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎵 Azimuth Data Analysis Dashboard")
st.markdown("Interactive data exploration and visualization")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # AWS credentials
    st.subheader("AWS Credentials")
    access_key = st.text_input("AWS Access Key", type="password", key="access_key")
    secret_key = st.text_input("AWS Secret Key", type="password", key="secret_key")
    region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "eu-west-1"])
    
    bucket_name = "azimuth-venue-analysis"
    st.info(f"Bucket: {bucket_name}")

# Initialize S3 client
@st.cache_resource
def get_s3_client(access_key, secret_key, region):
    if not access_key or not secret_key:
        return None
    return boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

# List files from S3
@st.cache_data
def list_s3_files(s3_client, bucket, prefix):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if not key.endswith('/'):
                    files.append(key)
        return files
    except Exception as e:
        st.error(f"Error listing files: {e}")
        return []

# Read file from S3
@st.cache_data
def read_s3_file(s3_client, bucket, key):
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        
        if key.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(obj['Body'].read()))
        elif key.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(obj['Body'].read()))
        elif key.endswith('.json'):
            data = json.loads(obj['Body'].read().decode('utf-8'))
            df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        else:
            return None
        
        return df
    except Exception as e:
        st.error(f"Error reading file {key}: {e}")
        return None

# Main content
if not access_key or not secret_key:
    st.warning("⚠️ Please enter your AWS credentials in the sidebar to continue")
else:
    s3_client = get_s3_client(access_key, secret_key, region)
    
    if s3_client:
        st.success("✅ AWS connection successful!")
        
        # Tab navigation
        tab1, tab2, tab3, tab4 = st.tabs([
            "📁 Azimuth Venue Analysis",
            "🔄 Deduplicate Data",
            "📊 Untreated Data",
            "🔍 Data Explorer"
        ])
        
        # Tab 1: Azimuth Venue Analysis
        with tab1:
            st.subheader("Azimuth Venue Analysis Data")
            prefix1 = "Azimuth_Delivery/Azimuth_venue_analysis/"
            files1 = list_s3_files(s3_client, bucket_name, prefix1)
            
            if files1:
                selected_file1 = st.selectbox("Select file", files1, key="file1")
                
                if selected_file1:
                    df = read_s3_file(s3_client, bucket_name, selected_file1)
                    if df is not None:
                        st.info(f"📄 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Rows", df.shape[0])
                        with col2:
                            st.metric("Columns", df.shape[1])
                        
                        st.dataframe(df, use_container_width=True)
                        
                        # Basic statistics
                        st.subheader("Statistics")
                        st.dataframe(df.describe(), use_container_width=True)
                        
                        # Download option
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name=f"{selected_file1.split('/')[-1]}.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("No files found in this folder")
        
        # Tab 2: Deduplicate Data
        with tab2:
            st.subheader("Deduplicate Data")
            prefix2 = "Azimuth_Delivery/Deduplicate data/"
            files2 = list_s3_files(s3_client, bucket_name, prefix2)
            
            if files2:
                selected_file2 = st.selectbox("Select file", files2, key="file2")
                
                if selected_file2:
                    df = read_s3_file(s3_client, bucket_name, selected_file2)
                    if df is not None:
                        st.info(f"📄 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name=f"{selected_file2.split('/')[-1]}.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("No files found in this folder")
        
        # Tab 3: Untreated Data
        with tab3:
            st.subheader("Untreated Data")
            prefix3 = "Azimuth_Delivery/Untreated data/"
            files3 = list_s3_files(s3_client, bucket_name, prefix3)
            
            if files3:
                selected_file3 = st.selectbox("Select file", files3, key="file3")
                
                if selected_file3:
                    df = read_s3_file(s3_client, bucket_name, selected_file3)
                    if df is not None:
                        st.info(f"📄 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name=f"{selected_file3.split('/')[-1]}.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("No files found in this folder")
        
        # Tab 4: Data Explorer (Advanced)
        with tab4:
            st.subheader("Advanced Data Explorer")
            
            all_prefixes = [
                "Azimuth_Delivery/Azimuth_venue_analysis/",
                "Azimuth_Delivery/Deduplicate data/",
                "Azimuth_Delivery/Untreated data/"
            ]
            
            all_files = []
            for prefix in all_prefixes:
                files = list_s3_files(s3_client, bucket_name, prefix)
                all_files.extend(files)
            
            if all_files:
                selected_file = st.selectbox("Select any file to explore", all_files, key="file_explorer")
                
                if selected_file:
                    df = read_s3_file(s3_client, bucket_name, selected_file)
                    if df is not None:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Rows", len(df))
                        with col2:
                            st.metric("Total Columns", len(df.columns))
                        with col3:
                            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                        
                        # Data preview
                        st.subheader("Data Preview")
                        st.dataframe(df.head(100), use_container_width=True)
                        
                        # Column info
                        st.subheader("Column Information")
                        col_info = pd.DataFrame({
                            'Column': df.columns,
                            'Type': df.dtypes,
                            'Non-Null Count': df.count(),
                            'Null Count': df.isnull().sum()
                        })
                        st.dataframe(col_info, use_container_width=True)
                        
                        # Visualization
                        st.subheader("Visualization")
                        
                        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                        if numeric_cols:
                            col = st.selectbox("Select column for visualization", numeric_cols)
                            
                            fig = px.histogram(df, x=col, nbins=50, title=f"Distribution of {col}")
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Export
                        st.subheader("Export Data")
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name=f"{selected_file.split('/')[-1]}.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("No files found")

st.markdown("---")
st.caption(f"Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
