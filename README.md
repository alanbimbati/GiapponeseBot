# GiapponeseBot
Leaning Japanese from a Telegram Bot

First we have to clone the repository:

  git clone https://github.com/alanbimbati/GiapponeseBot/

add a python virtual environment

  python3 -m venv python

let's make python executable like a script file (so python main.py become ./main.py), just add 
#!/home/path/python/bin/python3 on the first line of main.py. Be sure of the absolute path of your main.py adding the virtual environment (python/bin/python3)
then demonize the process on your server with systemD

  sudo systemctl edit --force .-full giappo.service

and add this into the file

  [Unit]
  Description=GiappoBot

  [Service]
  ExecPreStart=/bin/sleep 10
  ExecStart=/home/path/main.py
  Restart=always

  [Install]
  WantedBy=multi-user.target

than enable the service

  sudo systemctl enable giappo.service

and start it

  sudo systemctl start giappo.service
