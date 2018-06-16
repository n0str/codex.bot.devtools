#!/bin/bash

echo "	[bot] Killing Core	`screen -S bot_core	 -X quit;`";
echo "	[app] Killing GitHub	`screen -S bot_github 	 -X quit;`";
echo "	[app] Killing Weather	`screen -S bot_weather	 -X quit;`";
echo "	[app] Killing Rssparser	`screen -S bot_rssparser -X quit;`";
echo "	[app] Killing Metrika	`screen -S bot_metrika 	 -X quit;`";
echo "	[app] Killing Notify	`screen -S bot_notify 	 -X quit;`";

source /root/codex.bot/venv/bin/activate;

service rabbitmq-server reload;

cd /root/codex.bot/core;
screen -dmS bot_core    python3 main.py;
echo "	[bot] Core is running";

cd /root/codex.bot/applications/github/github;
screen -dmS bot_github  python3 main.py;
echo "	[app] Github is running.";

cd /root/codex.bot/applications/metrika/metrika;
screen -dmS bot_metrika python3 main.py;
echo "	[app] Metrika is running.";

cd /root/codex.bot/applications/notify/notify;
screen -dmS bot_notify  python3 main.py;
echo "	[app] Notify is running.";

cd /root/codex.bot/applications/rssparser/rssparser;
screen -dmS bot_rssparser  python3 main.py;
echo "	[app] Rssparser is running.";

cd /root/codex.bot/applications/weather/weather;
screen -dmS bot_weather  python3 main.py;
echo "	[app] Weather is running.";

deactivate;

echo "List of bot's screens: "
screen -ls | grep bot_*;

echo "Done."

sleep 3
curl -X POST https://notify.bot.ifmo.su/u/<...> -d "message=CodeX.Bot successfully restarted"
