import argparse
import os
import time

import cv2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

URL = "SOME_URL_HERE"


def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    service = Service(executable_path="./chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def capture_page(url: str, image_filename: str, html_filename: str, target_xpath: str):
    driver = create_driver()
    driver.get(url)
    el = driver.find_element(By.XPATH, target_xpath)
    total_height = el.size["height"] + 6000
    driver.set_window_size(1920, total_height)
    el.screenshot(image_filename)
    out_html = el.get_attribute("innerHTML")
    with open(html_filename, "w") as f:
        f.write(out_html)
    driver.close()
    driver.quit()


def calculate_image_similarity(image1: str, image2: str):
    prev_img = cv2.imread(image1)
    cur_img = cv2.imread(image2)

    if cur_img.shape != prev_img.shape:
        # cropping both image to fit smaller image
        if prev_img.shape[0] > cur_img.shape[0]:
            crop_height = cur_img.shape[0]
        else:
            crop_height = prev_img.shape[0]

        if prev_img.shape[1] > cur_img.shape[1]:
            crop_width = cur_img.shape[1]
        else:
            crop_width = prev_img.shape[1]

        prev_img = prev_img[:crop_height, :crop_width, :]
        cur_img = cur_img[:crop_height, :crop_width, :]
        print(f"Cropping image to height: {crop_height}, width: {crop_width}")

    height = cur_img.shape[0]
    width = cur_img.shape[1]

    errorL2 = cv2.norm(prev_img, cur_img, cv2.NORM_L2)
    similarity = 1 - errorL2 / (height * width)
    return similarity


def calculate_html_similarity(html1: str, html2: str):
    from difflib import SequenceMatcher

    with open(html1, "r") as f:
        html1 = f.readlines()
    with open(html2, "r") as f:
        html2 = f.readlines()

    return SequenceMatcher(None, html1, html2).ratio()


def detect_change(
    url: str,
    check_interval: int,
    image_similarity_threshold: float,
    html_similarity_threshold: float,
    targer_xpath: str,
):
    # create dir to isolate different url
    url_dir = url.replace("https://", "").replace("/", "_").replace(".", "_")
    if not os.path.isdir(url_dir):
        os.mkdir(url_dir)

    capture_page(url, f"{url_dir}/prev.png", f"{url_dir}/prev.html", targer_xpath)
    time.sleep(check_interval)
    capture_page(url, f"{url_dir}/cur.png", f"{url_dir}/cur.html", targer_xpath)
    html_similarity = calculate_html_similarity(
        f"{url_dir}/prev.html", f"{url_dir}/cur.html"
    )
    image_similarity = calculate_image_similarity(
        f"{url_dir}/prev.png", f"{url_dir}/cur.png"
    )
    while (image_similarity >= image_similarity_threshold) and (
        html_similarity >= html_similarity_threshold
    ):
        # print prev similarity
        print(
            f"HTML threshold({html_similarity_threshold}) not exceeded:",
            html_similarity,
        )
        print(
            f"Image threshold({image_similarity_threshold}) not exceeded:",
            image_similarity,
        )

        # pause and check again
        time.sleep(check_interval)

        # replace cur to prev for next check
        os.remove(f"{url_dir}/prev.png")
        os.rename(f"{url_dir}/cur.png", f"{url_dir}/prev.png")
        os.remove(f"{url_dir}/prev.html")
        os.rename(f"{url_dir}/cur.html", f"{url_dir}/prev.html")

        # capture and check again
        capture_page(url, f"{url_dir}/cur.png", f"{url_dir}/cur.html", targer_xpath)

        # html similarity
        html_similarity = calculate_html_similarity(
            f"{url_dir}/prev.html", f"{url_dir}/cur.html"
        )

        # image similarity
        image_similarity = calculate_image_similarity(
            f"{url_dir}/prev.png", f"{url_dir}/cur.png"
        )

    if html_similarity < html_similarity_threshold:
        print(
            f"HTML threshold({html_similarity_threshold}) exceeded: {html_similarity}"
        )
    if image_similarity < image_similarity_threshold:
        print(
            f"Image threshold({image_similarity_threshold}) exceeded: {image_similarity}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to detect changes on a website"
    )
    parser.add_argument("-u", "--url", help="Website URL to monitor", required=True)
    parser.add_argument(
        "-i",
        "--interval",
        help="Interval to check URL, unit is seconds, default to 86400 seconds, which is 1 day",
        default=60 * 60 * 24,
    )
    parser.add_argument(
        "-ht",
        "--html-threshold",
        help="HTML similarity threshold for website, range from 0 to 1, the higher the number the more similar the website, default to 0.9",
        default=0.9,
    )
    parser.add_argument(
        "-it",
        "--image-threshold",
        help="Image similarity threshold for website, range from 0 to 1, the higher the number the more similar the website, default to 0.9",
        default=0.9,
    )
    parser.add_argument(
        "-t",
        "--target-xpath",
        help="Target xpath to check for within the provided website.",
        default="/html/body",
    )
    args = vars(parser.parse_args())

    URL = args["url"]
    if (not URL.startswith("https://")) and (URL.startswith("www.")):
        URL = "https://" + URL
    check_interval = int(args["interval"])
    html_similarity_threshold = float(args["html_threshold"])
    image_similarity_threshold = float(args["image_threshold"])
    targer_xpath = str(args["targer_xpath"])

    print(
        f'Monitoring website on "{URL}" every {check_interval}s, html_similarity_threshold: {html_similarity_threshold}, image_similarity_threshold: {image_similarity_threshold}'
    )
    detect_change(
        url=URL,
        check_interval=check_interval,
        html_similarity_threshold=html_similarity_threshold,
        image_similarity_threshold=image_similarity_threshold,
        targer_xpath=targer_xpath,
    )
