#!/usr/bin/env python3
"""
threadsrecon GUI - Local Streamlit interface for threadsrecon CLI tool
Orchestrates pipeline stages without modifying core logic
"""

import streamlit as st
import yaml
import json
import subprocess
import os
import shutil
import threading
import time
from pathlib import Path
from typing import Dict, List, Iterator, Optional, Union
from io import StringIO

# Configuration
SETTINGS_FILE = "settings.yaml"
DATA_DIR = "data"
MAIN_SCRIPT = "main.py"

def load_yaml(path: str) -> dict:
    """Load and parse YAML file, return dict or raise exception for invalid syntax."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML syntax: {e}")

def save_yaml(path: str, data: dict) -> None:
    """Write dict to YAML file with proper formatting and atomic write."""
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        os.replace(temp_path, path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e

def patch_usernames(yaml_text: str, names: List[str]) -> str:
    """Update ScraperSettings.usernames in YAML text, preserve all other keys."""
    try:
        data = yaml.safe_load(yaml_text) or {}
        if 'ScraperSettings' not in data:
            data['ScraperSettings'] = {}
        data['ScraperSettings']['usernames'] = names
        return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    except yaml.YAMLError:
        return yaml_text

def validate_paths() -> Dict[str, bool]:
    """Check chromedriver, wkhtmltopdf, data/ write access. Return status dict."""
    status = {}
    
    # Check chromedriver
    chromedriver_paths = ['/usr/local/bin/chromedriver', './chromedriver', 'chromedriver']
    status['chromedriver'] = any(shutil.which(path) or os.path.isfile(path) for path in chromedriver_paths)
    
    # Check wkhtmltopdf
    wkhtmltopdf_paths = ['/usr/bin/wkhtmltopdf', 'wkhtmltopdf']
    status['wkhtmltopdf'] = any(shutil.which(path) or os.path.isfile(path) for path in wkhtmltopdf_paths)
    
    # Check data directory write access
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        test_file = os.path.join(DATA_DIR, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.unlink(test_file)
        status['data_write'] = True
    except (OSError, PermissionError):
        status['data_write'] = False
    
    return status

def run_stage_with_logs(stage: str, env: Dict[str, str]) -> Iterator[str]:
    """Execute python main.py <stage> and yield stdout/stderr lines in real-time."""
    cmd = ['python', MAIN_SCRIPT, stage]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env={**os.environ, **env}
        )
        
        for line in iter(process.stdout.readline, ''):
            yield line.rstrip()
        
        process.wait()
        yield f"\n--- Process completed with exit code: {process.returncode} ---"
        
    except Exception as e:
        yield f"Error executing pipeline: {e}"

def list_artifacts() -> Dict[str, List[str]]:
    """Scan data/ directory and return categorized artifact paths."""
    artifacts = {
        'json': [],
        'images': [],
        'reports': []
    }
    
    if not os.path.exists(DATA_DIR):
        return artifacts
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, DATA_DIR)
            
            if file.endswith('.json'):
                artifacts['json'].append(file_path)
            elif file.endswith(('.png', '.jpg', '.jpeg', '.svg')):
                artifacts['images'].append(file_path)
            elif file.endswith('.pdf'):
                artifacts['reports'].append(file_path)
    
    return artifacts

def preview_artifact(path: str) -> Optional[Union[Dict, bytes]]:
    """Load JSON, image, or PDF content for preview. Return None if missing."""
    if not os.path.exists(path):
        return None
    
    try:
        if path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif path.endswith(('.png', '.jpg', '.jpeg')):
            with open(path, 'rb') as f:
                return f.read()
        else:
            return None
    except (json.JSONDecodeError, OSError):
        return None

def get_versions() -> Dict[str, str]:
    """Query binary versions and paths for telemetry display."""
    versions = {}
    
    # ChromeDriver version
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            versions['chromedriver'] = result.stdout.strip()
        else:
            versions['chromedriver'] = "Not Found"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        versions['chromedriver'] = "Not Found"
    
    # wkhtmltopdf version
    try:
        result = subprocess.run(['wkhtmltopdf', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            versions['wkhtmltopdf'] = result.stdout.strip()
        else:
            versions['wkhtmltopdf'] = "Not Found"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        versions['wkhtmltopdf'] = "Not Found"
    
    return versions

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="threadsrecon GUI",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 threadsrecon GUI")
    st.markdown("*Local GUI for threads.net OSINT analysis*")
    
    # Initialize session state
    if 'yaml_content' not in st.session_state:
        st.session_state.yaml_content = ""
    if 'log_output' not in st.session_state:
        st.session_state.log_output = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    
    # Sidebar
    with st.sidebar:
        st.header("Pipeline Controls")
        
        # Environment validation
        st.subheader("Environment Status")
        validation = validate_paths()
        
        if validation['chromedriver']:
            st.success("✅ ChromeDriver Ready")
        else:
            st.error("❌ ChromeDriver Missing")
        
        if validation['wkhtmltopdf']:
            st.success("✅ wkhtmltopdf Ready")
        else:
            st.error("❌ wkhtmltopdf Missing")
        
        if validation['data_write']:
            st.success("✅ Data Directory Writable")
        else:
            st.error("❌ Permission Denied")
        
        # Pipeline settings
        st.subheader("Run Configuration")
        
        stage = st.selectbox(
            "Pipeline Stage",
            ["all", "scrape", "analyze", "visualize", "report"],
            help="Select which stage of the pipeline to run"
        )
        
        headless = st.checkbox(
            "Run in Background",
            value=True,
            help="Hide browser window during scraping"
        )
        
        usernames_input = st.text_input(
            "Target Usernames",
            placeholder="username1, username2, username3",
            help="Comma-separated list of usernames to analyze"
        )
        
        # Run button
        can_run = all(validation.values()) and not st.session_state.is_running
        
        if st.button("▶ Run Pipeline", disabled=not can_run, type="primary"):
            # Update usernames in YAML if provided
            if usernames_input.strip():
                usernames = [name.strip() for name in usernames_input.split(',') if name.strip()]
                try:
                    current_yaml = load_yaml(SETTINGS_FILE)
                    if 'ScraperSettings' not in current_yaml:
                        current_yaml['ScraperSettings'] = {}
                    current_yaml['ScraperSettings']['usernames'] = usernames
                    save_yaml(SETTINGS_FILE, current_yaml)
                    st.success(f"Updated usernames: {', '.join(usernames)}")
                except Exception as e:
                    st.error(f"Failed to update usernames: {e}")
            
            # Start pipeline
            st.session_state.is_running = True
            st.session_state.log_output = []
            st.rerun()
        
        if st.session_state.is_running:
            if st.button("⏹ Stop", type="secondary"):
                st.session_state.is_running = False
                st.rerun()
        
        # Version info
        st.subheader("System Info")
        versions = get_versions()
        st.text(f"ChromeDriver: {versions.get('chromedriver', 'Unknown')[:30]}...")
        st.text(f"wkhtmltopdf: {versions.get('wkhtmltopdf', 'Unknown')[:30]}...")
    
    # Main area tabs
    tab1, tab2, tab3 = st.tabs(["Settings", "Run", "Artifacts"])
    
    with tab1:
        st.header("Settings Management")
        
        # Load current YAML
        try:
            yaml_data = load_yaml(SETTINGS_FILE)
            if not st.session_state.yaml_content:
                st.session_state.yaml_content = yaml.safe_dump(yaml_data, default_flow_style=False, sort_keys=False)
        except Exception as e:
            st.error(f"Error loading settings: {e}")
            if not st.session_state.yaml_content:
                st.session_state.yaml_content = "# settings.yaml\n"
        
        # YAML editor
        yaml_editor = st.text_area(
            "settings.yaml",
            value=st.session_state.yaml_content,
            height=400,
            help="Edit your threadsrecon configuration"
        )
        
        # Save button
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("💾 Save", type="primary"):
                try:
                    # Validate YAML
                    yaml.safe_load(yaml_editor)
                    
                    # Save to file
                    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                        f.write(yaml_editor)
                    
                    st.session_state.yaml_content = yaml_editor
                    st.success("Settings saved successfully!")
                    time.sleep(1)
                    st.rerun()
                    
                except yaml.YAMLError as e:
                    st.error(f"Invalid YAML syntax: {e}")
                except Exception as e:
                    st.error(f"Failed to save settings: {e}")
        
        with col2:
            # YAML validation indicator
            try:
                yaml.safe_load(yaml_editor)
                st.success("✅ Valid YAML")
            except yaml.YAMLError as e:
                st.error(f"❌ Invalid YAML: {e}")
    
    with tab2:
        st.header("Pipeline Execution")
        
        if st.session_state.is_running:
            st.info("🔄 Pipeline is running...")
            
            # Execute pipeline in thread to avoid blocking
            env_vars = {'THREADSRECON_HEADLESS': '1' if headless else '0'}
            
            log_container = st.container()
            
            def run_pipeline():
                for log_line in run_stage_with_logs(stage, env_vars):
                    st.session_state.log_output.append(log_line)
                st.session_state.is_running = False
            
            # Start pipeline thread if not already running
            if len(st.session_state.log_output) == 0:
                thread = threading.Thread(target=run_pipeline)
                thread.daemon = True
                thread.start()
            
            # Display logs
            with log_container:
                if st.session_state.log_output:
                    log_text = '\n'.join(st.session_state.log_output)
                    st.text_area("Live Logs", value=log_text, height=400, key="live_logs")
                
                # Auto-refresh every second
                time.sleep(1)
                st.rerun()
        
        elif st.session_state.log_output:
            st.header("Last Run Results")
            log_text = '\n'.join(st.session_state.log_output)
            st.text_area("Execution Logs", value=log_text, height=400, key="final_logs")
            
            if "exit code: 0" in log_text:
                st.success("✅ Pipeline completed successfully!")
            else:
                st.error("❌ Pipeline failed. Check logs for details.")
        
        else:
            st.info("Click 'Run Pipeline' in the sidebar to start execution.")
    
    with tab3:
        st.header("Generated Artifacts")
        
        artifacts = list_artifacts()
        
        # JSON files
        if artifacts['json']:
            st.subheader("📄 JSON Data")
            for json_file in artifacts['json']:
                with st.expander(f"📁 {os.path.basename(json_file)}"):
                    json_data = preview_artifact(json_file)
                    if json_data:
                        st.json(json_data)
                    else:
                        st.error("Failed to load JSON file")
        else:
            st.info("No JSON artifacts found. Run the pipeline to generate data.")
        
        # Images
        if artifacts['images']:
            st.subheader("🖼️ Visualizations")
            cols = st.columns(3)
            for i, img_file in enumerate(artifacts['images']):
                with cols[i % 3]:
                    img_data = preview_artifact(img_file)
                    if img_data:
                        st.image(img_data, caption=os.path.basename(img_file))
                    else:
                        st.error(f"Failed to load {os.path.basename(img_file)}")
        else:
            st.info("No visualization images found. Run visualization stage to generate charts.")
        
        # Reports
        if artifacts['reports']:
            st.subheader("📋 Reports")
            for report_file in artifacts['reports']:
                st.markdown(f"📄 **{os.path.basename(report_file)}**")
                if st.button(f"📖 Open {os.path.basename(report_file)}", key=f"open_{report_file}"):
                    st.info(f"Report location: {os.path.abspath(report_file)}")
        else:
            st.info("No PDF reports found. Run report stage to generate comprehensive analysis.")

if __name__ == "__main__":
    main()