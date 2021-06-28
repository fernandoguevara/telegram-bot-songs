# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import re
import requests
from youtube_search import YoutubeSearch
import youtube_dl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
import eyed3

TOKEN = ''

updater = Updater(TOKEN, use_context=True)
bot = Bot(token=TOKEN)

def start(update, context):
    update.message.reply_text('Download Youtube Music')

def error(update, context):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, context.error)

def song(update, context):
    search =  update.message.text.replace('/song', '')
    filename = download(search) + '.mp3'
    bot.send_audio(chat_id=update.message.chat_id, audio=open(filename, 'rb'))
    os.remove(filename)

def album(update, context):
    search = update.message.text.replace('/album', '')
    album, artist, songs = get_album_info(search)

    filename = ''
    for song in songs:
        filename = download(song + ' ' + artist) + '.mp3'
        set_song_info(filename, artist, album)
        bot.send_audio(chat_id=update.message.chat_id, audio=open(filename, 'rb'))
        os.remove(filename)

def set_song_info(song, artist, album):
    file = eyed3.load(song)
    file.tag.title = song.replace('.mp3', '')
    file.tag.artist = artist
    file.tag.album = album
    file.tag.save()

def download(search):
    results = YoutubeSearch(search, max_results=10).to_dict()
    video_id = results[0]["id"]
    filename = results[0]["title"]
    filename = re.sub('[^A-zÀ-ú0-9 ]+', '', filename)
    ydl_opts = {
        'outtmpl': filename,
        'extractaudio': True,  # only keep the audio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"http://www.youtube.com/watch?v={video_id}"])

    return filename

def get_album_info(search):
    result = requests.get(f'https://api.deezer.com/search/album?q={search}').json()
    album = result['data'][0]['title']
    artist = result['data'][0]['artist']['name']
    tracklist = result['data'][0]['tracklist']
    tracks = requests.get(tracklist).json()['data']

    songs = []
    for track in tracks:
        songs.append(track['title'])
    return album, artist, songs

def main():

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("song", song, run_async=True))
    dp.add_handler(CommandHandler("album", album, run_async=True))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()