#!/usr/bin/python3
import payment
import sys
import billmgr.logger as logging

from jinja2 import Template
import requests
import json

MODULE = 'payment'
logging.init_logging('testpayment')
logger = logging.get_logger('testpayment')

class TestPaymentCgi(payment.PaymentCgi):
    def Process(self):
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")
        
        # Создает шаблон HTML с использованием синтаксиса Jinja2. Шаблон включает в себя
        # простую структуру HTML с функцией JavaScript, которая перенаправляет пользователя на указанный URL-адрес 
        # при загрузке страницы.
        payment_tm = Template('''
                        <html>
                            <head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>
                            <link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />
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
        
        headers = {"Content-Type": "application/json"}
        # Этот блок кода инициализирует словарь data_Init с различными парами ключ-значение, необходимыми для
        # получения ссылки в платежную систему.
        data_Init = dict()
        data_Init["TerminalKey"] = self.paymethod_params["terminalkey"]
        data_Init["Amount"] = str(float(self.payment_params["paymethodamount"]) * 100)
        data_Init["OrderId"] = self.elid + "#" + self.payment_params["randomnumber"]
        data_Init["PayType"] = "O"                                                          # Одностадийная оплата
        data_Init["DATA"] = {"OperationInitiatorType":0}                                    # Стандартный платеж
        data_Init["SuccessURL"] = self.success_page
        data_Init["FailURL"] = self.fail_page
        data_Init["Token"] = payment.gen_token(data_Init, self.paymethod_params["terminalpsw"])
        logger.info(f"data_Init = {data_Init}")
        
        # Делает POST-запрос на URL-адрес https://securepay.tinkoff.ru/v2/Init
        r_Init = requests.post('https://securepay.tinkoff.ru/v2/Init', headers=headers, data = json.dumps(data_Init))
        logger.info(f"r_Init = {r_Init.json()}")
        
        # url для перенаправления c cgi на страницу платежной системы
        redirect_url = r_Init.json()["PaymentURL"]

        # формируем html через шаблонизатор и отправляем в stdout для перехода на redirect_url
        payment_form = payment_tm.render(redirect_url=redirect_url)
        sys.stdout.write(payment_form)
        
        # переводим платеж в статус оплачивается, в externalid передаем "PaymentId"
        payment.set_in_pay(self.elid, '', r_Init.json()["PaymentId"])


TestPaymentCgi().Process()