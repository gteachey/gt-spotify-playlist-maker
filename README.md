# gt-spotify-playlist-maker
My Spotify Playlist Maker. Scrapes top 100 songs from Billboard 100 from selected year, month, date

I used a regex to increase the odds of a successful match, in my overly complex regex that I just had to do :-) .

artists = [
    re.sub("/\(.*?|\[.*?| featuring.*| &.*?| and.*?/g", "",
           title.parent.select(selector="span")[0].getText().strip("\n").lower())
    for title in songs
]
Gist of it is, it matches and removes 'Featuring', 'And', '&', '(', '[' and anything following it. I found Spotify doesn't like multiple artists at once on a search, so I keep just the main artist which helped increase my chances of matching songs.



I also spent many hours playing with ttk so I could have a GUI instead of typing out the year, month, date value.
