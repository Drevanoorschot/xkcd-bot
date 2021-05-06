# XKCD Discord bot
For the uninitiated: https://xkcd.com/
## What does it do?
It posts xkcd comics in the *#xkcd* channel of your server when a new comic is released

## How do I install it?
1. Clone the repository (duh)
2. install dependencies: `pip install -r requirements.txt`
2. Run setup.py: `python setup.py`
3. Copy `config_example.py` to `config.py` and enter your Discord application token
4. Run the thing: `python main.py`

Probably smart though to run the main.py in a service or daemon (or a screen if you're cheap).