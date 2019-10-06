import crawler

crwler = None
try:
    crwler = crawler.Crawler()
    builds = crwler.get_builds(0, 'all_users_no_stats.xlsx', False)
    print('DONE !')
finally:
    crwler.quit()