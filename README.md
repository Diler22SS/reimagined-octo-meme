# billmanager_paymethod
Создание метода оплаты Tinkoff для billmanager 

## Структура по файлам
- payment.py  - базовые классы для реализации cgi и модуля обработки
- billmgr_mod_testpayment.xml - xml с данными для формы настройки
- pmtestpayment.py - модуль обработки
- testpayment.py - cgi при перехода в платежную систему Tinkoff

## Установка окружения
1. cd <директория с проектом>
2. python3 -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt

## Размещение в структуре BILLmanager
1. cp ./billmgr_mod_testpayment.xml /usr/local/mgr5/etc/xml/
2. ln -s ./pmtestpayment.py /usr/local/mgr5/paymethods/pmtestpayment
3. ln -s ./testpayment.py /usr/local/mgr5/cgi/testpayment
Необходимо проверить права доступа.

## ЧТО РЕАЛИЗОВАНО
- Переход в платежную систему
- Перенаправление на successurl после успешной оплаты
- Обновление состояния платежа (checkpay)
- Валидация при настройке метода оплаты
- Добавлен Jinja2
