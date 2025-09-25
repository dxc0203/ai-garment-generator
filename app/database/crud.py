# File: app/database/crud.py
import sqlite3
import os
import json
from .models import create_connection

# --- Task Functions ---
def create_task(product_code, uploaded_image_paths, batch_id):
    conn = create_connection()
    if conn is None: return None
    paths_str = ",".join(uploaded_image_paths)
    sql = ''' INSERT INTO tasks(product_code, uploaded_image_paths, status, batch_id) VALUES(?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (product_code, paths_str, 'NEW', batch_id))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def update_task_status(task_id, new_status):
    conn = create_connection()
    if conn is None: return False
    sql = ''' UPDATE tasks SET status = ? WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, (new_status, task_id))
        conn.commit()
        return True
    finally:
        conn.close()

def get_task_by_id(task_id):
    conn = create_connection()
    if conn is None: return None
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        task = cur.fetchone()
        return dict(task) if task else None
    finally:
        conn.close()

def get_all_tasks():
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def delete_tasks_by_ids(task_ids: list):
    conn = create_connection()
    if conn is None or not task_ids: return False
    for task_id in task_ids:
        task = get_task_by_id(task_id)
        if task:
            if task.get('uploaded_image_paths'):
                for path in task['uploaded_image_paths'].split(','):
                    if os.path.exists(path): os.remove(path)
            if task.get('generated_image_path'):
                if os.path.exists(task['generated_image_path']): os.remove(task['generated_image_path'])
    try:
        cur = conn.cursor()
        placeholders = ','.join('?' for _ in task_ids)
        cur.execute(f'DELETE FROM spec_sheet_versions WHERE task_id IN ({placeholders})', task_ids)
        cur.execute(f'DELETE FROM tasks WHERE id IN ({placeholders})', task_ids)
        conn.commit()
        return True
    finally:
        conn.close()

def update_task_with_ai_data(task_id, product_name, tags_dict):
    conn = create_connection()
    if conn is None: return False
    tags_str = json.dumps(tags_dict)
    sql = ''' UPDATE tasks SET product_name = ?, product_tags = ? WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, (product_name, tags_str, task_id))
        conn.commit()
        return True
    finally:
        conn.close()

# --- Spec Sheet Version Functions ---
def create_spec_sheet_version(task_id, spec_text, author="AI"):
    conn = create_connection()
    if conn is None: return None
    cur = conn.cursor()
    cur.execute("SELECT MAX(version_number) FROM spec_sheet_versions WHERE task_id = ?", (task_id,))
    max_version = cur.fetchone()[0]
    next_version = 1 if max_version is None else max_version + 1
    sql = '''INSERT INTO spec_sheet_versions(task_id, version_number, spec_text, author) VALUES(?,?,?,?)'''
    try:
        cur.execute(sql, (task_id, next_version, spec_text, author))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_spec_sheet_versions(task_id):
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM spec_sheet_versions WHERE task_id = ? ORDER BY version_number ASC", (task_id,))
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def add_initial_spec_sheet(task_id, spec_sheet_text):
    create_spec_sheet_version(task_id, spec_sheet_text, author="AI")
    conn = create_connection()
    if conn is None: return False
    sql = ''' UPDATE tasks SET spec_sheet_text = ?, status = ? WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, (spec_sheet_text, 'PENDING_APPROVAL', task_id))
        conn.commit()
        return True
    finally:
        conn.close()

def save_spec_sheet_edit(task_id, edited_spec_text):
    versions = get_spec_sheet_versions(task_id)
    latest_version_text = versions[-1]['spec_text'] if versions else ""
    if edited_spec_text != latest_version_text:
        create_spec_sheet_version(task_id, edited_spec_text, author="USER")
    conn = create_connection()
    if conn is None: return False
    sql = ''' UPDATE tasks SET spec_sheet_text = ? WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, (edited_spec_text, task_id))
        conn.commit()
        print(f"Saved edits for task {task_id}.")
        return True
    finally:
        conn.close()

def approve_spec_sheet(task_id, final_spec_text):
    save_spec_sheet_edit(task_id, final_spec_text)
    return update_task_status(task_id, 'APPROVED')

def add_generated_image_to_task(task_id, final_prompt, generated_image_path, redo_prompt=""):
    conn = create_connection()
    if conn is None: return False
    sql = ''' UPDATE tasks SET final_prompt = ?, generated_image_path = ?, redo_prompt = ?, status = ? WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, (final_prompt, generated_image_path, redo_prompt, 'PENDING_IMAGE_REVIEW', task_id))
        conn.commit()
        return True
    finally:
        conn.close()

# --- Translation Cache Functions (REMOVED) ---
# All translation-related functions have been removed:
# - get_translation()
# - add_translation()
# - purge_old_translations()
# - get_all_unique_source_texts()

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
    return sorted(list(unique_tags))
