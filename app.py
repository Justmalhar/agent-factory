import streamlit as st
import json
import logging
from utils.openai_client import create_openai_client, generate_content, read_prompt
import time

# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="YouTube Content Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .output-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .stProgress > div > div > div > div {
        background-color: #00cc00;
    }
</style>
""", unsafe_allow_html=True)

def create_section_ui(title):
    """Create a collapsible section with progress and output"""
    st.markdown(f"### {title}")
    progress = st.progress(0)
    output = st.empty()
    return progress, output

def stream_output(output_container, stream_response):
    """Stream content to output container"""
    if stream_response is None:
        return "Error: Failed to generate content"
        
    placeholder = output_container.empty()
    full_text = ""
    
    try:
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_text += content
                placeholder.markdown(full_text + "▌")
        
        # Final update without cursor
        placeholder.markdown(full_text)
        return full_text
        
    except Exception as e:
        error_msg = f"Error during streaming: {str(e)}"
        logging.error(error_msg)
        placeholder.error(error_msg)
        return error_msg

def main():
    st.title("YouTube Content Generator")
    
    # Input Section
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            api_key = st.text_input("OpenAI API Key:", type="password")
            topic = st.text_input("Video Topic:", placeholder="Enter your video topic here...")
        
        with col2:
            model = st.selectbox(
                "AI Model",
                ["gpt-4o-mini", "gpt-4o"]
            )
            generate_button = st.button("Generate Content", type="primary", use_container_width=True)
    
    # Create containers for each section
    sections = {
        "video_ideas": "Video Ideas",
        "titles": "Titles",
        "keywords": "Keywords",
        "description": "Description",
        "hook": "Hook",
        "outline": "Outline",
        "script": "Script"
    }
    
    # Initialize session state for outputs
    if 'outputs' not in st.session_state:
        st.session_state.outputs = {}
    
    # Create section containers
    section_containers = {}
    for key, title in sections.items():
        with st.expander(title, expanded=True):
            progress, output = create_section_ui(title)
            section_containers[key] = {
                'progress': progress,
                'output': output,
                'download': st.empty()
            }
    
    if generate_button:
        if not api_key or not topic:
            st.error("Please provide both API key and topic!")
            return
        
        try:
            client = create_openai_client(api_key)
            previous_results = {}
            
            # Generate content for each section
            for section_key, section_title in sections.items():
                containers = section_containers[section_key]
                
                # Update progress
                containers['progress'].progress(25)
                
                # Generate content with context
                system_prompt = read_prompt(section_key)
                context = "\n".join([f"{k}: {v}" for k, v in previous_results.items()])
                user_prompt = f"Topic: {topic}\nPrevious content:\n{context}\n\nGenerate {section_key.replace('_', ' ')}."
                
                try:
                    # Stream response
                    containers['progress'].progress(50)
                    stream_response = generate_content(client, system_prompt, user_prompt, model)
                    
                    # Stream output
                    containers['progress'].progress(75)
                    result = stream_output(containers['output'], stream_response)
                    
                    if not result.startswith("Error"):
                        previous_results[section_key] = result
                        st.session_state.outputs[section_key] = result
                        
                        # Add download button
                        containers['download'].download_button(
                            f"Download {section_title}",
                            result,
                            file_name=f"{section_key}_{topic.replace(' ', '_')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                        
                        containers['progress'].progress(100)
                    else:
                        containers['output'].error(result)
                        containers['progress'].progress(0)
                
                except Exception as e:
                    containers['output'].error(f"Error generating {section_title}: {str(e)}")
                    containers['progress'].progress(0)
                    continue
        
        except Exception as e:
            st.error(f"Failed to initialize: {str(e)}")
            return
    
    # Display existing outputs
    elif st.session_state.outputs:
        for section_key, content in st.session_state.outputs.items():
            containers = section_containers[section_key]
            containers['output'].markdown(content)
            containers['progress'].progress(100)
            
            if content and not content.startswith("Error"):
                containers['download'].download_button(
                    f"Download {sections[section_key]}",
                    content,
                    file_name=f"{section_key}_{topic.replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

if __name__ == "__main__":
    main() 