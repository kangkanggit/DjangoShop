import smtplib #登陆邮件服务器，进行邮件发送
from email.mime.text import MIMEText #负责构建邮件格式

subject = "陈康的祝福邮件"
content = "<p>你好<p>"
sender = "1529825704@qq.com"
recver = """1529825704@qq.com,
215558997@qq.com,"""

password = "rujtmgdrgpihijdj"

#plan文本
message = MIMEText(content,"plain","utf-8")
message["Subject"] = subject
message["To"] = recver
message["From"] = sender

smtp = smtplib.SMTP_SSL("smtp.qq.com",465)
smtp.login(sender,password)
smtp.sendmail(sender,recver.split(",\n"),message.as_string())
smtp.close()

