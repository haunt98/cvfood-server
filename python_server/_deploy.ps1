cls
heroku pg:reset --confirm XXX
heroku pg:push postgres://postgres:PASS@localhost:5432/DATABASE_NAME DATABASE_URL
git add -A
git commit -m "Deploy"
git push heroku master