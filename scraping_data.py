from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=options
)


def get_batting_average_records(driver):
    driver.get("https://www.baseball-almanac.com/recbooks/rb_bavg1.shtml")
    header_row = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div[3]/table/tbody/tr[10]"
    )
    data_rows = header_row.find_elements(By.XPATH, ".//following-sibling::tr")
    records = []

    for row in data_rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) == 6:
            league_name = columns[1].text.strip()
            player_name = columns[2].text.strip()
            team_name = columns[3].text.strip()
            bat_avg = columns[4].text.strip()
            year_record = columns[5].text.strip()
        elif len(columns) == 5:
            league_name = columns[0].text.strip()
            player_name = columns[1].text.strip()
            team_name = columns[2].text.strip()
            bat_avg = columns[3].text.strip()
            year_record = columns[4].text.strip()
        else:
            continue

        records.append(
            {
                "League": league_name,
                "Name": player_name,
                "Team": team_name,
                "Batting Average": bat_avg,
                "Year": year_record,
            }
        )

    df_batting = pd.DataFrame(records)
    df_unique = df_batting.drop_duplicates(subset=["Name", "Batting Average"])
    top23 = df_unique.iloc[0:23].reset_index(drop=True)
    return top23


def get_career_home_runs(driver):
    driver.get("https://www.baseball-almanac.com/recbooks/rb_hr1.shtml")
    header_row = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div[3]/table/tbody/tr[2]"
    )
    data_rows = header_row.find_elements(By.XPATH, ".//following-sibling::tr")
    records = []

    for row in data_rows:
        columns = row.find_elements(By.TAG_NAME, "td")

        if len(columns) == 6:
            player_cell = columns[2]
            links = player_cell.find_elements(By.TAG_NAME, "a")
            player_name = links[0].text.strip() if links else player_cell.text.strip()

            hr_cell = columns[5]
            links = hr_cell.find_elements(By.TAG_NAME, "a")
            career_hr = links[0].text.strip() if links else hr_cell.text.strip()

        elif len(columns) == 5:
            player_cell = columns[1]
            links = player_cell.find_elements(By.TAG_NAME, "a")
            player_name = links[0].text.strip() if links else player_cell.text.strip()

            hr_cell = columns[4]
            links = hr_cell.find_elements(By.TAG_NAME, "a")
            career_hr = links[0].text.strip() if links else hr_cell.text.strip()

        elif len(columns) == 4:
            player_cell = columns[0]
            links = player_cell.find_elements(By.TAG_NAME, "a")
            player_name = links[0].text.strip() if links else player_cell.text.strip()

            hr_cell = columns[3]
            links = hr_cell.find_elements(By.TAG_NAME, "a")
            career_hr = links[0].text.strip() if links else hr_cell.text.strip()

        else:
            continue

        records.append({"Name": player_name, "Career Home Runs": career_hr})

    df_hr = pd.DataFrame(records)
    df_filtered = df_hr[~df_hr["Name"].isin(["AL", "NL", "LG", "ML"])]
    df_unique = df_filtered.drop_duplicates(subset=["Name"])
    final_hr = df_unique.iloc[:-5].reset_index(drop=True)
    return final_hr


def get_career_strikeouts(driver):
    driver.get("https://www.baseball-almanac.com/recbooks/rb_strik.shtml")
    header_row = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div[3]/table/tbody/tr[2]"
    )
    data_rows = header_row.find_elements(By.XPATH, ".//following-sibling::tr")
    records = []

    for row in data_rows:
        if "banner" in row.get_attribute("class"):
            break

        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) == 6:
            league_name = columns[1].text.strip()
            player_cell = columns[2]
            links = player_cell.find_elements(By.TAG_NAME, "a")
            player_name = links[0].text.strip() if links else player_cell.text.strip()
            strikeouts = columns[5].text.strip()

        elif len(columns) == 5:
            league_name = columns[0].text.strip()
            player_cell = columns[1]
            links = player_cell.find_elements(By.TAG_NAME, "a")
            player_name = links[0].text.strip() if links else player_cell.text.strip()
            strikeouts = columns[4].text.strip()

        else:
            continue

        records.append(
            {
                "League": league_name,
                "Name": player_name,
                "Career Strikeouts": strikeouts,
            }
        )

    df_strikeouts = pd.DataFrame(records)
    df_unique = df_strikeouts.drop_duplicates(subset=["League", "Name"])
    top8 = df_unique.iloc[0:8].reset_index(drop=True)
    return top8


try:
    # Batting averages
    bat_avg_df = get_batting_average_records(driver)
    sleep(3)
    bat_avg_df["Batting Average"] = bat_avg_df["Batting Average"].astype(float)
    bat_avg_df["Year"] = pd.to_numeric(bat_avg_df["Year"], errors="coerce")
    bat_avg_df.to_csv("batting_average_records.csv")
    print("Batting average records have been exported to batting_average_records.csv")

    # Home runs
    hr_df = get_career_home_runs(driver)
    sleep(3)
    hr_df["Career Home Runs"] = hr_df["Career Home Runs"].astype(int)
    hr_df.to_csv("career_home_run_records.csv")
    print("Career home run data written to career_home_run_records.csv")

    # Strikeouts
    so_df = get_career_strikeouts(driver)
    sleep(3)
    so_df["Career Strikeouts"] = pd.to_numeric(
        so_df["Career Strikeouts"].str.replace(",", "", regex=False), errors="coerce"
    )
    so_df.to_csv("career_strikeout_records.csv")
    print("Pitcher strikeout statistics saved to career_strikeout_records.csv")

except Exception as scrape_error:
    print(
        f"Scraping encountered an error: {type(scrape_error).__name__}: {scrape_error}"
    )

finally:
    driver.quit()
