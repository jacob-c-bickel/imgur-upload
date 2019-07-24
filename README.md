# Imgur Upload

A utility for creating Imgur albums and uploading images.

## User Setup

To use this application, you must first register with Imgur and update the
creds.json file with your Client ID and Client Secret.

1. Register an application.
    - While logged in to Imgur, visit https://api.imgur.com/oauth2/addclient
    - Populate the form:
        - `Application name`: anything
        - `Authorization callback URL`: https://imgur.com
        - `Email`: your email address
        - `Description`: something like "Basic app to upload images."
    - Click Submit.

2. Update creds.json.
    - After submitting, you will see your Client ID and Client Secret.
    - Open creds.json in a text editor.
    - Copy the Client ID and Client Secret into the appropriate places in creds.json (leave the double quotes).

If you do not upload anonymously, you will be prompted with an OAuth flow on
the first execution.

For help, run the program in a terminal with the -h option.