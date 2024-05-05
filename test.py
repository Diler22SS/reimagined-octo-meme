import hashlib
a = {
    "TerminalKey": "TinkoffBankTest",
"PaymentId": 13660,
"IP": "192.168.0.52"
}
b = "Token 7241ac8307f349afb7bb9dda760717721bbb45950b97c67289f23d8c69cc7b96"
[{"TerminalKey": "MerchantTerminalKey"},{"Amount": "19200"},{"OrderId": "21090"},{"Description": "Подарочная карта на 1000 рублей"}]
'0024a00af7c350a3a67ca168ce06502aa72772456662e38696d48b56ee9c97d9'
def gen_token(data, secretkey):
    secret_data = dict()
    for key, value in data.items():
        if type(value) in [int, float, str, bool]:
            secret_data[key] = value
    
    secret_data.update({"Password": secretkey})
    print(secret_data)
    secret_data = dict(sorted(secret_data.items()))
    print(secret_data)
    concatenated_values = ''.join(list(secret_data.values()))
    print('secret_data.values()', ''.join(list(secret_data.values())))
    print('concatenated_values', concatenated_values)
    token = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
    print(token)
    return token
        
data_Init = dict()
# data_Init["TerminalKey"] = "TinkoffBankTest"
# data_Init["PaymentId"] = '13660'
# data_Init["DATA"] = {"OperationInitiatorType":0}
# data_Init["IP"] = "192.168.0.52"
# data_Init["Token"] = gen_token(data_Init, "TinkoffBankTest")

data_Init["TerminalKey"] = "MerchantTerminalKey"
data_Init["Amount"] = "19200"
data_Init["OrderId"] = "21090"
data_Init["Description"] = "Подарочная карта на 1000 рублей"
data_Init["Token"] = gen_token(data_Init, "usaf8fw8fsw21g")

print(data_Init)