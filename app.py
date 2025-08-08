import streamlit as st

# Basic text elements
st.title("Main Title")
st.header("Header")
st.subheader("Subheader")
st.write("Regular text or markdown")
st.markdown("**Bold text** or *italic*")

# Input widgets
text_input = st.text_input("Enter text:")
text_area = st.text_area("Enter long text:")
number = st.number_input("Enter number:", min_value=0, max_value=100)
slider_value = st.slider("Select value:", 0, 100, 50)
selectbox_choice = st.selectbox("Choose option:", ["Option 1", "Option 2"])
multiselect_choices = st.multiselect("Choose multiple:", ["A", "B", "C"])
checkbox = st.checkbox("Check me")
radio = st.radio("Pick one:", ["Choice 1", "Choice 2"])

# Buttons
if st.button("Click me"):
    st.write("Button was clicked!")

# File upload
uploaded_file = st.file_uploader("Choose a file")

# Layout
col1, col2 = st.columns(2)
with col1:
    st.write("Left column")
with col2:
    st.write("Right column")

# Sidebar
with st.sidebar:
    st.write("This is in the sidebar")

# Expandable sections
with st.expander("Click to expand"):
    st.write("Hidden content")

# Status indicators
st.success("Success message")
st.error("Error message")
st.warning("Warning message")
st.info("Info message")

# Progress indicators
progress_bar = st.progress(0)
# Update progress: progress_bar.progress(50)

# Metrics
st.metric("Temperature", "70°F", "1.2°F")

# Display data
st.json({"key": "value"})  # JSON display
st.code("print('Hello')", language="python")  # Code block

# Session state (for keeping data between interactions)
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment"):
    st.session_state.counter += 1

st.write(f"Counter: {st.session_state.counter}")

# Page configuration (put at the top of your file)
st.set_page_config(
    page_title="My App",
    page_icon="🚀",
    layout="wide"  # or "centered"
)
