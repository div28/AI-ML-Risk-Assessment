import streamlit as st
import requests
import json
import time

# Page configuration
st.set_page_config(
    page_title="AI/ML Risk Assessment Workflow",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI/ML Risk Assessment Workflow")
st.write("Powered by CrewAI Multi-Agent System")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_url = st.text_input("CrewAI API URL", placeholder="https://your-crewai-api.com/workflow")
    api_key = st.text_input("API Key (if required)", type="password")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input")
    
    # Input form
    user_input = st.text_area("Enter your risk assessment request:", height=150, 
                             placeholder="Describe the AI/ML system you want to assess for risks...")
    
    # Additional parameters (customize based on your workflow)
    with st.expander("Advanced Options"):
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        agents_to_use = st.multiselect("Select Agents", 
                                     ["Risk Analyst", "Compliance Expert", "Technical Reviewer", "Report Generator"])
        max_iterations = st.slider("Max Iterations", 1, 10, 3)
    
    # Submit button
    if st.button("🚀 Run Risk Assessment", type="primary"):
        if user_input and api_url:
            # Store input in session state
            st.session_state.workflow_running = True
            st.session_state.user_input = user_input
            st.session_state.workflow_params = {
                "priority": priority,
                "agents": agents_to_use,
                "max_iterations": max_iterations
            }
        else:
            st.error("Please provide both input and API URL")

with col2:
    st.header("Output")
    
    # Check if workflow is running
    if hasattr(st.session_state, 'workflow_running') and st.session_state.workflow_running:
        
        # Prepare API request
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        payload = {
            "input": st.session_state.user_input,
            "config": st.session_state.workflow_params
        }
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Make API call
            status_text.text("🔄 Sending request to CrewAI...")
            progress_bar.progress(25)
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=300)
            
            if response.status_code == 200:
                progress_bar.progress(50)
                status_text.text("✅ Request sent successfully. Processing...")
                
                result = response.json()
                
                # Handle different response formats
                if "status" in result and result["status"] == "running":
                    # If workflow is async, poll for results
                    job_id = result.get("job_id")
                    if job_id:
                        st.session_state.job_id = job_id
                        status_text.text("⏳ Workflow running... Checking status...")
                        
                        # Poll for completion (you'll need to implement polling endpoint)
                        for i in range(60):  # 5 minutes max
                            time.sleep(5)
                            status_response = requests.get(f"{api_url}/status/{job_id}")
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                if status_data.get("status") == "completed":
                                    result = status_data.get("result", {})
                                    break
                                elif status_data.get("status") == "failed":
                                    st.error("Workflow failed!")
                                    break
                            progress_bar.progress(min(75 + i, 95))
                
                progress_bar.progress(100)
                status_text.text("✅ Risk Assessment completed!")
                
                # Display results
                st.success("Risk Assessment completed successfully!")
                
                # Show agent outputs
                if "agents_output" in result:
                    for agent_name, output in result["agents_output"].items():
                        with st.expander(f"🤖 {agent_name} Analysis"):
                            st.write(output)
                
                # Show final result
                if "final_output" in result:
                    st.subheader("📋 Risk Assessment Report")
                    st.write(result["final_output"])
                
                # Show execution details
                with st.expander("📊 Execution Details"):
                    if "execution_time" in result:
                        st.metric("Execution Time", f"{result['execution_time']:.2f}s")
                    if "tokens_used" in result:
                        st.metric("Tokens Used", result["tokens_used"])
                    if "agents_involved" in result:
                        st.write("**Agents Involved:**", ", ".join(result["agents_involved"]))
                
                # Download option
                if st.button("📥 Download Results"):
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"risk_assessment_results_{int(time.time())}.json",
                        mime="application/json"
                    )
                
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. The workflow might still be running.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
        
        finally:
            progress_bar.empty()
            st.session_state.workflow_running = False

# Real-time status updates (if your API supports websockets)
if "job_id" in st.session_state:
    if st.button("🔄 Refresh Status"):
        st.rerun()

# Sample request section
with st.expander("📝 Sample Risk Assessment Request"):
    st.write("""
    **Example input:**
    
    "Assess the risks of deploying a machine learning model for loan approval decisions. 
    The model uses customer credit history, income data, and demographic information. 
    It will be used to automatically approve or deny loan applications up to $50,000."
    
    **This will trigger your AI agents to analyze:**
    - Bias and fairness risks
    - Regulatory compliance issues  
    - Data privacy concerns
    - Model interpretability requirements
    - Operational risks
    """)

# Footer
st.markdown("---")
st.markdown("Built with 🤖 CrewAI and 🎈 Streamlit for AI/ML Risk Assessment")
