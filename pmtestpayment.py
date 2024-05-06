#!/usr/bin/python3

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET

import requests
import json

MODULE = 'payment'
logging.init_logging('pmtestpayment')
logger = logging.get_logger('pmtestpayment')

class TestPaymentModule(payment.PaymentModule):
    def __init__(self):
        super().__init__()

        self.features[payment.FEATURE_CHECKPAY] = True # проверка статуса платежа по крону
        self.features[payment.FEATURE_REDIRECT] = True # нужен ли переход в платёжку для оплаты
        self.features[payment.FEATURE_NOT_PROFILE] = True # оплата без плательщика (позволит зачислить платеж без создания плательщика)
        self.features[payment.FEATURE_PMVALIDATE] = True # проверка введённых данных на форме создания платежной системы

        self.params[payment.PAYMENT_PARAM_PAYMENT_SCRIPT] = "/mancgi/testpayment"

    # вызывается для проверки введенных в настройках метода оплаты значений
    # реализация --command pmvalidate
    # принимается xml с веденными на форме значениями
    # если есть некорректные значения, то бросаем исключение billmgr.exception.XmlException
    # если все значение валидны, то ничего не возвращаем, исключений не бросаем
    
    def PM_Validate(self, xml : ET.ElementTree):
        logger.info("run pmvalidate")
        logger.info(f"xml input: {ET.tostring(xml.getroot(), encoding='unicode')}")

        terminalkey_node = xml.find('./terminalkey')
        terminalpsw_node = xml.find('./terminalpsw')
        minamount_node = xml.find('./paymethod/minamount')
        terminalkey = terminalkey_node.text if terminalkey_node is not None else ''
        terminalpsw = terminalpsw_node.text if terminalpsw_node is not None else ''
        minamount = terminalpsw_node.text if terminalpsw_node is not None else '0'
        
        # Сумма платежа должна быть не меньше 10 руб.
        if float(minamount_node.text) < 10:
            raise billmgr.exception.XmlException('too_small_min_amount')

    # проверить оплаченные платежи
    # реализация --command checkpay
    # здесь делаем запрос в БД, получаем список платежей в статусе "оплачивается"
    # идем в платежку и проверяем прошли ли платежи
    # если платеж оплачен, выставляем соответствующий статус c помощью функции set_paid
    def CheckPay(self):
        logger.info("run checkpay")

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmtestpayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id, pm.xmlparams, p.externalid FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmtestpayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')
        
        # Для каждого платежа извлекает из данных платежа необходимую информацию, для обновления состояния платежей
        for p in payments:
            paymethod_xml = ET.fromstring(p['xmlparams'])
            data_GetState = dict()
            data_GetState['TerminalKey'] = paymethod_xml.find("terminalkey").text
            data_GetState['PaymentId'] = p["externalid"]
            data_GetState['Token'] = payment.gen_token(data_GetState, paymethod_xml.find("terminalpsw").text)
            logger.info(f"data_GetState = {data_GetState}")
            
            # Получение статуса платежа от платежной системы
            r_GetState = requests.post('https://securepay.tinkoff.ru/v2/GetState', 
                        headers={"Content-Type": "application/json"}, 
                        data = json.dumps(data_GetState))
            logger.info(f"r_GetState = {r_GetState.json()}")
            
            # Обновления состояния платежей, исходя из статуса
            json_GetState = r_GetState.json()
            success__statuses = ['CONFIRMED']
            fail_statuses = ['СANCELED', 'DEADLINE_EXPIRED', 'REJECTED']
            if json_GetState['Success']:
                if json_GetState['Status'] in success__statuses:
                    payment.set_paid(p['id'], '', f"external_{p['id']}")
                    logger.info(f"change status for payment {p['id']}")
                elif json_GetState['Status'] in fail_statuses:
                    payment.set_canceled(p['id'], '', f"external_{p['id']}")
                    logger.info(f"change status for payment {p['id']}")


TestPaymentModule().Process()
