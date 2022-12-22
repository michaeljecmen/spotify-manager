# rolling-songs: the sliding window playlist statkeeper

say you have some sliding window playlist, which always contains N songs: 
whenever you add one song, you remove another. say you also want stats kept for this list. this app does that for you. 
at the end of the year, you can take these stats and generate a cool poster or something.

here's what I'm doing with it:
- I have a rolling playlist of my favorite 25 songs at a given moment
- I would like to know how that list has progressed over the course of the year (as an exact timeline of substitutions)
- I would like to know which songs were my favorites
- I would like to know my favorite songs by season or month
- I would like to know these things by play count as well as length on playlist

so I'm linking my spotify and last.fm to this app and having it check on things every morning
and record the relevant data to those ends (at least that's the goal). afterwards, I'll make a 
cool "better spotify wrapped" graphic or poster or something with the data. if I finish this and 
make a template I'll link it here so others can use it too.

## usage
1. clone this repo with ```git clone git@github.com:michaeljecmen/rolling-songs.git```
2. run ```pip3 install spotipy pylast```
3.  ```cp example.json config.json``` and modify all of the fields except the spotify url
        
    3a. to find your spotify client id and client secret, head over to [the spotify dev dashboard](https://developer.spotify.com/dashboard/), log in, and create an application. 
        
    3b. to find your lastfm api key and shared secret, head
    over to [the lastfm dev dashboard](https://www.last.fm/api/accounts), create a dev account (or make your normal account a dev account), create an application, and copy over your credentials.

    3c. if you choose to add email updates (the app will email you each time it notices a change to your rolling playlist) and use gmail as
    your sender email address, you'll need to follow [this tutorial](https://wpmailsmtp.com/docs/how-to-set-up-the-other-smtp-mailer-in-wp-mail-smtp/#app-passwords) to generate an app password for this program. when you've generated the app password, use that password (it should be a series of 16 characters) as the ```SENDER_PASSWORD``` value in ```config.json``` instead of your actual email password you use to log in. this is necessary due to increased gmail security as of mid 2022.
    
    to be clear, modify the fields in ```config.json```, not ```example.json```.
4. for the app you just created on your spotify dev dashboard, add the url ```http://localhost:8888/callback``` to the list of callbacks using the "edit settings" button. this url should match the url in your ```config.json```, so if you edited that for whatever reason be sure to update your callback list on the dashboard to match.
5. run ```cd rolling-songs/```, then ```chmod +x rolling.py``` to enter the directory and mark the program as executable (second step not necessary, but makes cron-jobbing the app easier)
6. run the authenticator script with ```python3 auth.py``` and give the app access to your spotify account when it opens a browser window and yells at you. the program should auto-refresh the token once you generate it for the first time, but if you ever need to reauthenticate the program for some reason re-run ```python3 auth.py```.
7. run the program once a day (or whenever you make changes to your playlist) with ```python3 rolling.py``` or ```./rolling.py```, or, even better, set up a cron job on a box somewhere.
8. at the end of the year (or however long you want your cycle of reports to last), run ```python3 finalize.py```. after this, your logfile will be complete, containing all of the information needed to reconstruct the full picture of your playlist's history this cycle.

## data storage
the data itself is stored in two files, both in the ```{DATA_DIR}``` folder:
1. the file named ```{STORAGE_FILENAME}```, defaulted to ```current-tracklist.json```. this file stores the current tracklist from your playlist of choice. most key-value pairs are self explanatory, but the ```playcount``` field in each json object denotes the total playcount for this track *prior to the track being added to the playlist*. when the track is removed, this value is then subtracted from the current playcount to get the "number of plays during its time on the playlist" value.
2. the file named ```{LOG_FILENAME}```, defaulted to ```rolling-log.json```. this file stores the initial tracklist (from the first run of the program), then a list of substitution events. here (stored in each json object in the ```out``` list of each sub-event) the ```playcount``` value refers to the "true" number of plays the track had during its tenure on your playlist. furthermore, this file is simply appended to each time the program detects a tracklist change.

both of these files will be necessary at the end of each year to generate the kinds of reports I'd like to see. everything that's been removed will have the relevant data in the log file, and the rest of the tracks have their info stored in the current tracklist file.

and, of course, you can change these default values in your ```config.json``` file.

I made the decision to make both of these items json files, which allows you to read and edit the values as you see fit (for instance, sometimes you'll know better than the program when a song was added or removed from the playlist).