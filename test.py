import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET


string = '<?xml version="1.0" encoding="UTF-8"?>\n<doc><terminalkey private="yes">TinkoffBankTest</terminalkey><terminalpsw private="yes">TinkoffBankTest</terminalpsw></doc>\n'
a = ET.fromstring(string)

print(a.find('terminalkey').text)
    # # Получение состояния платежа от платежной системы
    # data_GetState = dict()
    # data_GetState['TerminalKey'] = p["terminalkey"]
    # data_GetState['PaymentId'] = p["PaymentId"]
    # data_GetState['Token'] = payment.gen_token(data_GetState, p["terminalpsw"])
    # logger.info(f"data_GetState = {data_GetState}")
    
    # r_GetState = requests.post('https://securepay.tinkoff.ru/v2/GetState', 
    #             headers={"Content-Type": "application/json"}, 
    #             data = json.dumps(data_GetState))
    # logger.info(f"r_GetState = {r_GetState.json()}")
    
    
    # logger.info(f"change status for payment {p['id']}")
    # payment.set_paid(p['id'], '', f"external_{p['id']}")