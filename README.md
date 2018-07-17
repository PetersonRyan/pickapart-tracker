# pickapart-tracker
Pickapart-tracker notifies users when a new car has been added on pickapart.ca

Some dependencies are required for this program to work. First install pip to manage the other dependencies by typing `sudo easy_install pip` in terminal.

Must have Selenium installed for Python
https://pypi.python.org/pypi/selenium
or type the command

```
pip install -U selenium
```

For Pushbullet notifications you must have pushbullet.py
https://pypi.python.org/pypi/pushbullet.py
or type the command

```
pip install pushbullet.py
```


To use the application just uncomment the car you want from carList.py, then run main.py

For more convenience, try running this script on a schedule to be notified automatically!
