# Imgur Upload

A utility for creating Imgur albums and uploading images.

## User Setup

To use this application, you must first register with Imgur and provide valid client credetials.

1. While logged in to Imgur, visit https://api.imgur.com/oauth2/addclient
2. Populate and submit the form:
    - `Application name`: anything
    - `Authorization callback URL`: https://imgur.com
    - `Email`: your email address
    - `Description`: something like "Basic app to upload images."
3. Copy the Client ID and Client Secret into the prompts.

If you do not upload anonymously, you will be prompted with an OAuth flow on the first execution.

For help, run the program in a terminal with the -h option.