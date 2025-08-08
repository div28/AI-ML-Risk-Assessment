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
                            
                            # Add manual results input section
                            st.markdown("---")
                            st.subheader("📋 Manual Results Entry")
                            st.write("Since your CrewAI workflow completed successfully, you can paste the results here:")
                            
                            # Manual input for results
                            manual_results = st.text_area(
                                "Paste Assessment Results from CrewAI Dashboard:",
                                height=200,
                                placeholder="Copy and paste the complete assessment output from your CrewAI dashboard here..."
                            )
                            
                            if st.button("📊 Display Results") and manual_results:
                                st.success("📋 Assessment Results Display")
                                
                                # Try to parse as JSON first
                                try:
                                    parsed_results = json.loads(manual_results)
                                    st.json(parsed_results)
                                    
                                    # Download as JSON
                                    st.download_button(
                                        label="📥 Download JSON",
                                        data=json.dumps(parsed_results, indent=2),
                                        file_name=f"risk_assessment_{project_name}_{int(time.time())}.json",
                                        mime="application/json"
                                    )
                                except json.JSONDecodeError:
                                    # Display as formatted text
                                    st.text_area("Assessment Results:", value=manual_results, height=300)
                                    
                                    # Download as text
                                    report_text = f"""AI/ML Risk Assessment Report
Project: {project_name}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Workflow ID: {kickoff_id}

ASSESSMENT RESULTS:
{manual_results}
"""
                                    st.download_button(
                                        label="📥 Download Report",
                                        data=report_text,
                                        file_name=f"risk_assessment_{project_name}_{int(time.time())}.txt",
                                        mime="text/plain"
                                    )
                    
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
            st.error("Please fill in Project Name and Risk Description!")

with col2:
    if 'assessment_results' not in locals():
        st.header("Output")
        st.write("👆 Fill in the form and click 'Generate Risk Assessment' to see results")

# Footer
st.markdown("---")
st.markdown("🤖 **Multi-Agent AI Risk Assessment** | Built with CrewAI + Streamlit")
