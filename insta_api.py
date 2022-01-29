import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, urllib.request
import json

def get_code(api_params):
    '''The function uses selenium to reach instagram API page
    https://api.instagram.com/oauth/ and the autorization page which the
    request is redirected to. The final redirect link (after autirization
    and confirmation by user) contains the autorisation code in form of GET
    parameter. This code is returned by function.
        Function uses saved instagram account credentials, which it reads
    from the csv file. The manual input will be implemented after a while.'''
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get('https://api.instagram.com/oauth/authorize?client_id='
    + api_params['app_id'] + '&redirect_uri=' + api_params['uri']
    +'&scope=user_profile,user_media&response_type=code')
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR
    , "input[name='username']"))).send_keys(api_params['username'])
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR
    , "input[name='password']"))).send_keys(api_params['password'])
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR
    , "button[type='submit']"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH
    , '//*[@id="react-root"]/section/main/div/div/div/div/button'))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable
    ((By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div[2]/div[3]'
    '/div/div[2]/button'))).click()
    time.sleep(1)
    code = re.findall('code=(.*)#_', driver.current_url)[0]
    driver.close()
    return code

def get_token(code, api_params):
    ''' the function changes the code for short living acess token, which
    is used in every instagramm API request. Code is send as POST request,
    token returns in json response'''
    params_dict = {'client_id': api_params['app_id']
    ,'client_secret': api_params['secret']
    ,'grant_type': 'authorization_code'
    ,'redirect_uri': api_params['uri']
    ,'code': code,}
    r = requests.post('https://api.instagram.com/oauth/access_token/'
    ,data = params_dict)
    return r.json()['access_token']

def save_params(file_patch, api_params):
    ''' the function saves the parameters (including short-living token) to .csv
    file for further use. The choice of file name should be implemented'''
    words={}
    with open(file_patch, "w") as params_file:
        for key, value in api_params.items():
            params_file.write(key + ','+ str(value) + '\n')
    print('params and token saved')

def read_params(file_patch):
    ''' the function reads the parameters (including short-living token) from
    .csv The choice of file name should be implemented'''
    with open(file_patch, "r") as params_file:
        api_params = {}
        for line in params_file:
            api_params[line.split(',')[0]] = line.split(',')[1][:-1]
    return api_params

def establish_connect(homepage_url, requests_params, api_params):
    '''The function checks, if the API request with given parameters does return
    200 Code. if not - the function tries to get new short-living token'''
    if requests.get(homepage_url ,params = requests_params).status_code != 200:
        print('getting new code')
        code = get_code(api_params)
        print(code)
        print('getting new token')
        api_params['token'] = get_token(code, api_params)
        input(api_params['token'])

def get_media(media_id, token, fields):
    '''the first functoion for working trough established API connection. It
    receives the parameters of media with given ID. Media should be one from
    users media'''
    url = 'https://graph.instagram.com/' + str(media_id)
    input(json.dumps(requests.get(url ,params = {'access_token': token
    , 'fields': fields}).json()
    , indent = 4))


api_params = read_params('api_params_file.csv')
requests_params = {'fields': 'id,username,media'
                        ,'access_token': api_params['token']}
establish_connect('https://graph.instagram.com/me', requests_params, api_params)
get_media(18153060142099950, api_params['token'], 'id,media_url')
save_params('api_params_file.csv', api_params)
print(api_params)
