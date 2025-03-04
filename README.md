# Automating Kerberos Ticket Renewal with a Cron Job

This guide explains how to generate a Kerberos keytab, create a script to renew Kerberos tickets, and automate the renewal process using a cron job.

---

## 1. Generate a Keytab

Instead of storing a password, generate a **Kerberos keytab** file.

### **Step 1: Open `ktutil`**
Run the following command:

```bash
ktutil
```

### **Step 2: Add an Entry to the Keytab**
Inside the interactive shell, run:

```bash
addent -password -p user@ACCT.UPMCHS.NET -k 1 -e aes256-cts-hmac-sha1-96
```
It will prompt you for a password:
```
Password for user@ACCT.UPMCHS.NET:
```
Enter your password and press **Enter**.

### **Step 3: Write the Keytab File**
```bash
wkt user.keytab
quit
```

### **Step 4: Move the Keytab to a Secure Location**
Before moving the keytab, **ensure the `.keytabs` directory exists**:

```bash
mkdir -p ~/.keytabs
```

Then, move the keytab file:

```bash
mv user.keytab ~/.keytabs/
chmod 600 ~/.keytabs/user.keytab
```
This ensures the keytab is stored securely with restricted permissions.

---

## 2. Create a Script to Renew Kerberos Tickets
Create a script named `renew_ticket.sh` to automate ticket renewal.

### **Step 1: Create the Script**

```bash
nano ~/renew_ticket.sh
```

Paste the following content:

```bash
#!/bin/bash
export KRB5CCNAME=$(klist | awk '/Ticket cache:/ {print $3}' | sed 's/FILE://')
/usr/bin/kinit -k -t ~/.keytabs/user.keytab user@ACCT.UPMCHS.NET
```

### **Step 2: Make the Script Executable**
```bash
chmod +x ~/renew_ticket.sh
```

---

## 3. Add a Cron Job for Automatic Ticket Renewal

To ensure the ticket is renewed automatically, set up a cron job.

### **Step 1: Edit Crontab**
```bash
crontab -e
```

### **Step 2: Add the Following Line**
```bash
0 */6 * * * /home/user/renew_ticket.sh
```
This will run `renew_ticket.sh` **every 6 hours** to keep the ticket valid.

### **Step 3: Verify the Cron Job**
To confirm that the cron job is scheduled:
```bash
crontab -l
```

---

## Testing the Setup
After setting everything up, manually test it:
```bash
./renew_ticket.sh
klist
```
If successful, `klist` should show an updated **Valid starting** timestamp.

---

## Security Considerations
- **Never store passwords in plaintext scripts** – Using a keytab is much safer.
- **Restrict permissions** on the keytab file (`chmod 600 ~/.keytabs/user.keytab`).
- **Use a dedicated ticket cache for cron jobs**, which the script handles automatically.

---

## Troubleshooting
- If you get `Permission denied` when running the script:
  ```bash
  chmod +x ~/renew_ticket.sh
  ```
- If `klist` does not show an updated ticket, verify that the keytab is correct:
  ```bash
  kinit -k -t ~/.keytabs/user.keytab user@ACCT.UPMCHS.NET
  klist
  ```
- If the cron job is not running, check the cron logs:
  ```bash
  grep CRON /var/log/syslog
  ```

# NIFTI Processing Scripts Documentation

## Overview
These scripts are used for processing MRI scan data, converting DICOM files to NIFTI format, organizing scan data, and updating a master spreadsheet with scan information. They are designed to work with the R2D3 study directory structure and integrate with external tools like `dcm2niix` and Excel.

---

## Script 1: niftiConverted.py

### Description
This script scans a designated raw MRI folder for new scans, converts them into NIFTI format using `dcm2niix`, organizes them into a structured folder, and updates an Excel sheet with relevant metadata.

### Dependencies
- Python 3
- `openpyxl` (for handling Excel files)
- `shutil`, `subprocess`, and `os` (for file handling and execution)

### File Paths
- **Raw Folder Path:** `/mnt/argo/Studies/R2D3/Public/Analysis/raw`
- **Rsync Folder Path:** `/mnt/argo/Studies/R2D3/Public/Analysis/raw/raw_mri/WPC-9080`
- **Excel File Path:** `/mnt/argo/Studies/R2D3/Public/Analysis/misc/spreadsheets/R2D3_Master.xlsx`

### Key Functionalities
1. **Verify Folder Paths** - Ensures that necessary directories exist before proceeding.
2. **Extract Scan Dates** - Identifies new scan folders from `rsyncFolderPath`.
3. **DICOM to NIFTI Conversion** - Uses `dcm2niix` to convert raw DICOM files.
4. **Organize NIFTI Files** - Moves converted NIFTI files to a structured directory.
5. **Update Excel Spreadsheet** - Appends metadata including Subject ID, Scan ID, and timestamps.

### Execution
Run the script using:
```sh
python niftiConverted.py
```

### Example Log Output
```
NIFTI_Creator script started...
Contents of /mnt/argo/Studies/R2D3/Public/Analysis/raw/raw_mri/WPC-9080: ['2025.03.01']
Extracted scanDates: ['2025.03.01']
Entering directory: /mnt/argo/Studies/R2D3/Public/Analysis/raw/raw_mri/WPC-9080/2025.03.01
Current subjID is: SP000
Current scanID is: 1
Running dcm2niix: /home/hudlowe/anaconda3/.../dcm2niix -f "%d" -z n -b n -s y "input_folder"
Added new row to Excel: ['SP000', '1', '2025-03-01 12:00:00', '2025-03-01 12:00:00']
Excel file saved successfully.
Conversion Completed!
```

---

## Script 2: organize.py

### Description
This script organizes scan files into a structured dataset, updates a master spreadsheet with scan details, and ensures consistency in the study directory structure. It is designed to work non-interactively and integrate with an existing dataset.

### Dependencies
- Python 3
- `pandas` (for handling spreadsheet data)
- `shutil`, `os` (for file manipulation)

### File Paths
- **Master Spreadsheet:** `/mnt/argo/Studies/R2D3/Public/Analysis/misc/spreadsheets/R2D3_Master.xlsx`
- **Scan Structure Sheet:** `/mnt/argo/Studies/R2D3/Public/Analysis/misc/spreadsheets/R2D3_FileStruc.xlsx`
- **Study Directory:** `/mnt/argo/Studies/R2D3/`

### Key Functionalities
1. **Identify Subject Index** - Locates the subject and scan ID in the master spreadsheet.
2. **Auto-fill Scan Paths** - Finds and assigns scan paths based on predefined rules.
3. **Organize Data** - Moves and structures scan data in the correct directories.
4. **Update Master Spreadsheet** - Logs the processing date and scan availability status.

### Execution
Run the script using:
```sh
python organize.py
```

### Example Log Output
```
Processing study directory: /mnt/argo/Studies/R2D3/Public/Analysis/raw/NIFTI_Converted
Skipping SP000_1 as it has already been processed.
Successfully organized SP001_1.
```

---

## Notes
- Ensure `dcm2niix` is installed and accessible in the specified path.
- Verify that the required Excel sheets exist before running the scripts.
- Both scripts assume a specific directory structure; modifying file paths may require updates to the code.
