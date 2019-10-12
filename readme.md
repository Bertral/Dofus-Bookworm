# Dofus Bookworm

This scripts dumps every character build from [dofusbook](https://www.dofusbook.net) into an xlsx file. Here's a sample:
![sample](https://i.imgur.com/aPWHPGH.png)

It takes a while (about 3 sec per page to read, the server is the bottleneck), so pick the number of users to scrape wisely. You can change this value in ```main.py``` in the call to get_builds. Set get_stats to True if you want the calculated stats for every build, it will take about 10 times longer.

The process is as follows :
1. Reads the list of members, page by page, excluding members without characters, sorted by views. This takes about 24 hours. The provided ```users.pkl``` lets you skip this step by loading the last scraped user list.
2. Reads the list of builds for every user, page by page (of 20 builds), excluding the ones that are less than level 200. If get_stats is set to True, it also reads each build's page to get their stats (extremely slow due to the server's response times). After every user scanned, the progress is saved to ```progress.pkl```, so if you crash or take a break it'll resume where you left.
3. Every 100 user scanned or at the end, progress is saved to an xlsx file.

I commit a result file whenever I make progress on it.

Google Chrome needs to be installed on your machine for this script to work.

As usual, python package requirements can be installed with ```pip install -r requirements.txt```.
