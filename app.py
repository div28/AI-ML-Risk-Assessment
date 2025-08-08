import streamlit as st
import requests
import json
import time

# Page configuration
st.set_page_config(
    page_title="AI/ML Risk Assessment Workflow",
    layout="wide"
)

st.title("AI/ML Risk Assessment Workflow")
st.write("Powered by CrewAI Multi-Agent System")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_url = st.text_input("CrewAI API URL", placeholder="https://your-crewai-api.com/kickoff")
    api_key = st.text_input("API Key (if required)", type="password")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input")
    
    # Required fields for your CrewAI API
    project_name = st.text_input("Project Name", placeholder="e.g., Loan Approval ML System")
    
    risk_description = st.text_area("Risk Description", height=100, 
                                   placeholder="Describe the AI/ML system and its risks...")
    
    initial_impact = st.selectbox("Initial Impact Level", ["Low", "Medium", "High", "Critical"])
    
    initial_probability = st.selectbox("Initial Probability", ["Low", "Medium", "High"])
    
    contextual_notes = st.text_area("Contextual Notes", height=80,
                                   placeholder="Additional context, constraints, or considerations...")
    
    customer_email = st.text_input("Customer Email", placeholder="customer@company.com")
    
    # Additional parameters
    with st.expander("Advanced Options"):
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        agents_to_use = st.multiselect("Select Agents", 
                                     ["Risk Analyst", "Compliance Expert", "Technical Reviewer", "Report Generator"])
        max_iterations = st.slider("Max Iterations", 1, 10, 3)
    
    # Submit button
    if st.button("Run Risk Assessment", type="primary"):
        # Debug: Show what values we're capturing
        st.write("DEBUG - Captured values:")
        st.write(f"Project Name: '{project_name}'")
        st.write(f"Risk Description: '{risk_description}'")
        st.write(f"Customer Email: '{customer_email}'")
        st.write(f"Initial Impact: '{initial_impact}'")
        st.write(f"Initial Probability: '{initial_probability}'")
        
        if risk_description and project_name and customer_email:
            # Store input in session state
            st.session_state.workflow_running = True
            st.session_state.api_payload = {
                "risk_description": risk_description,
                "initial_impact": initial_impact,
                "contextual_notes": contextual_notes,
                "customer_email": customer_email,
                "project_name": project_name,
                "initial_probability": initial_probability
            }
            st.session_state.workflow_params = {
                "priority": priority,
                "agents": agents_to_use,
                "max_iterations": max_iterations
            }
            
            # Debug: Show the payload being sent
            st.write("DEBUG - Payload being sent:")
            st.json(st.session_state.api_payload)
        else:
            st.error("Please fill in all required fields: Risk Description, Project Name, and Customer Email")
            st.write(f"Missing: Risk Description={bool(risk_description)}, Project Name={bool(project_name)}, Customer Email={bool(customer_email)}")

with col2:
    st.header("Output")
    
    # Check if workflow is running
    if hasattr(st.session_state, 'workflow_running') and st.session_state.workflow_running:
        
        # Prepare API request
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        payload = st.session_state.api_payload
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Make API call
            status_text.text("Sending request to CrewAI...")
            progress_bar.progress(25)
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=300)
            
            if response.status_code == 200:
                progress_bar.progress(50)
                status_text.text("Request sent successfully. Processing...")
                
                result = response.json()
                
                # Handle different response formats
                if "status" in result and result["status"] == "running":
                    # If workflow is async, poll for results
                    job_id = result.get("job_id")
                    if job_id:
                        st.session_state.job_id = job_id
                        status_text.text("Workflow running... Checking status...")
                        
                        # Poll for completion
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
                status_text.text("Risk Assessment completed!")
                
                # Display results
                st.success("Risk Assessment completed successfully!")
                
                # Show agent outputs
                if "agents_output" in result:
                    for agent_name, output in result["agents_output"].items():
                        with st.expander(f"Agent {agent_name} Analysis"):
                            st.write(output)
                
                # Show final result
                if "final_output" in result:
                    st.subheader("Risk Assessment Report")
                    st.write(result["final_output"])
                elif "result" in result:
                    st.subheader("Risk Assessment Report")
                    st.write(result["result"])
                else:
                    st.subheader("Complete Response")
                    st.json(result)
                
                # Show execution details
                with st.expander("Execution Details"):
                    if "execution_time" in result:
                        st.metric("Execution Time", f"{result['execution_time']:.2f}s")
                    if "tokens_used" in result:
                        st.metric("Tokens Used", result["tokens_used"])
                    if "agents_involved" in result:
                        st.write("**Agents Involved:**", ", ".join(result["agents_involved"]))
                
                # Download option
                if st.button("Download Results"):
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

# Real-time status updates
if "job_id" in st.session_state:
    if st.button("Refresh Status"):
        st.rerun()

# Sample request section
with st.expander("Sample Risk Assessment Request"):
    st.write("""
    **Example input:**
    
    Project Name: Loan Approval ML System
    Risk Description: Machine learning model for loan approval decisions using customer credit history, income data, and demographic information. Will automatically approve or deny loan applications up to $50,000.
    
    **This will trigger your AI agents to analyze:**
    - Bias and fairness risks
    - Regulatory compliance issues  
    - Data privacy concerns
    - Model interpretability requirements
    - Operational risks
    """)

# Footer
st.markdown("---")
st.markdown("Built with CrewAI and Streamlit for AI/ML Risk Assessment")
