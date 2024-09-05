import json
import os
import requests


def get_user_agent_string(first_name : str, last_name : str, email : str) -> str:
    return f'{first_name} {last_name} ({email})'

def get_cik_ticker_map(user_agent_string : str) -> dict:

    headers = {
        'User-Agent': user_agent_string
    }

    # Download the CIK mapping file
    cik_map_url = "https://www.sec.gov/include/ticker.txt"
    response = requests.get(cik_map_url, headers=headers, timeout=10)

    if response.status_code == 200:
        # Store the CIK mapping in the Edgar class as a dictionary
        cik_map = {}
        for line in response.text.splitlines():
            ticker, cik = line.split('\t')
            # Pad the CIK with leading zeros to ensure it's 10 digits long
            padded_cik = cik.zfill(10)
            cik_map[ticker.lower()] = padded_cik
        print("CIK mapping downloaded successfully.")
        return cik_map
    else:
        print(f"Failed to download CIK mapping. Status code: {response.status_code}")
        return None
        
def get_cik_from_ticker(ticker : str, cik_map : dict) -> str:
    ticker = ticker.lower()
    return cik_map[ticker]

def get_raw_data(user_agent_string : str, cik : str) -> dict:
    headers = {
        'User-Agent': user_agent_string
    }
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def get_taxonomies(company_data : dict):
    return list(company_data['facts'].keys())

def get_tags(company_data : dict):

    taxonomies = get_taxonomies(company_data)
    all_tags = {}
    for taxonomy in taxonomies:
        all_tags[taxonomy] = list(company_data['facts'][taxonomy].keys())

    return all_tags

def get_data_by_tag(company_data : dict, tag : str, taxonomy : str):

    concept = {}
    concept['tag'] = tag
    concept['taxonomy'] = taxonomy
    concept['label'] = company_data['facts'][taxonomy][tag]['label']
    concept['description'] = company_data['facts'][taxonomy][tag]['description']
    concept['filings'] = []
    for unit in company_data['facts'][taxonomy][tag]['units'].keys():
        for filing in company_data['facts'][taxonomy][tag]['units'][unit]:
            concept['filings'].append({
                'unit': unit,
                'value': filing['val'],
                'fiscal_year': filing['fy'],
                'fiscal_period': filing['fp'],
                'form_type': filing['form'],
                'date_filed': filing['filed']
            })
    return concept

def get_all_data(company_data : dict, all_tags : dict) -> dict:
    facts = {}
    for taxonomy, tags_list in all_tags.items():
        for tag in tags_list:
            fact = get_data_by_tag(company_data, tag, taxonomy)
            facts[tag] = fact
    return facts


def get_all_data_for_ticker(ticker : str):
    user_agent_string = get_user_agent_string(
        "Ingimar",
        "Tomasson",
        "ingitom99@gmail.com"
    )
    cik_map = get_cik_ticker_map(user_agent_string)
    cik = get_cik_from_ticker(ticker, cik_map)
    company_data = get_raw_data(user_agent_string, cik)
    all_tags = get_tags(company_data)
    all_data = get_all_data(company_data, all_tags)
    
    # Ensure the data directory and ticker subdirectory exist
    os.makedirs(f"./data/{ticker}", exist_ok=True)

    # Create the file path
    file_path = f"./data/{ticker}/sec.json"

    # Save the data to a JSON file
    with open(file_path, "w") as f:
        json.dump(all_data, f, indent=4)

    # Verify that the file was created
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Failed to create file: {file_path}")
    return None
