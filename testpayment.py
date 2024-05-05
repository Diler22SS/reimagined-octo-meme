#!/usr/bin/python3
import payment
import sys
import billmgr.logger as logging

import requests
import hashlib
import json


MODULE = 'payment'
logging.init_logging('testpayment')
logger = logging.get_logger('testpayment')

class TestPaymentCgi(payment.PaymentCgi):
    def Process(self):
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")
        
        def gen_token(data, secretkey):
        #генерирует токен с использованием алгоритма хеширования SHA-256
            secret_data = dict()
            for key, value in data.items():
                if type(value) in [int, float, str, bool]:
                    secret_data[key] = value
            secret_data.update({"Password": secretkey})
            secret_data = dict(sorted(secret_data.items()))
            concatenated_values = ''.join(list(secret_data.values()))
            token = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
            return token
        
        
        # Этот блок кода инициализирует словарь data_Init с различными парами ключ-значение, необходимыми для
        # получения ссылки в платежную систему.
        data_Init = dict()
        data_Init["TerminalKey"] = self.paymethod_params["terminalkey"]
        data_Init["Amount"] = str(float(self.payment_params["paymethodamount"]) * 100)
        data_Init["OrderId"] = self.elid + "#" + self.payment_params["randomnumber"]
        data_Init["PayType"] = "O"
        data_Init["DATA"] = {"OperationInitiatorType":0}
        data_Init["Success URL"] = self.success_page
        data_Init["Fail URL"] = self.fail_page
        data_Init["Token"] = gen_token(data_Init, self.paymethod_params["terminalpsw"])
        logger.info(f"data_Init = {data_Init}")
        
        # Делает POST-запрос на URL-адрес https://securepay.tinkoff.ru/v2/Init
        r_Init = requests.post('https://securepay.tinkoff.ru/v2/Init', 
                          headers={"Content-Type": "application/json"}, 
                          data = json.dumps(data_Init))
        logger.info(f"r_Init = {r_Init.json()}")
        
        # url для перенаправления c cgi на страницу платежной системы
        redirect_url = r_Init.json()["PaymentURL"]

        # формируем html через шаблонизатор и отправляем в stdout для перехода на redirect_url
        payment_form = self.payment_tm.render(redirect_url=redirect_url)
        sys.stdout.write(payment_form)
        
        # переводим платеж в статус оплачивается
        payment.set_in_pay(self.elid, '', 'external_' + self.elid)
        
        # Получение состояния платежа от платежной системы
        data_GetState = dict()
        data_GetState['TerminalKey'] = self.paymethod_params["terminalkey"]
        data_GetState['PaymentId'] = r_Init.json()["PaymentId"]
        data_GetState['Token'] = gen_token(data_GetState, self.paymethod_params["terminalpsw"])
        logger.info(f"data_GetState = {data_GetState}")
        
        r_GetState = requests.post('https://securepay.tinkoff.ru/v2/GetState', 
                    headers={"Content-Type": "application/json"}, 
                    data = json.dumps(data_GetState))
        logger.info(f"r_GetState = {r_GetState.json()}")


TestPaymentCgi().Process()