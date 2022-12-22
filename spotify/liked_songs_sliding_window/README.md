# liked-songs-sliding-window: maintain a shorter playlist of your recently liked songs 

is your liked songs playlist on spotify too long? do you listen to enough new music that you occasionally lose great tracks to the flow of time? do you wish your "on repeat" playlist wasn't just a strict most-played in last x days?

my solution to these problems is pretty rudimentary: keep a small playlist of only the most recent liked songs. I've currently got mine set up to maintain a playlist of songs I've liked in the previous 30 days, but you can also change the rule to maintain the playlist (last n songs liked or all songs liked in the last n days).

## usage
1. clone this repo with ```git clone git@github.com:michaeljecmen/liked-songs-sliding-window.git```
2. run ```pip3 install spotipy```
3.  ```cp example.json config.json``` and modify all of the fields except the spotify url
        
    3a. to find your spotify client id and client secret, head over to [the spotify dev dashboard](https://developer.spotify.com/dashboard/), log in, and create an application. 

    3b. of the two ```UPDATE_RULE```s now in your in ```config.json```, pick one and delete the other line from the file. if you want to have the playlist represent your previously liked n songs, keep and set the ```MAINTAIN_NUM_SONGS``` pair. if you want the playlist to contain the songs you've liked over the previous n days, use the ```MAINTAIN_NUM_DAYS``` pair. if you ever change this rule, you'll need to re-do step 7 of this guide
    
    to be clear, modify the fields in ```config.json```, not ```example.json```.
4. for the app you just created on your spotify dev dashboard, add the url ```http://localhost:8888/callback``` to the list of callbacks using the "edit settings" button. this url should match the url in your ```config.json```, so if you edited that for whatever reason be sure to update your callback list on the dashboard to match.
5. run ```cd liked-songs-sliding-window/```, then ```chmod +x update-sliding.py``` to enter the directory and mark the program as executable (second step not necessary, but makes cron-jobbing the app easier)
6. run the authenticator script with ```python3 auth.py``` and give the app access to your spotify account when it opens a browser window and yells at you. the program should auto-refresh the token once you generate it for the first time, but if you ever need to reauthenticate the program for some reason re-run ```python3 auth.py```.
7. on spotify, create a playlist with the name you provided in your ```config.json```
8. make sure the playlist in step 7 is empty, then run ```python3 populate-playlist.py``` to fill the playlist for the first time. don't rearrange the songs on this playlist, the add order is important
9. run the program regularly (I have mine running hourly) with ```python3 update-sliding.py``` or ```./update-sliding.py```, or, even better, set up a cron job on a box somewhere