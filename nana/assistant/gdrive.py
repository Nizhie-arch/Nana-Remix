import os

import pydrive
from pydrive.drive import GoogleDrive
from pyrogram import filters

from nana import setbot, AdminSettings, gauth, gdrive_credentials, HEROKU_API
from nana.tr_engine.strings import tld


@setbot.on_message(filters.user(AdminSettings) & filters.command(["gdrive"]))
async def gdrive_helper(_client, message):
    if len(message.text.split()) == 1:
        gdriveclient = os.path.isfile("client_secrets.json")
        if HEROKU_API:
            if not gdrive_credentials:
                await message.reply(tld("gdrive_credential_err_heroku"))
                return
            elif not gdriveclient:
                with open("client_secrets.json", "w") as gfile:
                    gfile.write(gdrive_credentials)
                    gfile.close()
                gdriveclient = os.path.isfile("client_secrets.json")
        if not gdriveclient:
            await message.reply(tld("gdrive_credential_err"))
            return

        gauth.LoadCredentialsFile("nana/session/drive")
        if gauth.credentials is None:
            try:
                authurl = gauth.GetAuthUrl()
            except:
                await message.reply(
                    "Wrong Credentials! Check var ENV gdrive_credentials on heroku or do .credentials (your "
                    "credentials) for change your Credentials")
                return
            teks = "First, you must log in to your Google drive first.\n\n[Visit this link and login to your Google " \
                   "account]({})\n\nAfter that you will get a verification code, type `/gdrive (verification code)` " \
                   "without '(' or ')'.".format(authurl)
            await message.reply(teks)
            return
        await message.reply("You're already logged in!\nTo logout type `/gdrive logout`")
    elif len(message.text.split()) == 2 and message.text.split()[1] == "logout":
        os.remove("nana/session/drive")
        await message.reply("You have logged out of your account!\nTo login again, just type /gdrive")
    elif len(message.text.split()) == 2:
        try:
            gauth.Auth(message.text.split()[1])
        except pydrive.auth.AuthenticationError:
            await message.reply("Your Authentication code is Wrong!")
            return
        gauth.SaveCredentialsFile("nana/session/drive")
        drive = GoogleDrive(gauth)
        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for drivefolders in file_list:
            if drivefolders['title'] == 'Nana Drive':
                await message.reply("Authentication successful!\nWelcome back!")
                return
        mkdir = drive.CreateFile({'title': 'Nana Drive', "mimeType": "application/vnd.google-apps.folder"})
        mkdir.Upload()
        await message.reply("Authentication successful!\nThe 'Nana Drive' folder has been created automatically!")
    else:
        await message.reply("Invaild args!\nCheck /gdrive for usage guide")
