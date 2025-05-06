from search_inputs import get_user_input
from selenium_config import setup_selenium
from get_doctors import search_doctolib, extract_data

if __name__ == "__main__":
    args = get_user_input()
    driver = setup_selenium()

    try:
        driver = search_doctolib(
            driver,
            args["query"],
            args["sector"],
            args["address_keyword"]
        )
        df = extract_data(driver, args["max_results"])
        df = df.iloc[1:]
        df.to_csv('doctors.csv', index=False, encoding="utf-8-sig")
    finally:
        driver.quit()