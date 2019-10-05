import crawler

crwler = None
try:
    crwler = crawler.Crawler()
    builds = crwler.get_builds(1000, 'top_1000_users.xlsx')
    print('DONE !')
finally:
    crwler.quit()