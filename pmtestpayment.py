#!/usr/bin/python3

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET

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
        if float(minamount_node.text) <= 10:
            raise billmgr.exception.XmlException('wrong_terminal_info')

    # проверить оплаченные платежи
    # реализация --command checkpay
    # здесь делаем запрос в БД, получаем список платежей в статусе "оплачивается"
    # идем в платежку и проверяем прошли ли платежи
    # если платеж оплачен, выставляем соответствующий статус c помощью функции set_paid
    
    # в тестовом примере получаем необходимые платежи
    # и переводим их все в статус 'оплачен'
    def CheckPay(self):
        logger.info("run checkpay")

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmtestpayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmtestpayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')

        for p in payments:
            logger.info(f"change status for payment {p['id']}")
            payment.set_paid(p['id'], '', f"external_{p['id']}")


TestPaymentModule().Process()
