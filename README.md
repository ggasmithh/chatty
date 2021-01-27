# chatty
A Telegram chatbot utilizing Markov chains for humourous results.
 
 ## usage
 Before running, chatty must be configured by setting the following enviroment variables.
 
 ### ```CHATTY_BOT_TOKEN```
 Your telegram bot token goes here. Get it from BotFather on telegram.
 
 ### ```CHATTY_CHAT_ID```
 Set this to your chat ID so chatty knows which group to talk to! I do it this way rather than letting chatty join just any group so that random people cannot run up my VM quoats.
 
 Once all that is done, I usually just run chatty like this, because I'm too lazy to install ```screen``` or ```tmux```
 
```
python3 chatty.py
ctrl+z
bg
disown -h
```


---

under no circumstances should you use this in your telegram group.
