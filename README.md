# fed_autoplayer

Script that automaticaly plays game hosted on https://thefed.app/ with use of Selenium by simulating clicks.

![Screenshot](fed_autoplay.gif)

Script plays the game using simple alghoritm to choose which item should be bought next. Taken into consideration are how much item costs, how long until player will be able to afford it with current income and how much money player has at time of checking.

I don't recommend leaving this running for too long as over time memory usage may be significant.

Usage: download Chromedriver, install Selenium, run app.py
```
pip install selenium
python app.py
```

