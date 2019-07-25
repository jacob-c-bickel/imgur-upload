import argparse
import glob
import json
import os
import sys
import urllib
import webbrowser

from imgurpython import ImgurClient

dirname = os.path.dirname(__file__)


class App:
    def __init__(self):
        self.client = None


    def initialize_client(self):
        with open(os.path.join(dirname, "creds.json"), "r") as f:
            stored_creds = json.load(f)
            if "client_id" not in stored_creds:
                stored_creds["client_id"] = None
            if "client_secret" not in stored_creds:
                stored_creds["client_secret"] = None

        client_id = stored_creds["client_id"]
        client_secret = stored_creds["client_secret"]
        new_creds = False

        while True:
            try:
                self.client = ImgurClient(client_id, client_secret)
                break
            except:
                print("*** Missing or invalid client credentials. ", end="")
                print("You must first register an applicaton with Imgur ", end="")
                print("and provide the client id and secret. ", end="")
                print("See README.md for help.")
                client_id = input("Client ID: ")
                client_secret = input("Client secret: ")
                new_creds = True


        # Update creds file if there was a change.
        if new_creds:
            print("Client credentials successfully validated.\n")

            stored_creds["client_id"] = client_id
            stored_creds["client_secret"] = client_secret

            with open(os.path.join(dirname, "creds.json"), "w") as f:
                json.dump(stored_creds, f)


    def authorize_user(self):
        with open(os.path.join(dirname, "creds.json"), "r") as f:
            stored_creds = json.load(f)
            if "access_token" not in stored_creds:
                stored_creds["access_token"] = None
            if "refresh_token" not in stored_creds:
                stored_creds["refresh_token"] = None

        access_token = stored_creds["access_token"]
        refresh_token = stored_creds["refresh_token"]
        new_tokens = False
        
        while True:
            try:
                self.client.set_user_auth(access_token, refresh_token)
                break
            except:
                print("*** Missing or invalid tokens. ", end="")
                print("Please follow the OAuth flow and enter the pin.")
                webbrowser.open(self.client.get_auth_url("pin"))
                pin = input("Pin: ")

                try:
                    credentials = self.client.authorize(pin, "pin")
                except:
                    print("Invalid pin.")
                    continue

                access_token = credentials["access_token"]
                refresh_token = credentials["refresh_token"]
                new_tokens = True

        # Update creds file if there was a change.
        if new_tokens:
            print("Tokens successfully validated.\n")

            stored_creds["access_token"] = access_token
            stored_creds["refresh_token"] = refresh_token

            with open(os.path.join(dirname, "creds.json"), "w") as f:
                json.dump(stored_creds, f)


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
                images += filter(None, [self.upload_image(config, url=target)])
            # File upload.
            elif os.path.isfile(target):
                images += filter(None, [self.upload_image(config, path=target)])
            # Directory upload.
            elif os.path.isdir(target):
                for filepath in glob.glob(f"{target}/**"):
                    images += filter(None,
                            [self.upload_image(config, path=filepath)])
            else:
                print(f"*** Invalid target: {target} ***")

        print("========================================")

        print(f"Album: https://imgur.com/a/{album['id']}")
        if images:
            print(f"First Image: https://imgur.com/{images[0]['id']}.png")
        print("")

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


    def parse_args(self, raw_args):
        parser = argparse.ArgumentParser(raw_args)
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
        return parser.parse_args()


    def prompt_args(self):
        print("-- Targets may be a url, filepath, or directory.")
        targets = []
        while True:
            target = input("Target: ")
            if target:
                targets.append(target)
            else:
                break

        title = input("Title: ")
        description = input("Description: ")
        anon = (input("Anonymous (y/n): ") == "y")
        print("")

        return argparse.Namespace(targets=targets, title=title,
                description=description, anon=anon)


    def run(self, raw_args):
        self.initialize_client()

        if raw_args:
            interactive = False
            args = self.parse_args(raw_args)
        else:
            interactive = True
            args = self.prompt_args()

        if not args.anon:
            self.authorize_user()

        self.create_album(args.targets, args.title, args.description)

        print(self.client.credits)

        if interactive:
            input("press enter to exit...")


def main():
    app = App()
    app.run(sys.argv[1:])