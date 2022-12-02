from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os

# url of the website
test_url = "https://democracy-lab-prod-mirror.herokuapp.com/projects"
# input directory
test_case_dir = "test_cases"
# output directory
test_res_dir = "test_results"
# top n results that will be written to the output
top_n = 30

# Retrieve the projects currently displayed on the web page
def find_projects(driver):
    res = []

    project_cards = driver.find_elements(By.CLASS_NAME, "ProjectCard-root")
    for card in project_cards:
        title = card.find_element(By.CLASS_NAME, "ProjectCard-title").find_element(By.TAG_NAME, 'h2').text
        url = card.find_element(By.XPATH, ".//a[@href]").get_attribute("href")
        res.append([title, url])

    return res


# Test all keywords in an input file and write the results to the output folder
def test_input(input_file):
    results_map = {}
    driver = webdriver.Chrome()

    with open(os.path.join(test_case_dir, input_file), newline='') as f:
        reader = csv.reader(f)
        keywords = sum(list(reader), [])

    for keyword in keywords:
        if not keyword:
            continue
        driver.get(test_url + "?keyword=" + keyword)
        try:
            myElem = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'tech-for-good projects found')]")))
            projects_amount = int(myElem.text.split()[0])
        except TimeoutException as ex:
            projects_amount = 0

        results = find_projects(driver)
        while len(results) < min(projects_amount, top_n):
            buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'More Projects...')]")
            if len(buttons) > 0:
                buttons[0].click()
            results = find_projects(driver)

        results_map[keyword] = results

    with open(os.path.join(test_res_dir, input_file), mode='w', newline='') as results:
        writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["keyword", "project", "url"])
        for keyword, projects in results_map.items():
            for project in projects:
                writer.writerow([keyword, project[0], project[1]])


def main():
    for dir_, _, files in os.walk(test_case_dir):
        for file_name in files:
            print("testing: ", file_name)
            test_input(file_name)


if __name__ == "__main__":
    main()
