from  alipay import AliPay

alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw33Gh5+47xMbHRi2FbdBoxJpje8cWtherlkmLbqCn4n8Wgz5dcoCi6YS/hPHHTeqKf6gNw4BnlYEDizpP/SWjD0NyBszn1wuzMX9jF4YwJ/bWOtPaGa91Bu26AGVoyILPtvMIMCMHlrvEOWJ9qcn8Nhf9i3W2nC+eO9OSHE61M1EtosQsqByLck8YmmeuRpPAtU8avUgfuTIQtri3ik3aSjaiqLFpfrBaPL19S9Ax6nfC/ZiI3eof7G0Nph2lt73IrNqOpU226ZetLJyDYp0Ou8kt185tiSeEOKf/ydx83fcSGj99SwnK4xb18/aysJ/LoyMbaGdQ00g/3kQ5GprpQIDAQAB
-----END PUBLIC KEY-----"""

app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAw33Gh5+47xMbHRi2FbdBoxJpje8cWtherlkmLbqCn4n8Wgz5dcoCi6YS/hPHHTeqKf6gNw4BnlYEDizpP/SWjD0NyBszn1wuzMX9jF4YwJ/bWOtPaGa91Bu26AGVoyILPtvMIMCMHlrvEOWJ9qcn8Nhf9i3W2nC+eO9OSHE61M1EtosQsqByLck8YmmeuRpPAtU8avUgfuTIQtri3ik3aSjaiqLFpfrBaPL19S9Ax6nfC/ZiI3eof7G0Nph2lt73IrNqOpU226ZetLJyDYp0Ou8kt185tiSeEOKf/ydx83fcSGj99SwnK4xb18/aysJ/LoyMbaGdQ00g/3kQ5GprpQIDAQABAoIBAC9BXhY2s9uGwM0dxhYlwEYNE1rt6+rB1tFKV4JCTYUHM+sIq9yfQlJDiN/GJCGZ7RZNqKjmR9ngbQaIMLH3C9VGhOhUOvxQqjdxvMKLlGwruDgcWYuhGk4FjQc0KtnORu2g8A0SvkwwKw3ojpsC+RKtGzVFC2SuUDynjELSrCf4MewCkNji47HfSQl4prlqsl05q+azrbPuMS5/BNO0ULCDtOedOD1azMDKW3O5JulC2WJM0HqJiGWGXZTeqI9O1NbZZwQDMeJPJGZHcEaivgvoI3S4/0iqK+yhMaGLeFZXsRChzwKTu2Qjf5tFvFg4uyEwjfBCvv2xqO6iICw5tYECgYEA9zpSQsY6YbeSQTQiqs1w+jNLdqwJlk6rXI2U3fPKJ3/53fu6uSnNiJu0pmpI2JtMxMRW8afEGnLbq/WoSEgsgm8rp7K+I+2smRPXO/jPyy14KPHpBG5CZk0J6llHBo+7sv77jZRz6rqFn1CI5Im4Efen4RnHW60LaR/c/5/Mf3UCgYEAym2CQIDxF4cBQIaDc3uvWKAoYGtRNZVJuVPcP+LjHKGXGI6+Kl75xJ76DHqiPE89a2Hc3ZIhdQzjbUNsQ2mQa+IhcIvganU2+Rb8Q8h4yGyLc6lWNknEWG0+1XhrCcntfWiJZpx3PigRTxVUm1dKjuyxje+vOBw9zCpIN/LJZXECgYBRP6d9LmxNZOj56Mpj27R/ZZAtZgiYjy4d8qGz98S+Cn7xhyMsayKS/Kj38AIUvaUTHXt9W6dFEe5Dqy4s4xtNmn98U2/NmvSYMj8QBIs1uLG+sxHjVOEZgcP6cnC3JVGIV+gP9XPK9pWnb+4tPV1y+jL/9VrhNBOF7uTQVZH9aQKBgH8kdxoioss/PZcUpb3EIudMeO/OmAxKvyqLNJxf2nwiNm/zQBgG3WQU4kMyR3IP5yjqJ7p3TVJijPoUzgwtYsuQFabGBGd5RdUADeRZJxvjqVc1NfQVMyDDRSL5ZmmYjfUl0p9DiVXd/rkoUaLcGfVZT1AyCmD4xAvXRtL1SG/RAoGBAJGhRj7R+E975ckb1bdDlR1mRWTvH14VTdamzi/L9jGY2x2aUISMAiZ/PdJTXtDHtqqLpOBSUoCIe60lQw07K6+G5LpY3ltTqiuUt6yyxZztvJCHEB4bSat8xYyN4G8eC5OnXrg658L+OR8Bp8obtLwNf3t9VQBOUqLldc2TcP3e
-----END RSA PRIVATE KEY-----"""

#实例化支付应用
alipay = AliPay(
    appid='2016101000652521',
    app_notify_url=None,
    app_private_key_string=app_private_key_string,
    alipay_public_key_string=alipay_public_key_string,
    sign_type='RSA2'
)

#发起支付请请求
order_string = alipay.api_alipay_trade_page_pay(
    out_trade_no="10003", #订单号
    total_amount=str(200000),#支付金额
    subject="西瓜", #交易主题
    return_url=None,
    notify_url=None
)

print("https://openapi.alipaydev.com/gateway.do?"+order_string)