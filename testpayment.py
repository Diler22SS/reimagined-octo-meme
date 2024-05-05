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
        # необходимые данные достаем из self.payment_params, self.paymethod_params, self.user_params
        # здесь для примера выводим параметры метода оплаты (self.paymethod_params) и платежа (self.payment_params) в лог
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")

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

        r = requests.post('https://securepay.tinkoff.ru/v2/Init', headers={"Content-Type": "application/json"}, data = json.dumps(data)) 
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
        payment_form =  "<html>\n";
        payment_form += "<head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>\n"
        payment_form += "<link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />"
        payment_form += "	<script language='JavaScript'>\n"
        payment_form += "		function DoSubmit() {\n"
        payment_form += "			window.location.assign('" + redirect_url + "');\n"
        payment_form += "		}\n"
        payment_form += "	</script>\n"
        payment_form += "</head>\n"
        payment_form += "<body onload='DoSubmit()'>\n"
        payment_form += "</body>\n"
        payment_form += "</html>\n";

        sys.stdout.write(payment_form)


TestPaymentCgi().Process()
