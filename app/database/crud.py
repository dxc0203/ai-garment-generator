# File: app/database/crud.py
import sqlite3
import os
import json
import logging
from ..validation import validate_sku
from .models import get_db_connection

logger = logging.getLogger(__name__)

# --- Task Functions ---
def create_task(product_code, uploaded_image_paths, batch_id):
    # Validate product code
    is_valid, error_msg = validate_sku(product_code)
    if not is_valid:
        logger.error(f"Invalid product code: {error_msg}")
        return None

    try:
        with get_db_connection() as conn:
            paths_str = ",".join(uploaded_image_paths)
            sql = ''' INSERT INTO tasks(product_code, uploaded_image_paths, status, batch_id) VALUES(?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, (product_code, paths_str, 'NEW', batch_id))
            task_id = cur.lastrowid
            logger.info(f"Created new task with ID {task_id} for product code {product_code}")
            return task_id
    except sqlite3.Error as e:
        logger.error(f"Failed to create task for product code {product_code}: {e}")
        return None

def update_task_status(task_id, new_status):
    try:
        with get_db_connection() as conn:
            sql = ''' UPDATE tasks SET status = ? WHERE id = ?'''
            cur = conn.cursor()
            cur.execute(sql, (new_status, task_id))
            logger.info(f"Updated task {task_id} status to {new_status}")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to update task {task_id} status to {new_status}: {e}")
        return False

def get_task_by_id(task_id):
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
            task = cur.fetchone()
            if task:
                logger.debug(f"Retrieved task {task_id}")
                return dict(task)
            else:
                logger.warning(f"Task {task_id} not found")
                return None
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve task {task_id}: {e}")
        return None

def get_all_tasks():
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cur.fetchall()
            tasks = [dict(row) for row in rows]
            logger.info(f"Retrieved {len(tasks)} tasks from database")
            return tasks
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve all tasks: {e}")
        return []

def delete_tasks_by_ids(task_ids: list):
    if not task_ids:
        return False

    deleted_files = 0
    # First, collect file paths to delete (before transaction)
    files_to_delete = []
    for task_id in task_ids:
        task = get_task_by_id(task_id)
        if task:
            if task.get('uploaded_image_paths'):
                for path in task['uploaded_image_paths'].split(','):
                    if os.path.exists(path):
                        files_to_delete.append(path)
            if task.get('generated_image_path'):
                if os.path.exists(task['generated_image_path']):
                    files_to_delete.append(task['generated_image_path'])

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholders = ','.join('?' for _ in task_ids)
            cur.execute(f'DELETE FROM spec_sheet_versions WHERE task_id IN ({placeholders})', task_ids)
            cur.execute(f'DELETE FROM tasks WHERE id IN ({placeholders})', task_ids)
            logger.info(f"Deleted {len(task_ids)} tasks from database")

        # Delete files after successful database transaction
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_files += 1
                logger.debug(f"Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {file_path}: {e}")

        logger.info(f"Successfully deleted {len(task_ids)} tasks and {deleted_files} associated files")
        return True

    except sqlite3.Error as e:
        logger.error(f"Failed to delete tasks {task_ids}: {e}")
        return False

def update_task_with_ai_data(task_id, product_name, tags_dict):
    try:
        with get_db_connection() as conn:
            tags_str = json.dumps(tags_dict)
            sql = ''' UPDATE tasks SET product_name = ?, product_tags = ? WHERE id = ?'''
            cur = conn.cursor()
            cur.execute(sql, (product_name, tags_str, task_id))
            logger.info(f"Updated task {task_id} with AI data: product_name='{product_name}', tags_count={len(tags_dict)}")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to update task {task_id} with AI data: {e}")
        return False

# --- Spec Sheet Version Functions ---
def create_spec_sheet_version(task_id, spec_text, author="AI"):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT MAX(version_number) FROM spec_sheet_versions WHERE task_id = ?", (task_id,))
            max_version = cur.fetchone()[0]
            next_version = 1 if max_version is None else max_version + 1
            sql = '''INSERT INTO spec_sheet_versions(task_id, version_number, spec_text, author) VALUES(?,?,?,?)'''
            cur.execute(sql, (task_id, next_version, spec_text, author))
            version_id = cur.lastrowid
            logger.info(f"Created spec sheet version {next_version} for task {task_id} by {author}")
            return version_id
    except sqlite3.Error as e:
        logger.error(f"Failed to create spec sheet version for task {task_id}: {e}")
        return None

def get_spec_sheet_versions(task_id):
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM spec_sheet_versions WHERE task_id = ? ORDER BY version_number ASC", (task_id,))
            rows = cur.fetchall()
            versions = [dict(row) for row in rows]
            logger.debug(f"Retrieved {len(versions)} spec sheet versions for task {task_id}")
            return versions
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve spec sheet versions for task {task_id}: {e}")
        return []

def add_initial_spec_sheet(task_id, spec_sheet_text):
    try:
        with get_db_connection() as conn:
            # First create the version
            cur = conn.cursor()
            cur.execute("SELECT MAX(version_number) FROM spec_sheet_versions WHERE task_id = ?", (task_id,))
            max_version = cur.fetchone()[0]
            next_version = 1 if max_version is None else max_version + 1
            sql = '''INSERT INTO spec_sheet_versions(task_id, version_number, spec_text, author) VALUES(?,?,?,?)'''
            cur.execute(sql, (task_id, next_version, spec_sheet_text, "AI"))

            # Then update the task
            sql = ''' UPDATE tasks SET spec_sheet_text = ?, status = ? WHERE id = ?'''
            cur.execute(sql, (spec_sheet_text, 'PENDING_APPROVAL', task_id))

            logger.info(f"Added initial spec sheet for task {task_id} and set status to PENDING_APPROVAL")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to add initial spec sheet for task {task_id}: {e}")
        return False

def save_spec_sheet_edit(task_id, edited_spec_text):
    versions = get_spec_sheet_versions(task_id)
    latest_version_text = versions[-1]['spec_text'] if versions else ""

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # Create new version if text changed
            if edited_spec_text != latest_version_text:
                cur.execute("SELECT MAX(version_number) FROM spec_sheet_versions WHERE task_id = ?", (task_id,))
                max_version = cur.fetchone()[0]
                next_version = 1 if max_version is None else max_version + 1
                sql = '''INSERT INTO spec_sheet_versions(task_id, version_number, spec_text, author) VALUES(?,?,?,?)'''
                cur.execute(sql, (task_id, next_version, edited_spec_text, "USER"))

            # Update the task
            sql = ''' UPDATE tasks SET spec_sheet_text = ? WHERE id = ?'''
            cur.execute(sql, (edited_spec_text, task_id))

            logger.info(f"Saved spec sheet edits for task {task_id}")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to save spec sheet edits for task {task_id}: {e}")
        return False

def approve_spec_sheet(task_id, final_spec_text):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # Save the edit (create version and update task)
            versions_result = get_spec_sheet_versions(task_id)
            latest_version_text = versions_result[-1]['spec_text'] if versions_result else ""
            if final_spec_text != latest_version_text:
                cur.execute("SELECT MAX(version_number) FROM spec_sheet_versions WHERE task_id = ?", (task_id,))
                max_version = cur.fetchone()[0]
                next_version = 1 if max_version is None else max_version + 1
                sql = '''INSERT INTO spec_sheet_versions(task_id, version_number, spec_text, author) VALUES(?,?,?,?)'''
                cur.execute(sql, (task_id, next_version, final_spec_text, "USER"))

            sql = ''' UPDATE tasks SET spec_sheet_text = ? WHERE id = ?'''
            cur.execute(sql, (final_spec_text, task_id))

            # Update status
            sql = ''' UPDATE tasks SET status = ? WHERE id = ?'''
            cur.execute(sql, ('APPROVED', task_id))

            logger.info(f"Approved spec sheet for task {task_id}")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to approve spec sheet for task {task_id}: {e}")
        return False

def add_generated_image_to_task(task_id, final_prompt, generated_image_path, redo_prompt=""):
    try:
        with get_db_connection() as conn:
            sql = ''' UPDATE tasks SET final_prompt = ?, generated_image_path = ?, redo_prompt = ?, status = ? WHERE id = ?'''
            cur = conn.cursor()
            cur.execute(sql, (final_prompt, generated_image_path, redo_prompt, 'PENDING_IMAGE_REVIEW', task_id))
            logger.info(f"Added generated image to task {task_id} with status PENDING_IMAGE_REVIEW")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to add generated image to task {task_id}: {e}")
        return False

def get_all_unique_tags():
    all_tasks = get_all_tasks()
    unique_tags = set()
    for task in all_tasks:
        tags_str = task.get('product_tags')
        if tags_str:
            try:
                tags_dict = json.loads(tags_str)
                for key, value in tags_dict.items():
                    unique_tags.add(f"{key.title()}: {value}")
            except (json.JSONDecodeError, TypeError):
                continue
    result = sorted(list(unique_tags))
    logger.debug(f"Retrieved {len(result)} unique tags from {len(all_tasks)} tasks")
    return result
