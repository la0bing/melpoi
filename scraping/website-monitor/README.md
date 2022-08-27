# website-monitor
A python script that uses Selenium and opencv to detect if a website has new updates or changes. There are 2 metrics used to compare if change happened.

1. ```html_similarity```: This compares previous and current HTML source and find calculate the similarity between them.
2. ```image_similarity```: This compares the rendered image of the previous and current website and calculate the similarity using opencv.

## Get Started
1. Run the following line, you can install the dependencies in your virtual environment if you want:
    ```
    pip install -r requirements.txt
    ```
2. Download your matching webdriver [here](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/), the script is set to use chromedriver, you may change to your desired webdriver [here](https://github.com/la0bing/website-monitor/blob/main/website_monitor.py?plain=1#L17).


## Usage
Run the script ```website_monitor.py``` in the root folder with the command below and your desired configurations.
```
python website_monitor.py \
--url <TARGET_URL> \
--interval <CHECK_INTERVAL> \
--html-threshold <HTML_THRESHOLD> \
--image-threshold <IMAGE_THRESHOLD> \
--target-xpath <TARGET_XPATH>
```

The scripts accepts the following parameters and some is optional with default values:
- **(required)** url: Website URL to monitor
- *(optional)* interval: Interval to check URL, unit is seconds, default to 86400 seconds, which is 1 day
- *(optional)* html_threshold: HTML similarity threshold for website, range from 0 to 1, the higher the number the more similar the website, default to 0.9
- *(optional)* image_threshold: Image similarity threshold for website, range from 0 to 1, the higher the number the more similar the website, default to 0.9
- *(optional)* target_xpath: Target xpath to check for within the provided website., default to "/html/body"

Use command ```python website_monitor.py --help``` for help.
