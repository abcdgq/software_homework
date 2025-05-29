from django_cron import CronJobBase, Schedule

from business.api.rss_flush_newest_paper import RSS_FEEDS, save_papers_to_db


class UpdateNewsJob(CronJobBase):
    RUN_EVERY_MINS = 360  # 每6小时运行一次

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'arxiv.update_papers'

    def do(self):
        for category in RSS_FEEDS.keys():
            save_papers_to_db(category)