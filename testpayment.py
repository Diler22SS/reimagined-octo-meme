#!/usr/bin/python3
import payment
import sys
import billmgr.logger as logging

import requests
import hashlib
import json
from jinja2 import Template

MODULE = 'payment'
logging.init_logging('testpayment')
logger = logging.get_logger('testpayment')

class TestPaymentCgi(payment.PaymentCgi):
    def Process(self):
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")
        
        payment_tm = Template('''<html>
                                    <head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>
                                    <link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />"
                                        <script language='JavaScript'>
                                            function DoSubmit() {
                                                window.location.assign("{{ redirect_url }}");
                                            }
                                        </script>
                                    </head>
                                    <body onload='DoSubmit()'>
                                    </body>
                                </html>
                                    ''')


        data = dict()
        data["TerminalKey"] = self.paymethod_params["terminalkey"]
        data["Amount"] = float(self.payment_params["paymethodamount"]) * 100
        data["OrderId"] = self.elid + "#" + self.payment_params["randomnumber"]
        data["PayType"] = "O"
        data["DATA"] = {"OperationInitiatorType":0}
        data["Success URL"] = self.success_page
        data["Fail URL"] = self.fail_page

        psw = self.paymethod_params["terminalpsw"]
        
        token_data = data.copy()

        token_data.update({"Password": psw})
        token_data = dict(sorted(token_data.items()))
        concatenated_values = ''.join(str(token_data.values()))
        hashed_result = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
        data["Token"] = hashed_result

        r = requests.post('https://securepay.tinkoff.ru/v2/Init', 
                          headers={"Content-Type": "application/json"}, 
                          data = json.dumps(data))
        
        logger.info(f"data = {data}")
        logger.info(f"requests = {r.json()}")
        
        # переводим платеж в статус оплачивается
        payment.set_in_pay(self.elid, '', 'external_' + self.elid)

        # url для перенаправления c cgi
        # здесь, в тестовом примере сразу перенаправляем на страницу BILLmanager
        # должны перенаправлять на страницу платежной системы
        redirect_url = r.json()["PaymentURL"]

        # формируем html и отправляем в stdout
        # таким образом переходим на redirect_url
        payment_form = payment_tm.render(redirect_url=redirect_url)

        sys.stdout.write(payment_form)


TestPaymentCgi().Process()