import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="AI/ML Risk Assessment Workflow",
    layout="wide"
)

st.title("AI/ML Risk Assessment Workflow")
st.write("Powered by CrewAI Multi-Agent System with Webhook Integration")

# Configuration section
st.subheader("🔧 Configuration")
col_config1, col_config2 = st.columns(2)

with col_config1:
    api_url = st.text_input(
        "CrewAI API URL", 
        value="https://ai-ml-product-risk-intake-assessment-agent--7d76c5b8.crewai.com/kickoff",
        help="Enter your CrewAI API endpoint"
    )

with col_config2:
    api_token = st.text_input(
        "API Token", 
        value="a57ebdae2616",
        type="password",
        help="Enter your CrewAI authentication token"
    )

# Webhook configuration
with st.expander("🔗 Webhook Configuration (Advanced)"):
    webhook_url = st.text_input(
        "Webhook URL (Optional)",
        placeholder="https://your-webhook-receiver.com/crewai-results",
        help="URL where CrewAI will send completed results"
    )
    
    if webhook_url:
        st.info("✅ Webhook mode enabled - results will be sent to your webhook endpoint")
    else:
        st.info("📡 Using polling mode - will check for results periodically")

st.markdown("---")

# Initialize session state for webhook results
if 'webhook_results' not in st.session_state:
    st.session_state.webhook_results = {}

