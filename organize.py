#!/usr/bin/python
import os
import shutil
import pandas as pd
from datetime import datetime

def get_index(master_df, subj_list):
    """Find the index of a subject ID and scan ID in the master spreadsheet."""
    if "_" in subj_list:
        subj_id, scan_id = subj_list.rsplit("_", 1)  # Split subject ID and scan ID
    else:
        print(f"Invalid subject format: {subj_list}")
        return None
    
    matches = master_df[(master_df['Vault_UID'].astype(str) == subj_id) & (master_df['Vault_ScanID'].astype(str) == scan_id)]
    return matches.index[0] if not matches.empty else None

def auto_fill_function(session_dir, subj_list, organize_df):
    """Autofill scan paths based on identifiers and exclusion criteria."""
    raw_dir = os.path.join(session_dir, subj_list)
    
    if not os.path.isdir(raw_dir):
        raise FileNotFoundError(f"Error: The following folder does not exist: {raw_dir}")
    
    subj_folder_names = [f for f in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, f))]
    
    scan_paths = []
    for _, row in organize_df.iterrows():
        id = str(row['ID']) if pd.notna(row['ID']) else ""
        scan_name = str(row['scan_name']) if pd.notna(row['scan_name']) else ""
        excluder = str(row['exclude']) if pd.notna(row['exclude']) else ""
        
        matching_scans = [scan for scan in subj_folder_names if id in scan and (not excluder or excluder not in scan)]
        
        if len(matching_scans) > 1:
            selected_scan = matching_scans[0]  # Non-interactive: choose first match
        elif not matching_scans:
            selected_scan = 'EMPTY'
        else:
            selected_scan = matching_scans[0]
        
        scan_paths.append(os.path.join(raw_dir, selected_scan) if selected_scan != 'EMPTY' else 'EMPTY')
    
    return scan_paths

def main_organize(output_df, study_dir, master_fname, subj_list):
    """Organize MRI scan files and update the master spreadsheet."""
    data_dir = os.path.join(study_dir, 'Public', 'Analysis', 'data')
    
    master_df = pd.read_excel(master_fname)
    row_num = get_index(master_df, subj_list)
    
    if row_num is None:
        print(f"Error: Subject {subj_list} not found in master spreadsheet.")
        return
    
    if 'data_organize_date' not in master_df.columns:
        master_df['data_organize_date'] = pd.NaT
    
    for _, row in output_df.iterrows():
        scan_type = f"{row['scan_folder']}_exists"
        scan_path = row['scan_filepath']
        
        if scan_type not in master_df.columns:
            master_df[scan_type] = float('nan')
        
        if os.path.isfile(scan_path):
            master_df.at[row_num, scan_type] = 1
            subj_id, scan_id = subj_list.rsplit("_", 1)
            dest_dir = os.path.join(data_dir, f'{subj_id}_{scan_id}', 'converted', row['scan_folder'])
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy(scan_path, os.path.join(dest_dir, row['scan_name']))
        else:
            master_df.at[row_num, scan_type] = 0
    
    master_df.at[row_num, 'data_organize_date'] = datetime.today()
    master_df.to_excel(master_fname, index=False)
    print(f"Successfully organized {subj_list}.")

def process_study(master_sheet, scan_sheet, directory):
    """Process a study without GUI interaction."""
    master_df = pd.read_excel(master_sheet)
    scan_df = pd.read_excel(scan_sheet)
    organize_df = scan_df.rename(columns={"folder": "scan_folder", "name": "scan_name", "identifier": "ID", "exclude": "exclude", "path": "scan_filepath"})
    
    nifticonverted_dir = os.path.join(directory, 'Public', 'Analysis', 'raw', 'NIFTI_Converted')
    
    for session_folder in sorted(os.listdir(nifticonverted_dir)):
        session_path = os.path.join(nifticonverted_dir, session_folder)
        if not os.path.isdir(session_path):
            continue
        
        for subj_folder in os.listdir(session_path):
            subj_list = subj_folder  # This follows the subjID_sessID naming convention
            subject_path = os.path.join(session_path, subj_folder)
            
            row_num = get_index(master_df, subj_list)
            
            if row_num is not None and pd.notna(master_df.at[row_num, 'data_organize_date']):
                print(f"Skipping {subj_list} as it has already been processed.")
                continue
            
            scan_paths = auto_fill_function(session_path, subj_list, organize_df)
            organize_df['scan_filepath'] = scan_paths
            main_organize(organize_df, directory, master_sheet, subj_list)

if __name__ == "__main__":
    MASTER_SHEET = "/mnt/argo/Studies/R2D3/Public/Analysis/misc/spreadsheets/R2D3_Master.xlsx"
    SCAN_SHEET = "/mnt/argo/Studies/R2D3/Public/Analysis/misc/spreadsheets/R2D3_FileStruc.xlsx"
    DIRECTORY = "/mnt/argo/Studies/R2D3/"
    
    process_study(MASTER_SHEET, SCAN_SHEET, DIRECTORY)

