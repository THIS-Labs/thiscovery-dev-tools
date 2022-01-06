#!/bin/bash

# Rotate your AWS access key id and secret access key.
#
# Note that the credentials file needs a [default] account,
#   the values can be exactly the same as the usual Administrator access account
#
# Also note that you will need to create an IAM user (sophie in this example)
#   and put them in an Administrator group. It's this user's key that you will rotate.


USER='sophie'
ACCOUNT_ID='623819932980_AdministratorAccess'
NEW_KEY_FILE="$HOME/.aws/new-access-key.json"
OLD_KEY_FILE="$HOME/.aws/old-access-key.json"
CREDENTIALS_FILE="$HOME/.aws/credentials"

# Retrieve Old credentials
echo 'Getting existing key...'
AWS iam list-access-keys --user-name $USER > "$OLD_KEY_FILE"

# Create new key
echo 'Creating new key...'
AWS iam create-access-key --user-name $USER > "$NEW_KEY_FILE"

# Backup old credentials
cp "$CREDENTIALS_FILE" "$HOME/.aws/credentials-backup"

# SET new access keys and new secret variables
NEW_ACCESS_KEY=$(grep -o '"AccessKeyId": "[^"]*' "$NEW_KEY_FILE" | grep -o '[^"]*$')
NEW_ACCESS_SECRET=$(grep -o '"SecretAccessKey": "[^"]*' "$NEW_KEY_FILE" | grep -o '[^"]*$')

# store the new key
echo 'Storing new key...'

echo '[default]' > "$CREDENTIALS_FILE"
echo 'aws_access_key_id = ' "$NEW_ACCESS_KEY" >> "$CREDENTIALS_FILE"
echo 'aws_secret_access_key = ' "$NEW_ACCESS_SECRET" >> "$CREDENTIALS_FILE"
echo '' >> "$CREDENTIALS_FILE"
echo "[$ACCOUNT_ID]" >> "$CREDENTIALS_FILE"
echo 'aws_access_key_id = ' "$NEW_ACCESS_KEY" >> "$CREDENTIALS_FILE"
echo 'aws_secret_access_key = ' "$NEW_ACCESS_SECRET" >> "$CREDENTIALS_FILE"
sleep 10

# Delete old key
OLD_ACCESS_KEY=$(grep -o '"AccessKeyId": "[^"]*' "$OLD_KEY_FILE" | grep -o '[^"]*$')

echo 'Removing old key from AWS...'
AWS iam delete-access-key --user-name $USER --access-key-id "$OLD_ACCESS_KEY"

# Cleanup
rm "$NEW_KEY_FILE"
rm "$OLD_KEY_FILE"
