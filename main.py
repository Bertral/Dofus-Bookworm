import crawler

crwler = None
try:
    crwler = crawler.Crawler()
    builds = crwler.get_builds(user_limit=150200, filename='all_users_no_stats.xlsx', get_stats=False)
    print('DONE !')
finally:
    crwler.quit()
