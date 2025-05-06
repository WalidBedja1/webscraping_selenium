from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time


def search_doctolib(driver, query, sector, address_keyword):
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Accéder à Doctolib
        driver.get("https://www.doctolib.fr/")
        time.sleep(2)

        # 2. Accepter les cookies
        try:
            cookie_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            cookie_btn.click()
            time.sleep(1)
        except:
            print("Popup cookies non trouvée")

        # 3. Effectuer la recherche
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchbar-query-input"))
        )
        search_input.send_keys(query)
        time.sleep(2)

        location_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchbar-input.searchbar-place-input"))
        )
        location_input.clear()
        location_input.send_keys(address_keyword)
        time.sleep(1)
        location_input.send_keys(Keys.ENTER)
        time.sleep(1)

        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.searchbar-submit-button"))
        )
        search_button.click()
        time.sleep(3)

        # 4. Filtrer par secteur si spécifié
        if sector:
            try:
                sector_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(., 'Secteur {sector}')]"))
                )
                sector_btn.click()
                time.sleep(3)
            except:
                print(f"Filtre secteur {sector} non trouvé")

        return driver

    except Exception as e:
        print(f"Erreur lors de la recherche: {str(e)}")
        driver.save_screenshot("search_error.png")
        raise


def extract_data(driver, max_results):
    wait = WebDriverWait(driver, 20)
    data = []

    try:
        time.sleep(5)  # Attente cruciale pour le chargement

        cards = driver.find_elements(By.CSS_SELECTOR, "div.dl-search-result-card, div.dl-card")
        if not cards:
            raise Exception("Aucune carte médecin trouvée")

        print(f"Nombre de médecins trouvés: {len(cards)}")

        for i, card in enumerate(cards[:max_results+1]):
            try:
                doctor = {
                    'nom': extract_with_fallback(card, [
                        ('css', 'h2'),
                        ('css', 'a[href*="/dermatologue/"]')
                    ]),

                    'specialite': extract_with_fallback(card, [
                        ('xpath', './/*[contains(text(), "Dermatologue")]')
                    ]),

                    'adresse': extract_address(card),

                    'disponibilite': extract_with_fallback(card, [
                        ('xpath', './/*[contains(text(), "disponibilité")]/following::span[1]')
                    ])
                }
                data.append(doctor)

            except Exception as e:
                print(f"Erreur sur le médecin {i + 1}: {str(e)}")
                continue

        return pd.DataFrame(data)

    except Exception as e:
        print(f"Erreur lors de l'extraction: {str(e)}")
        driver.save_screenshot("extract_error.png")
        raise


# Fonctions utilitaires
def extract_with_fallback(element, selectors, default="Non trouvé"):
    for selector_type, selector in selectors:
        try:
            if selector_type == 'css':
                return element.find_element(By.CSS_SELECTOR, selector).text
            elif selector_type == 'xpath':
                return element.find_element(By.XPATH, selector).text
        except NoSuchElementException:
            continue
    return default


def extract_address(card):
    try:
        # Méthode plus robuste pour l'adresse
        address_div = card.find_element(By.XPATH, './/div[contains(@class, "gap-8 flex")][.//*[@aria-label="Adresse"]]')
        parts = address_div.find_elements(By.XPATH, './/p[contains(@class, "XZWvFVZmM9FHf461kjNO")]')
        return ", ".join(p.text for p in parts[:2])
    except:
        return "Adresse non trouvée"