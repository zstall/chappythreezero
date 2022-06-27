# chappythreezero

Very early notes, much more to come on setup...

Setting up postgresql for Mac OS. Start by installing postgresql:
`brew install postgresql`
Create a data dir if desired and update postgres to use this datadir:
`initdb /<path to>/<dataDir>/`
You may have to stop postgres to start it with the new datadir:
`pg_ctl -D /usr/local/var/postgres stop`
Start postgres with the new data dir:
`pg_ctl -D psqlData -l psqlData/chppyPG start`


## TO DO:
Registration Form:
- Fix if a user adds a org_id
- Check if password re-entry matches
- Create error message if password doesn't match

Success page:
- restyle
- make a link to go to login page

Security:
- Add logic to make sure that user is logged in

User Page (create a user page):
- this is where users can see personal info
- Join organizations (if they have an ID)
- If admin, can see users and org ids

CHores:
- differentiate between super user and admin user. IE, admin should only see their org, super user (reserved for support and chappy admin) can see ALL orgs