if 'active_workflows' not in st.session_state:
    st.session_state.active_workflows = {}

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input")
    
    # Required fields for your CrewAI API
    project_name = st.text_input("Project Name", value="Sales Email Copilot")
    
    risk_description = st.text_area("Risk Description", height=100, 
                                   value="Automates drafting of customer emails using sensitive CRM data")
    
    initial_impact = st.selectbox("Initial Impact Level", ["Low", "Medium", "High", "Critical"], index=2)
    
    initial_probability = st.selectbox("Initial Probability", ["Low", "Medium", "High"], index=2)
    
    contextual_notes = st.text_area("Contextual Notes", height=80,
                                   value="Targets EU; GDPR applies; drafts stored for 14 days.")
    
    # Submit button
    if st.button("🚀 Generate Risk Assessment", type="primary"):
        if risk_description and project_name:
            
            with col2:
                st.header("Output")
                
                # Generate unique session ID for this request
                session_id = str(uuid.uuid4())
                
                # Prepare payload with webhook info
                payload = {
                    "inputs": {
                        "project_name": project_name,
                        "risk_description": risk_description,
                        "contextual_notes": contextual_notes,
                        "initial_probability": initial_probability,
                        "initial_impact": initial_impact,
                        "customer_email": "assessment@company.com"
                    }
                }
                
                # Add webhook configuration if provided
                if webhook_url:
                    payload["webhook"] = {
                        "url": webhook_url,
                        "session_id": session_id,
                        "method": "POST"
                    }
                
                # Show loading
                with st.spinner("Calling CrewAI API..."):
                    
                    # Call CrewAI API
                    response = requests.post(
                        api_url,
                        headers={
                            "Authorization": f"Bearer {api_token}",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=300
                    )
                
                # Handle response
                if response.status_code == 200:
                    assessment_results = response.json()
                    
                    if "kickoff_id" in assessment_results:
                        kickoff_id = assessment_results["kickoff_id"]
                        st.success(f"✅ Workflow Started! ID: {kickoff_id}")
                        
                        # Store workflow info
                        st.session_state.active_workflows[kickoff_id] = {
                            "project_name": project_name,
                            "started_at": datetime.now().isoformat(),
                            "session_id": session_id,
                            "status": "running"
                        }
                        
                        if webhook_url:
                            # Webhook mode
                            st.info("🔗 Webhook configured - waiting for results...")
                            st.write(f"**Webhook URL:** {webhook_url}")
                            st.write(f"**Session ID:** {session_id}")
                            
                            # Show instructions for webhook setup
                            with st.expander("📋 Webhook Setup Instructions"):
                                st.write("""
                                **To receive results via webhook:**
                                
                                1. **Configure CrewAI** to send results to your webhook URL
                                2. **Your webhook endpoint** should accept POST requests
                                3. **Expected payload format:**
                                ```json
                                {
                                    "kickoff_id": "...",
                                    "session_id": "...",
                                    "status": "completed",
                                    "output": "...",
                                    "final_output": "..."
                                }
                                ```
                                4. **Update this page** to see results when received
                                """)
                            
                            # Check for webhook results
                            if session_id in st.session_state.webhook_results:
                                webhook_data = st.session_state.webhook_results[session_id]
                                st.success("📨 Webhook Results Received!")
                                st.subheader("📊 AI Risk Assessment Results")
                                
                                if "output" in webhook_data:
                                    st.markdown(webhook_data["output"])
                                elif "final_output" in webhook_data:
                                    st.markdown(webhook_data["final_output"])
                                else:
                                    st.json(webhook_data)
                                
                                # Download button
                                st.download_button(
                                    label="📥 Download Results",
                                    data=json.dumps(webhook_data, indent=2),
                                    file_name=f"webhook_results_{project_name}_{int(time.time())}.json",
                                    mime="application/json"
                                )
                        
                        else:
                            # Polling mode (existing implementation)
                            st.info("⏳ Polling for assessment results... (This may take 1-2 minutes)")
                            
                            # Progress tracking
                            progress_bar = st.progress(0)
                            status_placeholder = st.empty()
                            
                            # Poll for completion
                            max_polls = 24  # 4 minutes total
                            base_url = api_url.replace('/kickoff', '')
                            
                            for poll_count in range(max_polls):
                                # Update progress
                                progress = (poll_count + 1) / max_polls
                                progress_bar.progress(progress)
                                status_placeholder.write(f"🔄 Checking for results... ({poll_count + 1}/{max_polls})")
                                
                                # Try status endpoints
                                poll_endpoints = [
                                    f"{base_url}/status/{kickoff_id}",
                                    f"{base_url}/result/{kickoff_id}",
                                    f"{base_url}/output/{kickoff_id}"
                                ]
                                
                                found_completed = False
                                
                                for endpoint in poll_endpoints:
                                    try:
                                        poll_response = requests.get(
                                            endpoint,
                                            headers={
                                                "Authorization": f"Bearer {api_token}",
                                                "Content-Type": "application/json"
                                            },
                                            timeout=10
                                        )
                                        
                                        if poll_response.status_code == 200:
                                            poll_data = poll_response.json()
                                            
                                            if poll_data and "status" in poll_data and poll_data["status"] == "completed":
                                                progress_bar.progress(1.0)
                                                status_placeholder.write("✅ Assessment completed!")
                                                
                                                st.success("🎉 Assessment Results Retrieved!")
                                                st.subheader("📊 AI Risk Assessment Results")
                                                
                                                if "output" in poll_data:
                                                    st.markdown(poll_data["output"])
                                                elif "final_output" in poll_data:
                                                    st.markdown(poll_data["final_output"])
                                                else:
                                                    st.json(poll_data)
                                                
                                                st.download_button(
                                                    label="📥 Download Results",
                                                    data=json.dumps(poll_data, indent=2),
                                                    file_name=f"assessment_{project_name}_{int(time.time())}.json",
                                                    mime="application/json"
                                                )
                                                found_completed = True
                                                break
                                    
                                    except Exception:
                                        continue
                                
                                if found_completed:
                                    break
                                
                                if poll_count < max_polls - 1:
                                    time.sleep(10)
                            
                            # If no results found via polling
                            if not found_completed:
                                st.warning("⏰ Results not available via polling")
                                st.info("✅ Workflow started successfully - results may be available via webhook or dashboard")
                    
                    else:
                        # Direct synchronous results
                        st.success("✅ Immediate Results!")
                        st.subheader("📊 AI Risk Assessment Results")
                        st.json(assessment_results)
                        
                        st.download_button(
                            label="📥 Download Results",
                            data=json.dumps(assessment_results, indent=2),
                            file_name=f"immediate_results_{int(time.time())}.json",
                            mime="application/json"
                        )
                
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.write(response.text)
        
        else:
            st.error("Please fill in Project Name and Risk Description!")

with col2:
    if 'assessment_results' not in locals():
        st.header("Output")
        st.write("👆 Fill in the form and click 'Generate Risk Assessment' to see results")

# Webhook receiver simulation (for demo purposes)
st.markdown("---")
with st.expander("🔧 Webhook Result Simulator (Demo)"):
    st.write("**For demonstration:** Simulate receiving webhook results")
    
    col_demo1, col_demo2 = st.columns(2)
    
    with col_demo1:
        demo_session_id = st.text_input("Session ID", placeholder="Enter session ID from active workflow")
    
    with col_demo2:
        demo_output = st.text_area("Simulated Result", height=100, 
                                  placeholder="Paste assessment results here...")
    
    if st.button("📨 Simulate Webhook Result") and demo_session_id and demo_output:
        st.session_state.webhook_results[demo_session_id] = {
            "session_id": demo_session_id,
            "status": "completed",
            "output": demo_output,
            "received_at": datetime.now().isoformat()
        }
        st.success(f"✅ Simulated webhook result stored for session: {demo_session_id}")
        st.rerun()

# Active workflows display
if st.session_state.active_workflows:
    st.markdown("---")
    st.subheader("📊 Active Workflows")
    
    for workflow_id, info in st.session_state.active_workflows.items():
        with st.expander(f"Workflow: {info['project_name']} ({workflow_id[:8]}...)"):
            st.write(f"**Started:** {info['started_at']}")
            st.write(f"**Status:** {info['status']}")
            st.write(f"**Session ID:** {info.get('session_id', 'N/A')}")

# Footer
st.markdown("---")
st.markdown("🤖 **Multi-Agent AI Risk Assessment** | Built with CrewAI + Streamlit + Webhooks")
