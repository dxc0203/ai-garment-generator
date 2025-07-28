# File: app/core/workflow_manager.py

from app.database import crud
from app.core import ai_services

def bulk_generate_images(task_ids: list):
    """
    Handles the logic for bulk-generating images for selected tasks.
    It will only process tasks that are in the 'APPROVED' status.
    """
    if not task_ids:
        return "No tasks were selected."

    # 1. Filter for tasks that are actually ready for generation
    approved_tasks_to_process = []
    for task_id in task_ids:
        task = crud.get_task_by_id(task_id)
        if task and task['status'] == 'APPROVED':
            approved_tasks_to_process.append(task)
    
    if not approved_tasks_to_process:
        return "No tasks with 'APPROVED' status were selected."

    # 2. Update status of all selected tasks to 'GENERATING' first
    # This provides immediate feedback to the user on the dashboard.
    for task in approved_tasks_to_process:
        crud.update_task_status(task['id'], 'GENERATING')

    # 3. Now, process each task one by one
    success_count = 0
    error_count = 0
    for task in approved_tasks_to_process:
        print(f"Generating image for Task ID: {task['id']}...")
        
        # Reconstruct the final prompt
        base_model_prompt = "professional photograph of a female model wearing the garment, full body shot, studio lighting, hyperrealistic, 8k"
        final_prompt = f"{base_model_prompt}, {task['spec_sheet_text']}"
        
        # Call the AI service
        generated_path = ai_services.generate_image_from_prompt(final_prompt, task['product_code'])
        
        # Process the result
        if "Error" in generated_path:
            crud.update_task_status(task['id'], 'ERROR')
            error_count += 1
        else:
            crud.add_generated_image_to_task(task['id'], final_prompt, generated_path)
            success_count += 1
            
    return f"Bulk generation complete. Success: {success_count}, Errors: {error_count}."

