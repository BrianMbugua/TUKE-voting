from selenium import webdriver

url = "http://localhost:5000/transactions"
browser = webdriver.Chrome()
browser.get(url)

browser.find_element_by_xpath('/html/body/div/div[2]/ul').click()