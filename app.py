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
                
                # Show loading
                with st.spinner("Calling CrewAI API..."):
                    
                    # Call your CrewAI API with actual credentials
                    response = requests.post(
                        "https://ai-ml-product-risk-intake-assessment-agent--7d76c5b8.crewai.com/kickoff",
                        headers={
                            "Authorization": "Bearer a57ebdae2616",
                            "Content-Type": "application/json"
                        },
                        json={
                            "inputs": {
                                "project_name": project_name,
                                "risk_description": risk_description,
                                "contextual_notes": contextual_notes,
                                "initial_probability": initial_probability,
                                "initial_impact": initial_impact,
                                "customer_email": "assessment@company.com"  # Fixed placeholder
                            }
                        },
                        timeout=300
                    )
                
                # Display results
                if response.status_code == 200:
                    assessment_results = response.json()
                    
                    if "kickoff_id" in assessment_results:
                        kickoff_id = assessment_results["kickoff_id"]
                        st.success(f"✅ Workflow Started! ID: {kickoff_id}")
                        
                        # Poll for actual results using the kickoff_id
                        st.info("⏳ Fetching your assessment results...")
                        
                        # Try to get results from the kickoff_id endpoint
                        max_attempts = 12  # 2 minutes total
                        for attempt in range(max_attempts):
                            try:
                                # Try to get results from the same kickoff endpoint with the ID
                                results_response = requests.get(
                                    f"https://ai-ml-product-risk-intake-assessment-agent--7d76c5b8.crewai.com/kickoff/{kickoff_id}",
                                    headers={
                                        "Authorization": "Bearer a57ebdae2616",
                                        "Content-Type": "application/json"
                                    },
                                    timeout=10
                                )
                                
                                if results_response.status_code == 200:
                                    results_data = results_response.json()
                                    
                                    # Check if we got actual results (not just status)
                                    if results_data and "status" in results_data and results_data["status"] == "completed":
                                        st.success("🎉 Assessment Complete!")
                                        st.subheader("📊 Your AI Risk Assessment Results")
                                        
                                        # Show the actual assessment content
                                        if "output" in results_data:
                                            st.markdown(results_data["output"])
                                        else:
                                            st.json(results_data)
                                        
                                        # Download button
                                        st.download_button(
                                            label="📥 Download Assessment",
                                            data=json.dumps(results_data, indent=2),
                                            file_name=f"risk_assessment_{project_name}_{int(time.time())}.json",
                                            mime="application/json"
                                        )
                                        break
                                    
                                    elif attempt < max_attempts - 1:
                                        st.write(f"⏳ Checking... (Attempt {attempt + 1}/{max_attempts})")
                                        time.sleep(10)
                                
                                else:
                                    st.write(f"Attempt {attempt + 1}: Status {results_response.status_code}")
                                    if attempt < max_attempts - 1:
                                        time.sleep(10)
                                        
                            except Exception as e:
                                st.write(f"Attempt {attempt + 1}: {str(e)}")
                                if attempt < max_attempts - 1:
                                    time.sleep(10)
                        
                        else:
                            st.warning("⏰ Assessment is taking longer than expected. Your workflow is processing...")
                            st.write(f"Workflow ID: {kickoff_id}")
                            st.write("Results will be available in your CrewAI dashboard when complete.")
                    
                    else:
                        # Direct results returned
                        st.success("✅ Assessment Complete!")
                        st.subheader("📊 AI Risk Assessment Results")
                        st.json(assessment_results)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Results",
                            data=json.dumps(assessment_results, indent=2),
                            file_name=f"crewai_response_{int(time.time())}.json",
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

# Footer
st.markdown("---")
st.markdown("🤖 **Multi-Agent AI Risk Assessment** | Built with CrewAI + Streamlit")
