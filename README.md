# spotify-manager
the one stop shop for an upgraded spotify experience

## modules
- __rolling songs__: maintain a playlist of your favorite N songs and this'll keep stats (song -> playcount and duration on favorites list), and a running log playlist (every song that has ever made your favorites list)
- __liked songs sliding window__: maintains a playlist of your last N days of liked songs, or your last N liked songs (for when your liked songs playlist is too long to shuffle)
- __monthly recap__: at the end of every month, automatically creates a playlist of your top N songs for that month (by playcount)

## usage
1. make a lastfm account and link it to your spotify (this allows you to track more detailed statistics like playcount. it's also currently required by this manager repo as a whole)
2. run ```git clone git@github.com:michaeljecmen/spotify-manager.git```
3. run ```pip3 install -r requirements.txt```
4.  ```cp example.json config.json``` and fill out all of the fields except the ```SPOTIFY_REDIRECT_URI``` and the ```SPOTIFY_TOKEN```
        
    3a. to find your spotify client id and client secret, head over to [the spotify dev dashboard](https://developer.spotify.com/dashboard/), log in, and create an application. 
        
    3b. to find your lastfm api key and shared secret (only necessary if using the rolling songs module), head
    over to [the lastfm dev dashboard](https://www.last.fm/api/accounts), create a dev account (or make your normal account a dev account), create an application, and copy over your credentials.

    3c. if you choose to add email updates (the app will email you each time it notices a change to your rolling playlist) and use gmail as
    your sender email address, you'll need to follow [this tutorial](https://wpmailsmtp.com/docs/how-to-set-up-the-other-smtp-mailer-in-wp-mail-smtp/#app-passwords) to generate an app password for this program. when you've generated the app password, use that password (it should be a series of 16 characters) as the ```SENDER_PASSWORD``` value in ```config.json``` instead of your actual email password you use to log in. this is necessary due to increased gmail security as of mid 2022.
    
    to be clear, modify the fields in ```config.json```, not ```example.json```.
5. for the app you just created on your spotify dev dashboard, add the url ```http://localhost:8888/callback``` to the list of callbacks using the "edit settings" button. this url should match the url in your ```config.json```, so if you edited that for whatever reason be sure to update your callback list on the dashboard to match.
6. run ```cd spotify-manager/```
7. run the authenticator script with ```python3 -m scripts.auth``` and give the app access to your spotify account when it opens a browser window and yells at you. the program should auto-refresh the token once you generate it for the first time, but if you ever need to reauthenticate the program for some reason re-run this command.

## future work
- fill this out (usage with cron via https://stackoverflow.com/questions/8899737/crontab-run-in-directory)
- account for enabledness of modules with config enabled keys
- update sub-readmes
- add custom tagging system
- add support for not having lastfm
- add better error handling and email reporting for that
- be able to set the debug / email flag from a spotify playlist description 
- add every X day email dump with all changes made (each module logs its changes with the email module, which gets run on every X cadence and wipes its data after that)
- for rolling-songs, generate an html page with the graphs for the year from the python module. could use a very basic templating system or something more complex
- github actions integration, add testing and ci
- remove redirect uri from config
- make config a class and abstract out the keys from users
- use the github issues tracker instead of this file
- type annotate everything
- make custom spotify api calls auto-reauth
- for last month liked -- track how long the buffer of last 30 days is over time (how much new music you listened to as a 30 day buffer of minutes). really cool stat to see at the end of the year
- possibly remove lastfm altogether -- playcounts may be accessible from spotify api now
- make the album cover of the top song the playlist cover for the monthly_recap generated playlist 
