# %%
import imghdr
import os
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage

import matplotlib.pyplot as plt
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import click
from dotenv import dotenv_values

# %%

# Helper functions
def select_day(driver, xpath, target_date):
    """Select day in datepicker"""
    dates = driver.find_elements(By.XPATH, xpath)
    for date in dates:
        if date.text == target_date:
            date.click()
            break


def select_time(driver, xpath, target_time):
    """Select pickup and delivery time"""
    t = driver.find_element(By.XPATH, xpath)
    t.click()
    time.sleep(1)
    t.send_keys(target_time)
    t.send_keys(Keys.ENTER)


@click.command(name="autoeurope_scraper")
@click.option(
    "--country",
    type=str,
    required=True,
    help="Country of pickup. Check spelling at autoeurope website.",
)
@click.option("--city", type=str, required=True)
@click.option("--pickup", type=str, help="Pickup location", required=True)
@click.option(
    "--pickupdate",
    type=str,
    help="Date of pickup formatted as 06-JUNI-2022",
    required=True,
)
@click.option(
    "--pickuptime",
    type=str,
    help="Time of pickup formatted in whole hours (ie. 14)",
    required=True,
)
@click.option(
    "--dropoffdate",
    type=str,
    help="Date of pickup formatted as 6-JUNI-2022 (no 0 in front of day)",
    required=True,
)
@click.option(
    "--dropofftime",
    type=str,
    help="Time of dropoff formatted in whole hours (ie. 14)",
    required=True,
)
@click.option(
    "--mailfrom",
    type=str,
    help="Mail address to send from. If none uses env file",
    default="",
)
@click.option(
    "--mailpass",
    type=str,
    help="Password to mailfrom email. If none uses env file",
    default="",
)
@click.option(
    "--mailto",
    type=str,
    help="Mail address to send to. If none given mails to the mail given in mailfrom",
    default="",
)
def scrape_autoeurope(
    country,
    city,
    pickup,
    pickupdate,
    pickuptime,
    dropoffdate,
    dropofftime,
    mailfrom,
    mailpass,
    mailto,
):
    """Scrapes autoeruope"""
    DESTINATION_COUNTRY = country
    DESTINATION_CITY = city
    DESTINATION_PICKUP_LOC = pickup

    PICKUP_DATE, PICKUP_MONTH, PICKUP_YEAR = pickupdate.split("-")
    PICKUP_TIME = pickuptime
    DELIVERY_DATE, DELIVERY_MONTH, DELIVERY_YEAR = dropoffdate.split("-")
    DELIVERY_TIME = dropofftime

    if not mailfrom or not mailpass:
        cfg = dotenv_values()
    EMAIL_ADDRESS = mailfrom if mailfrom else cfg["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = mailpass if mailpass else cfg["EMAIL_PASS"]
    EMAIL_TO = mailfrom if not mailto else mailto

    click.echo(f"Sending mail from: {EMAIL_ADDRESS} using pass {EMAIL_PASSWORD}")
    click.echo(f"Sending mail to: {EMAIL_TO}")
    click.echo("Running tests")
    if PICKUP_DATE.startswith("0") or DELIVERY_DATE.startswith("0"):
        raise ValueError("Date cannot start with 0. Causes endless loop")

    if PICKUP_MONTH.isdigit() or DELIVERY_MONTH.isdigit():
        raise ValueError("Specify month as JUNI etc")

    CSV_OUT = "data.csv"
    PLT_OUT = "prices.png"

    #### START
    click.echo("Starting driver")
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://www.autoeurope.dk")
    driver.implicitly_wait(60)
    time.sleep(1)

    click.echo("Selecting country, city and pickup location")

    ### SET LOCATION
    Select(driver.find_element(By.NAME, "PU-country")).select_by_visible_text(
        DESTINATION_COUNTRY
    )

    Select(driver.find_element(By.NAME, "PU-city")).select_by_visible_text(
        DESTINATION_CITY
    )

    Select(driver.find_element(By.NAME, "PU-loc")).select_by_visible_text(
        DESTINATION_PICKUP_LOC
    )

    ## PICKUP DATE
    click.echo("Opening datepicker")

    ## OPEN DATEPICKER PICK_UP
    driver.find_element(
        By.XPATH, r"//div[@data-label='Afhentningsdato']//button"
    ).click()

    # CHECK IF FIRST DISPLAYED MONTH IS CORRECT

    first_dp_m = driver.find_element(
        By.XPATH,
        r'//div[@class="ui-datepicker-group ui-datepicker-group-first"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-month"]',
    ).text

    first_dp_y = driver.find_element(
        By.XPATH,
        r'//div[@class="ui-datepicker-group ui-datepicker-group-first"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-year"]',
    ).text

    if first_dp_y == PICKUP_YEAR and first_dp_m == PICKUP_MONTH:
        select_day(
            driver,
            '//div[@class="ui-datepicker-group ui-datepicker-group-first"]//table[@class="ui-datepicker-calendar"]//a',
            PICKUP_DATE,
        )

    else:
        last_dp_m = driver.find_element(
            By.XPATH,
            r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-month"]',
        ).text

        last_dp_y = driver.find_element(
            By.XPATH,
            r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-year"]',
        ).text

        correct_m_and_y = last_dp_m == PICKUP_MONTH and last_dp_y == PICKUP_YEAR
        click.echo("Selecting pickup month and year")

        while not correct_m_and_y:
            driver.find_element(
                By.XPATH, "//span[@class='ui-icon ui-icon-circle-triangle-e']"
            ).click()
            last_dp_m = driver.find_element(
                By.XPATH,
                r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-month"]',
            ).text

            last_dp_y = driver.find_element(
                By.XPATH,
                r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-year"]',
            ).text

            correct_m_and_y = last_dp_m == PICKUP_MONTH and last_dp_y == PICKUP_YEAR
        click.echo("Selecting pickup day")

        ## SELECT PICKUP DAY
        select_day(
            driver,
            '//div[@class="ui-datepicker-group ui-datepicker-group-last"]//table[@class="ui-datepicker-calendar"]//a',
            PICKUP_DATE,
        )

    ## SELECT PICKUP TIME
    click.echo("Selecting pickup time")

    select_time(driver, '//span[@id="pickup-time-button"]', PICKUP_TIME)

    ## DELIVERY DATE ######
    click.echo("Selecting dropoff month and year")

    ## OPEN DATEPICKER DELIVERY
    driver.find_element(
        By.XPATH, r"//div[@data-label='Afleveringsdato']//button"
    ).click()

    first_dp_m = driver.find_element(
        By.XPATH,
        r'//div[@class="ui-datepicker-group ui-datepicker-group-first"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-month"]',
    ).text

    first_dp_y = driver.find_element(
        By.XPATH,
        r'//div[@class="ui-datepicker-group ui-datepicker-group-first"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-year"]',
    ).text

    if first_dp_y == DELIVERY_YEAR and first_dp_m == DELIVERY_MONTH:
        select_day(
            driver,
            '//div[@class="ui-datepicker-group ui-datepicker-group-first"]//table[@class="ui-datepicker-calendar"]//a',
            DELIVERY_DATE,
        )

    else:
        last_dp_m = driver.find_element(
            By.XPATH,
            r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-month"]',
        ).text

        last_dp_y = driver.find_element(
            By.XPATH,
            r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-year"]',
        ).text

        correct_m_and_y = last_dp_m == DELIVERY_MONTH and last_dp_y == DELIVERY_YEAR

        while not correct_m_and_y:
            driver.find_element(
                By.XPATH, "//span[@class='ui-icon ui-icon-circle-triangle-e']"
            ).click()
            last_dp_m = driver.find_element(
                By.XPATH,
                r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-month"]',
            ).text

            last_dp_y = driver.find_element(
                By.XPATH,
                r'//div[@class="ui-datepicker-group ui-datepicker-group-last"]//div//div[@class="ui-datepicker-title"]//span[@class="ui-datepicker-year"]',
            ).text

            correct_m_and_y = last_dp_m == DELIVERY_MONTH and last_dp_y == DELIVERY_YEAR
        click.echo("Selecting dropoff day")

        select_day(
            driver,
            '//div[@class="ui-datepicker-group ui-datepicker-group-last"]//table[@class="ui-datepicker-calendar"]//a',
            DELIVERY_DATE,
        )

    ## SELECT DROPOFF TIME
    click.echo("Selecting dropoff time")

    select_time(driver, '//span[@id="dropoff-time-button"]', DELIVERY_TIME)

    ## CICK SEARCH
    click.echo("Clicking search")

    driver.find_element(By.NAME, "btn-submit").click()

    ## GATHER PRICES
    click.echo("gathering prices")

    cars = {
        "mini": '//li[@data-event-code=",C1"]',
        "economy": '//li[@data-event-code=",C2"]',
        "medium": '//li[@data-event-code=",C3"]',
        "large": '//li[@data-event-code=",C4"]',
        "stationcar_suv": '//li[@data-event-code=",C5"]',
        "minibus": '//li[@data-event-code=",C6"]',
    }

    prices = {"date": pd.to_datetime(datetime.now())}
    for car, xpath in cars.items():
        price = driver.find_element(By.XPATH, xpath).text
        prices[car] = int(price.replace("DKK ", ""))
    new_df = pd.DataFrame([prices]).set_index("date")

    driver.close()

    click.echo("Writing csv")

    if not os.path.exists(CSV_OUT):
        new_df.to_csv(CSV_OUT)
    else:
        old_df = pd.read_csv(CSV_OUT, parse_dates=["date"]).set_index("date")
        out_df = pd.concat([old_df, new_df], axis="rows")

        out_df.to_csv(CSV_OUT)

        # PLOT PRICES
        click.echo("Creating plot")

        fig, ax = plt.subplots(figsize=(10, 10))
        out_df.plot(ax=ax)
        fig.set_facecolor("white")
        fig.tight_layout()
        fig.savefig(PLT_OUT)

        # Get price differences

        diffs = pd.concat([new_df.T, old_df.min()], axis=1)
        diffs.columns = ["New price", "Old price"]
        diffs = diffs.assign(Difference=diffs["New price"] - diffs["Old price"])
        lower_prices = diffs[diffs.Difference.lt(0)]

        if lower_prices.shape[0] > 0:
            click.echo("Sending mail")

            msg = EmailMessage()
            msg["Subject"] = f"Prisen er faldet for {DESTINATION_CITY}"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = EMAIL_TO
            msg.set_content(
                f"""\
                <!DOCTYPE html>
                    <html>
                        <body>
                            {lower_prices.to_html()}
                        </body>
                    </html>
                """,
                subtype="html",
            )

            with open("prices.png", "rb") as img:
                img_data = img.read()
                img_type = imghdr.what(img.name)
                img_name = img.name

            msg.add_attachment(
                img_data, maintype="image", subtype=img_type, filename=img_name
            )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)


# %%
if __name__ == "__main__":
    scrape_autoeurope()
