#!/bin/bash

# Set a consistent Kerberos cache location
export KRB5CCNAME=FILE:/tmp/krb5cc_youruser

# Path to your keytab file
KEYTAB=~/.keytabs/youruser.keytab
PRINCIPAL=youruser@YOUR.UPMC.CREDENTIALS

# Try renewing existing ticket; if that fails, acquire a new one using the keytab
/usr/bin/kinit -R 2>/dev/null || /usr/bin/kinit -k -t "$KEYTAB" "$PRINCIPAL"

# Print confirmation
echo ">> Showing ticket cache:"
/usr/bin/klist

# Optionally, request service tickets for CIFS shares
# Uncomment and update these lines as needed
# /usr/bin/kvno cifs/SERVER1.UPMC
# /usr/bin/kvno cifs/SERVER2.UPMC 

# Run your downstream scripts (adjust paths as needed)
/usr/bin/python /path/to/niftiConverted.py >> /path/to/niftiConverted.log 2>&1
/usr/bin/python /path/to/organize.py >> /path/to/organize.log 2>&1

