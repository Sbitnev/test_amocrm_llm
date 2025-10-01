import datetime as dt

from tg_bot_s import bot
from metrics import metrics

yesterday = dt.datetime.now() - dt.timedelta(days=1)
start_dt = yesterday.replace(hour=0, minute=0, second=0)
end_dt = yesterday.replace(hour=23, minute=59, second=59)
digest = metrics.get_digest(start_dt, end_dt)
# print(metrics.get_nl_tg_user_ids())
for user_id in metrics.get_nl_tg_user_ids():
    print(user_id)
    bot.send_digest_message(user_id, digest)
