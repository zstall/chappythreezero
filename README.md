# chappythreezero

Very early notes, much more to come on setup...

Setting up postgresql for Mac OS. Start by installing postgresql:
`brew install postgresql`
Create a data dir if desired and update postgres to use this datadir:
`initdb /<path to>/<dataDir>/`
You may have to stop postgres to start it with the new datadir:
`pg_ctl -D /usr/local/var/postgres stop`
Start postgres with the new data dir:
`pg_ctl -D psqlData -l psqlData/chppyPG star`


