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
    
    customer_email = st.text_input("Customer Email", value="divya288@gmail.com")
    
    # Submit button
    if st.button("🚀 Generate Risk Assessment", type="primary"):
        if risk_description and project_name and customer_email:
            
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
                                "customer_email": customer_email
                            }
                        },
                        timeout=300
                    )
                
                # Display results
                if response.status_code == 200:
                    st.success("✅ Assessment Complete!")
                    st.subheader("📊 AI Risk Assessment Results")
                    
                    # Show the complete report
                    assessment_results = response.json()
                    
                    # Display results beautifully
                    if "kickoff_id" in assessment_results:
                        st.info(f"🚀 Workflow Started! ID: {assessment_results['kickoff_id']}")
                        st.write("Your multi-agent assessment is now running...")
                        
                        # Try to get immediate results
                        kickoff_id = assessment_results["kickoff_id"]
                        
                        # Wait a moment and try to get results
                        st.write("⏳ Checking for completed results...")
                        time.sleep(5)
                        
                        # Try different result endpoints
                        base_url = "https://ai-ml-product-risk-intake-assessment-agent--7d76c5b8.crewai.com"
                        result_urls = [
                            f"{base_url}/{kickoff_id}",
                            f"{base_url}/result/{kickoff_id}",
                            f"{base_url}/output/{kickoff_id}",
                            f"{base_url}/status/{kickoff_id}"
                        ]
                        
                        found_results = False
                        for url in result_urls:
                            try:
                                result_response = requests.get(url, headers={
                                    "Authorization": "Bearer a57ebdae2616",
                                    "Content-Type": "application/json"
                                }, timeout=10)
                                
                                if result_response.status_code == 200:
                                    result_data = result_response.json()
                                    if result_data and len(str(result_data)) > 100:
                                        st.success("📋 Found Assessment Results!")
                                        st.json(result_data)
                                        
                                        # Download button
                                        st.download_button(
                                            label="📥 Download Assessment",
                                            data=json.dumps(result_data, indent=2),
                                            file_name=f"risk_assessment_{project_name}_{int(time.time())}.json",
                                            mime="application/json"
                                        )
                                        found_results = True
                                        break
                            except:
                                continue
                        
                        if not found_results:
                            st.write("⌛ Assessment is processing... Results will be available shortly.")
                            st.write("Your workflow is running successfully in the background!")
                    
                    else:
                        # Direct results returned
                        st.json(assessment_results)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Assessment",
                            data=json.dumps(assessment_results, indent=2),
                            file_name=f"risk_assessment_{project_name}_{int(time.time())}.json",
                            mime="application/json"
                        )
                
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.write(response.text)
        
        else:
            st.error("Please fill in all required fields!")

with col2:
    if 'assessment_results' not in locals():
        st.header("Output")
        st.write("👆 Fill in the form and click 'Generate Risk Assessment' to see results")

# Sample section
st.markdown("---")
with st.expander("📝 Sample Assessment"):
    st.write("""
    **Project:** Sales Email Copilot
    **Risk Description:** Automates drafting of customer emails using sensitive CRM data
    **Impact:** High - Potential GDPR violations and data breaches
    **Probability:** High - Direct access to sensitive customer information
    **Context:** EU operations, 14-day data retention, automated processing
    """)

# Footer
st.markdown("---")
st.markdown("🤖 **Multi-Agent AI Risk Assessment** | Built with CrewAI + Streamlit")
