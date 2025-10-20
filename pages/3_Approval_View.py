# File: pages/3_Approval_View.py

import streamlit as st
import os
import sys
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import crud
from app.core import ai_services

# --- Initialize State ---
st.set_page_config(page_title="Review & Generate", layout="wide")
st.title(f"🔍 Review, Generate, and Finalize")

if 'current_task_id' in st.session_state and st.session_state['current_task_id'] is not None:
    task_id = st.session_state['current_task_id']
    task = crud.get_task_by_id(task_id)

    if not task:
        st.error("Could not find Task ID: {}. It may have been deleted.".format(task_id))
        st.warning("Resetting session and returning to the dashboard.")
        st.session_state['current_task_id'] = None
        st.switch_page("pages/1_Dashboard.py")
    else:
        st.header(f"Working on Task ID: {task_id} for Product: {task.get('product_code', 'N/A')}")
        
        # --- UI for PENDING_APPROVAL status ---
        if task['status'] == 'PENDING_APPROVAL':
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Uploaded Images")
                image_paths_str = task.get('uploaded_image_paths', '')
                if image_paths_str:
                    for path in image_paths_str.split(','):
                        st.image(Image.open(path))
            with col2:
                st.subheader("Generated Spec Sheet (Editable)")
                edited_spec_sheet = st.text_area("Edit and approve:", value=task.get('spec_sheet_text', ''), height=300, key=f"spec_{task_id}")
                with st.expander("View Edit History"):
                    for version in reversed(crud.get_spec_sheet_versions(task_id)):
                        st.markdown(f"**Version {version['version_number']} (by {version['author']})**")
                        st.text(version['spec_text'])
                
                # --- NEW: Action Buttons with Save ---
                b_col1, b_col2, b_col3, _ = st.columns([1, 1, 1, 4])
                
                with b_col1:
                    if st.button(f"💾 Save Changes"):
                        if crud.save_spec_sheet_edit(task_id, edited_spec_sheet):
                            st.success("Changes saved successfully!")
                            # Rerun to refresh the version history
                            st.rerun()
                        else:
                            st.error("Failed to save changes.")

                with b_col2:
                    if st.button(f"✅ Approve", type="primary"):
                        if crud.approve_spec_sheet(task_id, edited_spec_sheet):
                            st.success("Task {} approved!".format(task_id))
                            st.rerun() # Rerun to show the next UI state
                        else:
                            st.error("Failed to approve task.")

                with b_col3:
                    if st.button(f"❌ Reject"):
                        crud.update_task_status(task_id, 'REJECTED')
                        st.session_state['current_task_id'] = None
                        st.switch_page("pages/1_Dashboard.py")

        # --- Other status UIs (APPROVED, GENERATING, etc.) remain the same ---
        elif task['status'] == 'APPROVED':
            st.info("This task is approved. Please review the final prompt and original images before generating.")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Images for Reference")
                image_paths_str = task.get('uploaded_image_paths', '')
                if image_paths_str:
                    for path in image_paths_str.split(','):
                        st.image(Image.open(path), caption=os.path.basename(path))
            with col2:
                st.subheader("Final Prompt for Generation")
                base_model_prompt = "professional photograph of a female model wearing the garment, full body shot, studio lighting, hyperrealistic, 8k"
                final_prompt = f"{base_model_prompt}, {task.get('spec_sheet_text', '')}"
                st.text_area("This prompt will be sent to the image generation AI:", value=final_prompt, height=400, disabled=True)
            st.divider()
            if st.button(f"🚀 Generate On-Model Photo", type="primary"):
                crud.update_task_status(task_id, 'GENERATING')
                st.rerun()

        elif task['status'] == 'GENERATING':
            st.info(f"⚙️ Calling Stable Diffusion... This can take up to a minute. Please do not navigate away from this page.")
            with st.spinner("Generating image..."):
                base_model_prompt = "professional photograph of a female model wearing the garment, full body shot, studio lighting, hyperrealistic, 8k"
                final_prompt = f"{base_model_prompt}, {task.get('spec_sheet_text', '')}"
                generated_path = ai_services.generate_image_from_prompt(final_prompt, task['product_code'])
                if "Error" in generated_path:
                    st.error(generated_path)
                    crud.update_task_status(task_id, 'ERROR')
                else:
                    crud.add_generated_image_to_task(task_id, final_prompt, generated_path)
                    st.success("Image generated successfully!")
            st.rerun()

        elif task['status'] in ['PENDING_IMAGE_REVIEW', 'PENDING_REDO']:
            st.info("Review the generated image. You can approve it or request a redo with additional instructions.")
            if task.get('generated_image_path') and os.path.exists(task['generated_image_path']):
                st.image(Image.open(task['generated_image_path']), caption="Latest Generated Image", use_container_width=True)
            redo_prompt = st.text_input("Additional instructions for redo (e.g., 'make the background darker', 'change model's hair to blonde'):")
            r_col1, r_col2, _ = st.columns([1,1,5])
            if r_col1.button(f"✅ Complete Task", type="primary"):
                crud.update_task_status(task_id, 'COMPLETED')
                st.success("Task {} has been marked as complete!".format(task_id))
                st.balloons()
                st.session_state['current_task_id'] = None
                st.switch_page("pages/1_Dashboard.py")
            if r_col2.button(f"🔄 Request Redo"):
                if not redo_prompt:
                    st.warning("Please provide instructions for the redo.")
                else:
                    new_prompt = f"{task.get('final_prompt', '')}, {redo_prompt}"
                    crud.update_task_status(task_id, 'GENERATING')
                    st.rerun()
else:
    st.error("No task selected. Please go back to the dashboard and select a task to review.")
