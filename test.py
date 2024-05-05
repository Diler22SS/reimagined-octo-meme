from jinja2 import Template
payment_tm = Template('''<html>
<head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>
<link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />"
    <script language='JavaScript'>
        function DoSubmit() {
            window.location.assign({{ redirect_url }});
        }
    </script>
</head>
<body onload='DoSubmit()'>
</body>
</html>
''')
redirect_url = 'https://www.youtube.com/feed/subscriptions'
payment_form = payment_tm.render(redirect_url=redirect_url)

print(payment_form)