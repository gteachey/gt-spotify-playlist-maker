from bs4 import BeautifulSoup
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
from tkinter import *
from tkinter import ttk, messagebox
import os
import re
import requests
import spotipy
import tkinter

# Add environment variables or replace this with own ID and secret
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def make_spotify_playlist(year, month, day):
    # Billboard goes back to 1958-08-04
    # Make sure user doesn't put anything older than this.
    date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Get HTML from billboard.com
    response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Webscrape billboard top 100 for the date provided
    songs = soup.select(selector="li > .c-title")
    titles = [song.getText().strip("\n") for song in songs]

    # Behold! The more complex than it needs to be list comprehension!
    # What it does:
    # Grab the artist using the parent of titles gathered above, save in all lower case
    # Run a regular expression to 'clean' the artists by removing these matches and everything after them:
    # 'Featuring', 'And', '&', '(', '['
    # When a song/artist hits the Except block below, if I can regex it out, so it will match I update the regex.
    artists = [
        re.sub("/\(.*?|\[.*?| featuring.*| &.*?| and.*?/g", "",
               title.parent.select(selector="span")[0].getText().strip("\n").lower())
        for title in songs
    ]

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                                   client_secret=SPOTIFY_CLIENT_SECRET,
                                                   redirect_uri="http://example.com"))

    spotify_tracks = []
    for i in range(0, len(artists)):
        try:
            spotify_tracks.append(sp.search(q=f"{titles[i]} {artists[i]}")['tracks']['items'][0]['id'])
        except IndexError:
            print(f"Couldn't find Artist: '{artists[i]}'\nSong: '{titles[i]}'.\nCan you can regex this!")

    # Create a playlist, save the response
    playlist = sp.user_playlist_create(user="31hz4zruuhbiycpeljek5robbuaq", name=f"{date} Billboard 100",
                                       public=False,
                                       collaborative=False,
                                       description=f'Playlist from the day {date}')
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id=playlist_id, items=spotify_tracks)


def is_valid_date(year, month, day):
    day_count_for_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        day_count_for_month[2] = 29
    return 1 <= month <= 12 and 1 <= day <= day_count_for_month[month]


def submit_button_pressed():
    year = year_picker.get()
    month = month_picker.get()
    day = day_picker.get()
    if year and month and day: # TODO: Come back to this later. Maybe there's a better way to check this
        if year == "1958" and \
                int(month) < 8 and \
                int(day) < 4:
            messagebox.showinfo(title="No Data",
                                message="Billboard top 100 started August 4, 1958. Choose a date after then")
        elif int(year) == datetime.today().year and \
                int(month) >= datetime.today().month and \
                int(day) > datetime.today().day:
            messagebox.showinfo(title="From the Future?",
                                message="That day hasn't happened yet. Try another date!")
        elif is_valid_date(year=int(year), month=int(month), day=int(day)):
            make_spotify_playlist(year, month, day)
            messagebox.showinfo(title="Playlist Created!", message="Go to Spotify to start listening!")
        else:
            messagebox.showinfo(title="No Data",
                                message="The date selected doesn't actually exist.\nCheck the entries chosen.")
    else:
        messagebox.showinfo(title="Missing Date", message="Please confirm you've made all the choices")


def quit_button_pressed():
    quit()


window = Tk()
window.geometry("575x300")
window.resizable(False, False)
window.title("Spotify Playlist Maker")
window.configure(background="aliceblue")

style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground="orange", background="white", padding=(15, 1, 15, 1), justify="center")
style.configure("BW.TLabel", foreground="black", background="aliceblue", padding=(15, 50, 15, 15))
style.configure("TButton", foreground="black", background="aliceblue", padding=(15, 10, 15, 10), width=15,
                font=("Arial", 12, "bold"))
style.configure("TFrame", background="aliceblue")

# Set up frames to contain the label and combobox widgets for each data point.
# Helps with getting the layout I want
month_frame = ttk.Frame(window)
month_frame.columnconfigure(0, weight=1)
month_frame.columnconfigure(0, weight=3)
month_frame['padding'] = (15, 10, 15, 10)
month_frame['style'] = "TFrame"
ttk.Label(month_frame, text='Choose Month', font=("Arial", 14, "bold"), style="BW.TLabel").grid(column=0, row=0)
pick_month = tkinter.StringVar()
month_picker = ttk.Combobox(month_frame, textvariable=pick_month, style="TCombobox", width=10)
month_picker['values'] = [month for month in range(1, 13)]
month_picker['state'] = 'readonly'
month_picker.grid(column=0, row=1)
month_frame.grid(column=0, row=0)

day_frame = ttk.Frame(window)
day_frame.columnconfigure(0, weight=1)
day_frame.columnconfigure(0, weight=3)
day_frame['padding'] = (15, 10, 15, 10)
day_frame['style'] = "TFrame"
ttk.Label(day_frame, text='Choose Day', font=("Arial", 14, "bold"), style="BW.TLabel").grid(column=0, row=0)
pick_day = tkinter.StringVar()
day_picker = ttk.Combobox(day_frame, textvariable=pick_day, style="TCombobox", width=10)
day_picker['values'] = [day for day in range(1, 31)]
day_picker['state'] = 'readonly'
day_picker.grid(column=0, row=1)
day_frame.grid(column=1, row=0)

year_frame = ttk.Frame(window)
year_frame.columnconfigure(0, weight=1)
year_frame.columnconfigure(0, weight=3)
year_frame['padding'] = (15, 10, 15, 10)
year_frame['style'] = "TFrame"
ttk.Label(year_frame, text='Choose Year', font=("Arial", 14, "bold"), style="BW.TLabel").grid(column=0, row=0)
pick_year = tkinter.StringVar()
year_picker = ttk.Combobox(year_frame, textvariable=pick_year, style="TCombobox", width=10)
year_picker['values'] = [year for year in range(2022, 1957, -1)]
year_picker['state'] = 'readonly'
year_picker.grid(column=0, row=1)
year_frame.grid(column=2, row=0)

# Create some space with this separator widget
separator = ttk.Separator(window, orient='horizontal')
separator.grid(column=0, row=1, columnspan=3, pady=30)

# One more fram set up to contain the button widgets
button_frame = ttk.Frame(window)
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(0, weight=3)
button_frame['padding'] = (15, 10, 15, 10)
button_frame['style'] = "TFrame"
submit_button = ttk.Button(button_frame, text="Create Playlist", command=submit_button_pressed, style="TButton")
submit_button.grid(column=0, row=0)
ttk.Label(button_frame, text="", style="BW.TLabel").grid(column=1, row=0)
quit_button = ttk.Button(button_frame, text="Quit", command=quit_button_pressed, style="TButton")
quit_button.grid(column=2, row=0)
button_frame.grid(column=0, row=2, columnspan=3)

window.mainloop()
