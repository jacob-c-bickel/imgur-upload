import argparse
import glob
import json
import os
import sys
import time
import urllib
import webbrowser

from imgurpython import ImgurClient

dirname = os.path.dirname(__file__)

class App:
    def __init__(self):
        self.client = None


    def check_client_credentials(self):
        with open(os.path.join(dirname,"creds.json"), "r") as f:
            stored_creds = json.load(f)
        if stored_creds["client_id"] == "YOUR_CLIENT_ID" or \
                stored_creds["client_secret"] == "YOUR_CLIENT_SECRET":
            print("Error: No client credentials found. ", end="")
            print("You must first register an applicaton with Imgur. ", end="")
            print("See README.md for help. ")
            input("press enter to exit...")
            sys.exit(0)


    def init_client(self, anon):
        with open("creds.json", "r") as file_in:
            stored_creds = json.load(file_in)

        self.client = ImgurClient(
            stored_creds["client_id"],
            stored_creds["client_secret"]
        )

        if not anon:
            if "refresh_token" in stored_creds:
                # Authorize using stored creds.
                self.client.set_user_auth(
                    stored_creds["access_token"],
                    stored_creds["refresh_token"]
                )
            else:
                # User OAuth flow.
                print("Please follow the OAuth flow and enter the pin...")
                time.sleep(2)
                webbrowser.open(self.client.get_auth_url("pin"))
                pin = input("Enter pin: ")

                # Authorize using new creds.
                credentials = self.client.authorize(pin, "pin")
                self.client.set_user_auth(
                    credentials["access_token"],
                    credentials["refresh_token"]
                )

                # Update creds file.
                stored_creds["access_token"] = credentials["access_token"]
                stored_creds["refresh_token"] = credentials["refresh_token"]
                with open(os.path.join(dirname, "creds.json"), "w") as f:
                    json.dump(stored_creds, f, indent=2)


    def arg_form(self):
        print("Imgur Upload\n")
        
        print("Targets may be a url, filepath, or directory.")
        targets = []
        while True:
            target = input("Target: ")
            if not target:
                break
            targets.append(target)
        print("")

        title = input("Title: ")
        print("")

        description = input("Description: ")
        print("")

        anon = (input("Anonymous (y/n): ") == "y")
        print("")

        return argparse.Namespace(targets=targets, title=title,
                description=description, anon=anon)


    def create_album(self, targets, title, description):
        print("Creating album... ", end="", flush=True)
        album = self.client.create_album({
            "title": title,
            "description": description
        })
        print(f"done. (id={album['id']})")

        config = { "album": album["deletehash"] }

        # If there is only one image, add title/description to the image also.
        if len(targets) == 1:
            config["title"] = title
            config["description"] = description

        images = []
        for target in targets:
            # URL upload.
            if urllib.parse.urlparse(target).scheme in ("http", "https"):
                image = self.upload_image(config, url=target)
                if image is not None:
                    images.append(image)
            # File upload.
            elif os.path.isfile(target):
                image = self.upload_image(config, path=target)
                if image is not None:
                    images.append(image)
            # Directory upload.
            elif os.path.isdir(target):
                for filepath in glob.glob(f"{target}/**"):
                    image = self.upload_image(config, path=filepath)
                    if image is not None:
                        images.append(image)
            else:
                print(f"*** Invalid target: {target} ***")

        return {
            "album_id": album["id"],
            "image_ids": [i["id"] for i in images]
        }


    def upload_image(self, config, url=None, path=None):
        try:
            if url is not None:
                print(f"Uploading {url}... ", end="", flush=True)
                image = self.client.upload_from_url(url, config=config)
            elif path is not None:
                print(f"Uploading {path}... ", end="", flush=True)
                image = self.client.upload_from_path(path, config=config)
            else:
                return
        except Exception as e:
            print(f"failed.\n*** {e} ***")
            return

        print(f"done. (id={image['id']})")
        return image


    def run(self, args=None):
        self.check_client_credentials()

        if args is None:
            args = self.arg_form()

        self.init_client(args.anon)

        res = self.create_album(args.targets, args.title, args.description)
        print(f"\nAlbum: https://imgur.com/a/{res['album_id']}")
        if res['image_ids']:
            print(f"First Image: https://imgur.com/{res['image_ids'][0]}.png")
        print("")

        print(self.client.credits)
        print("")

        input("press enter to exit...")


def main():
    app = App()
    if len(sys.argv) == 1:
        app.run()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "targets",
            metavar="target",
            nargs="+",
            help="directory, filepath, or url to upload"
        )
        parser.add_argument(
            "-t", "--title",
            dest="title",
            metavar="title",
            help="post's title"
        )
        parser.add_argument(
            "-d", "--description",
            dest="description",
            metavar="desc",
            help="post's description"
        )
        parser.add_argument(
            "-a", "--anonymous",
            dest="anon",
            action="store_const", const=True, default=False,
            help="anonymously upload (no imgur account)"
        )
        app.run(args=parser.parse_args())