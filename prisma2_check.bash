#!/bin/bash

# Set base directory
BASE_DIR="/mnt/argo/Studies/R2D3/Public/Analysis/raw/raw_mri/WPC-9080"
OUTPUT_FILE="matching_scans.txt"
DEBUG_FILE="debug_log.txt"
TEMP_FILE="temp_matching_scans.txt"

# Clear output files
> "$DEBUG_FILE"
> "$TEMP_FILE"

# Loop through each scan date directory
for DATE_DIR in "$BASE_DIR"/*; do
    if [[ -d "$DATE_DIR" ]]; then
        # Extract scan date from directory name
        SCAN_DATE=$(basename "$DATE_DIR" | cut -d'-' -f1)

        echo "Checking: $SCAN_DATE" >> "$DEBUG_FILE"

        # Loop through subject/session directories
        for SUBJ_DIR in "$DATE_DIR"/*; do
            if [[ -d "$SUBJ_DIR" ]]; then
                # Loop through acquisition folders
                for ACQ_DIR in "$SUBJ_DIR"/*; do
                    if [[ -d "$ACQ_DIR" ]]; then
                        # Get the first DICOM file (any file in folder)
                        FIRST_DICOM=$(find "$ACQ_DIR" -type f | head -n 1)

                        if [[ -n "$FIRST_DICOM" ]]; then
                            # Extract scanner model and log output
                            SCANNER_MODEL=$(dicom_hinfo -tag 0008,1010 -no_name "$FIRST_DICOM" | tr -d '[:space:]')

                            echo "File: $FIRST_DICOM -> Scanner: $SCANNER_MODEL" >> "$DEBUG_FILE"

                            # Check if scanner matches AWP167046
                            if [[ "$SCANNER_MODEL" == "AWP167046" ]]; then
                                echo "$SCAN_DATE" >> "$TEMP_FILE"
                                echo "MATCH FOUND: $SCAN_DATE" >> "$DEBUG_FILE"
                            fi
                        else
                            echo "No DICOM found in $ACQ_DIR" >> "$DEBUG_FILE"
                        fi
                    fi
                done
            fi
        done
    fi
done

# Remove duplicates and save unique dates
sort -u "$TEMP_FILE" > "$OUTPUT_FILE"
rm "$TEMP_FILE"

echo "Script finished. Unique matching scan dates saved in $OUTPUT_FILE. Debug log in $DEBUG_FILE."

