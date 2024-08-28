import json
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# 获取 Mod 的名称和支持的 Minecraft 版本列表
def get_mod_info_from_url(url):
    # 设置 Selenium 的 Chrome 浏览器选项
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument("--disable-gpu")

    # 初始化 WebDriver
    service = Service(executable_path="chromedriver.exe")  # 修改为你的 chromedriver 路径
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # 等待 Mod 名称元素加载
        mod_name_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='name-container']/h1"))
        )
        mod_name = mod_name_element.text.strip()
        print(mod_name)

        # 进入文件页面提取版本信息
        files_url = f"{url}/files/all?page=1&pageSize=1000"
        driver.get(files_url)

        # 等待页面加载
        time.sleep(3)

        # 获取所有版本信息的span元素
        version_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 "//*[@id='__next']/div/main/div[2]/div[2]/div/section/div[3]/div/div/a/div[5]/div/span[1]")))

        # 存储版本信息
        versions = []
        for version_element in version_elements:
            version_text = version_element.text.strip()
            try:
                if all(part.isdigit() for part in version_text.split('.')):
                    versions.append(version_text)
            except ValueError:
                continue

        # 去重并按降序排序版本信息
        unique_sorted_versions = sorted(set(versions), key=lambda v: [int(x) for x in v.split('.')], reverse=True)

        if not unique_sorted_versions:
            print("No supported versions found on the page.")
        else:
            print("Extracted versions:", unique_sorted_versions)

        return mod_name, unique_sorted_versions

    except Exception as e:
        print(f"Failed to retrieve mod info from URL: {e}")
        return None, None

    finally:
        driver.quit()


# 用户确认解析结果并可能手动修改
def confirm_and_edit_mod_info(mod_name, versions):
    print(f"\nAuto-detected mod name: {mod_name}")
    confirmed_name = input(f"Please confirm the mod name [{mod_name}]: ") or mod_name

    print(f"Auto-detected supported versions: {', '.join(versions)}")
    confirmed_versions = input(f"Please confirm the supported versions (comma separated) [{', '.join(versions)}]: ")
    if confirmed_versions:
        versions = [v.strip() for v in confirmed_versions.split(',')]

    return confirmed_name, versions


# 编辑器界面
# 编辑器界面
def config_editor():
    config = {
        "mods": [],
        "target_versions": []
    }

    while True:
        print("\n--- Configuration Editor ---")
        print("1. Add a mod manually")
        print("2. Add a mod by URL and auto-parse")
        print("3. Set target versions")
        print("4. Save and exit")
        choice = input("Choose an option: ")

        if choice == "1":
            # 手动添加 Mod
            mod_name = input("Enter the mod name: ")
            mod_url = input("Enter the mod URL: ")
            importance = input("Enter the mod importance (low, medium, high): ")
            versions = input("Enter the supported versions (comma separated): ")
            versions = [v.strip() for v in versions.split(',')]
            note = input("Enter any notes or remarks for the mod: ")

            config["mods"].append({
                "name": mod_name,
                "url": mod_url,
                "importance": importance,
                "versions": versions,
                "note": note
            })

        elif choice == "2":
            # 通过 URL 自动解析
            mod_url = input("Enter the mod URL: ")
            mod_name, versions = get_mod_info_from_url(mod_url)

            if mod_name and versions:
                mod_name, versions = confirm_and_edit_mod_info(mod_name, versions)
                importance = input("Enter the mod importance (low, medium, high): ")
                note = input("Enter any notes or remarks for the mod: ")

                config["mods"].append({
                    "name": mod_name,
                    "url": mod_url,
                    "importance": importance,
                    "versions": versions,
                    "note": note
                })
            else:
                print("Failed to auto-parse the mod information. Please try again.")

        elif choice == "3":
            # 设置目标版本
            target_versions = input("Enter the target versions (comma separated): ")
            # 去重并排序
            config["target_versions"] = sorted(set([v.strip() for v in target_versions.split(',')]), reverse=True)

        elif choice == "4":
            print(config)
            # 默认文件名为 config.json
            config_file = "config.json"
            # 如果配置文件存在，读取并加载现有配置
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    existing_config = json.load(file)
            else:
                # 如果配置文件不存在，初始化空配置
                existing_config = {"mods": [], "target_versions": []}
            # 获取现有的 mod 名称集合以避免重复
            existing_mod_names = {mod['name'].lower() for mod in existing_config['mods']}
            # 筛选新的 mod，排除与现有配置重复的 mod
            new_mods = [mod for mod in config["mods"] if mod["name"].lower() not in existing_mod_names]
            # 添加新的 mod 并合并到现有配置
            existing_config["mods"].extend(new_mods)

            # 按字母顺序排序所有 mod
            existing_config["mods"] = sorted(existing_config["mods"], key=lambda mod: mod["name"].lower())

            # 合并并排序目标版本
            all_versions = set(existing_config.get("target_versions", [])) | set(config["target_versions"])
            existing_config["target_versions"] = sorted(all_versions)

            # 将最终的配置保存到文件
            with open(config_file, 'w') as file:
                json.dump(existing_config, file, indent=4)
            print(f"Configuration updated and saved to {config_file}")
            break


if __name__ == "__main__":
    config_editor()
