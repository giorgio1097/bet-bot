from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


def get_last_bet(rendimento=0, importo_puntata=500):
  url = "https://www.ninjabet.it/surebet?rendimento-da=" + str(
    rendimento) + "&importo-puntata=" + str(importo_puntata) + "&puntata=totale"

  chrome_options = Options()
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')

  driver = webdriver.Chrome(options=chrome_options)

  driver.get(url)

  table = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'datatable')))
  try:
    row = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, 'tooltip1')))
  except TimeoutException as e:
    raise Exception('Nessuna bet disponibile')

  tbody = table.find_elements(By.TAG_NAME, 'tbody')[0]
  rows = tbody.find_elements(By.TAG_NAME,
                             "tr")  # get all of the rows in the table

  list_rendimento = []

  for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    cell_rendimento = cells[3]
    try:
      span = cell_rendimento.find_elements(By.TAG_NAME, "span")[0]
    except Exception as e:
      continue
    list_rendimento.append(span.text)
    # print (span.text)

  driver.quit()

  print(list_rendimento[0])
  return list_rendimento[0]
