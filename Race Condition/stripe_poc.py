from urllib import request
from webbrowser import get
from wsgiref import headers
import requests
import threading

#initial requirements
Promo_code = "CANDY20"
Payment_link = "https://buy.stripe.com/test_eVabIM5AY3sVgGQaER"
key = "pk_test_51LZDVzKhT16fMhGCe6eva9oUSkoN0yf6hYbW9aSJ7QnL8KHrPxym5V5SFb97fYk7A66ynRlAbJpHUCtn4rQ4w3hy00qIl2OfnF"
amt = "50000" #amount after discount is placed here

#no. of product to buy
n=5

#card Details
card = "4242424242424242"
cvc = "111"
exp_m = "11"
exp_y = "23"

#user details
name = "video"
email = "video@test.com"
country = "NP"

#variable declarations
i = 0
j = -1

#arrays declarations
pm_id = []
ses_id = []
threads = []

# Remove all characters after the character '?' and before 3rd '/' from string to modify link
def get_format_link(strValue): 
    ch = '/'
    ch1 = '?'
    strValue = strValue.split(ch1, 1)[0]
    for x in range(3):
        listOfWords = strValue.split(ch, 1)
        if len(listOfWords) > 0: 
            strValue = listOfWords[1]
    return strValue

#formatting payment link
Payment_link =get_format_link(Payment_link)

# Remove all characters after the character '#' and before 5th '/' from string to obtain plink from url
def get_formatted(strValue): 
    ch = '/'
    ch1 = '#'
    strValue = strValue.split(ch1, 1)[0]
    for x in range(5):
        listOfWords = strValue.split(ch, 1)
        if len(listOfWords) > 0: 
            strValue = listOfWords[1]
    return strValue


#looping for n no. of times to get n parameters
for x in range(n):
    #Send get request to buy.stripe.com with payment link to obtain plink in Location header of response.
    r= requests.get("https://buy.stripe.com/"+Payment_link, allow_redirects=True)
    #get just plink from Location header
    r_plink=get_formatted(r.url) 

    #plink parameter is used with key to obtain session_id by sending Post request to ``` /v1/payment_pages/for_plink ```
    payload1 = {"key": key, "payment_link": r_plink}
    r= requests.post("https://api.stripe.com/v1/payment_pages/for_plink", data=payload1)
    #get session_id from json of response
    r_all=r.json()
    r_sesid=r_all["session_id"]

    #POST request is sent to ``` /v1/payment_pages/<session_id>``` with token to apply coupon in session
    payload2 = {"key": key, "promotion_code": Promo_code}
    r= requests.post("https://api.stripe.com/v1/payment_pages/"+r_sesid, data=payload2)

    #One time payment_method is created using card credentials and user details by sending post request to ```/v1/payment_methods```
    payload3 = {"type": "card", "card[number]": card, "card[cvc]": cvc, "card[exp_month]": exp_m, "card[exp_year]": exp_y, "billing_details[name]": name, "billing_details[email]": email,"billing_details[address][country]": country, "key": key}
    r= requests.post("https://api.stripe.com/v1/payment_methods", data=payload3)
    #get payment_method from json of response
    r1_all=r.json()
    r_pmid=r1_all["id"]

    #store session_id and payment_method in array for each iteration for further use
    ses_id.append(r_sesid)
    pm_id.append(r_pmid)

#Function to send POST request to ```/v1/payment_pages/<session_id>/confirm ``` with key, payment_method, expected_amount and so on.
def send():
    
    payload4 = {"payment_method": pm_id[j], "expected_amount": amt, "expected_payment_method_type": "card", "key": key}
    r=requests.post("https://api.stripe.com/v1/payment_pages/"+ ses_id[j]+"/confirm", data=payload4)
    #print status_code to check if the request is successful or not.
    print(r.status_code)

#looping to make n final requests
for _ in range (n):
    j = j + 1

    # n threads are created to send the final request concurrenty
    t = threading.Thread(target=send)
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()
