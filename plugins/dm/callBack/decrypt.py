'''

█ █▄ █    █▄█ ▄▀▄ █▄ ▄█ ██▀    █▀▄ █▀▄ █▀ 
█ █ ▀█    █ █ █▀█ █ ▀ █ █▄▄    █▀  █▄▀ █▀ 
                        Dev : IlhamGUD

'''

import time
import fitz
import shutil
from pdf import PROCESS
from pyromod import listen
from pyrogram import filters
from Configs.dm import Config
from plugins.progress import progress
from plugins.checkPdf import checkPdf
from pyrogram.types import ForceReply
from pyrogram import Client as InHamePDF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup




#--------------->
#--------> LOCAL VARIABLES
#------------------->

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> PDF DECRYPTION
#------------------->

decrypts = ["decrypt", "Kdecrypt"]
decrypt = filters.create(lambda _, __, query: query.data.startswith(tuple(decrypts)))


@InHamePDF.on_callback_query(decrypt)
async def _decrypt(bot, callbackQuery):
    try:
        # CHECKS IF BOT DOING ANY WORK
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "⏳ - Sedang dalam proses",
            )
            return
        # CALLBACK DATA
        data = callbackQuery.data
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        # PYROMOD ADD-ON (ASK'S PASSWORD)
        password=await bot.ask(
            chat_id=callbackQuery.message.chat.id,
            reply_to_message_id=callbackQuery.message.message_id,
            text="__PDF Decryption »\nSekarang, silakan masukkan kata sandi :__\n\n/keluar __untuk membatalkan__",
            filters=filters.text,
            reply_markup=ForceReply(True)
        )
        # CANCEL DECRYPTION PROCESS IF MESSAGE == /exit
        if password.text == "/keluar":
            await password.reply(
                "`☑️ - Proses dibatalkan`"
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        # DOWNLOAD MESSAGE
        downloadMessage=await callbackQuery.message.reply_text(
            "`📥 - Mendownload PDF`", quote=True
        )
        input_file = f"{callbackQuery.message.message_id}/pdf.pdf"
        output_pdf = f"{callbackQuery.message.message_id}/Decrypted.pdf"
        file_id = callbackQuery.message.reply_to_message.document.file_id
        fileSize = callbackQuery.message.reply_to_message.document.file_size
        # STARTED DOWNLOADING
        c_time=time.time()
        downloadLoc=await bot.download_media(
            message=file_id,
            file_name=input_file,
            progress=progress,
            progress_args=(
                fileSize,
                downloadMessage,
                c_time
            )
        )
        # CHECKS PDF DOWNLOAD OR NOT
        if downloadLoc is None:
            PROCESS.remove(callbackQuery.message.chat.id)
            return
        await downloadMessage.edit(
            "`🔐 - Started Decrypting`"
        )
        if data[0] != "K":
            checked = await checkPdf(f"{callbackQuery.message.message_id}/pdf.pdf", callbackQuery)
            if not(checked == "encrypted"):
                await downloadMessage.edit(
                    "❗ - File tidak Encrypted"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                shutil.rmtree(f"{callbackQuery.message.message_id}")
                return
        try:
            with fitz.open(input_file) as encrptPdf:
                encrptPdf.authenticate(f"{password.text}")
                encrptPdf.save(
                    output_pdf
                )
        except Exception:
            await downloadMessage.edit(
                f"❗ - Tidak dapat Decrypt file ini dengan `{password.text}`"
            )
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
            return
        # CHECH IF PROCESS CANCELLED
        if callbackQuery.message.chat.id not in PROCESS:
            shutil.rmtree(f'{callbackQuery.message.message_id}')
            return
        await downloadMessage.edit(
            "`📤 - Mengirim file`"
        )
        await bot.send_chat_action(
            callbackQuery.message.chat.id, "upload_document"
        )
        await callbackQuery.message.reply_document(
            document=open(output_pdf, "rb"),
            thumb=PDF_THUMBNAIL,
            quote=True
        )
        await downloadMessage.delete()
        shutil.rmtree(f"{callbackQuery.message.message_id}")
        PROCESS.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            print("decrypt: ", e)
            PROCESS.remove(callbackQuery.message.chat.id)
            shutil.rmtree(f"{callbackQuery.message.message_id}")
        except Exception:
            pass


# Copyright InHame Dev
