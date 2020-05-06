# coding:utf8
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import GetConfig as gc
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

#read config
emailcfg = gc.EmailConfig()
email_enable = emailcfg.email_enable()
email_host = emailcfg.email_host()
email_port = emailcfg.email_port()
email_sender = emailcfg.email_sender()
email_password = emailcfg.email_password()
email_receiver = emailcfg.email_receiver()
email_receiver_list = email_receiver.split(',')
email_encrypt = emailcfg.email_encrypt()

def email_switch(func):
    def send():
        if email_enable == 'yes':
            return func()
        else:
            print("The Email swich is off.")
    return send


def send_email(title, content):
    msg = MIMEMultipart()
    msg['Subject'] = title
    msg['From'] = email_sender
    msg['To'] = ",".join(email_receiver_list)
    context = MIMEText(content, _subtype='html', _charset='utf-8')
    msg.attach(context)
    try:
        if email_encrypt == 'ssl':
            send_smtp = smtplib.SMTP_SSL(email_host, 465)
            send_smtp.connect(email_host)
        else:
            send_smtp = smtplib.SMTP()
            if email_encrypt == 'tls':
                send_smtp.connect(email_host, 587)
                send_smtp.ehlo()
                send_smtp.starttls()
            else:
                send_smtp.connect(email_host, email_port)
                send_smtp.ehlo()
    except:
        print("Failed to access smtp server!")
        return False

    try:
        send_smtp.login(email_sender, email_password)
    except:
        print("ID or Password is wrong")
        return False

    try:
        send_smtp.sendmail(email_sender, email_receiver_list, msg.as_string())
    except:
        print("Send Fail, Please check recipient")
        return False

    send_smtp.close()
    print("Send success!")
    return True

@email_switch
def send_warnmail(warninfo_email):
    data_table = ""
    for lstMsg in warninfo_email:
        line_table = """<tr>
                    <td>""" + str(lstMsg[0]) + """</td>
                    <td>""" + str(lstMsg[1]) + """</td>
                    <td>""" + str(lstMsg[2]) + """</td>
                    <td>""" + str(lstMsg[3]) + """</td>
                    <td>""" + str(lstMsg[4]) + """</td>
                </tr>"""
        data_table = data_table + line_table
    content = """\
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>用户未确认预警信息</title>
        <body>
        <div id="container">
          <p><strong>用户未确认预警信息</strong></p>
          <div id="content">
           <table width="500" border="2" bordercolor="red" cellspacing="2">
           <div class="container">
                <div class="row">
                <div class="container">
                  <tr>
                    <th>Time</th>
                    <th>IP</th>
                    <th>Device</th>
                    <th>Level</th>
                    <th>Message</th>
                  </tr>
                  """ + data_table + """
                  </div>
                </div>  
                </div>     
            </table>
          </div>
        </body>
        </html> """
    title = "ClusterIO System Status Alert"
    send_email(title, content)

@email_switch
def send_test():
    title = "This is a HA-AP test email"
    content = "Test"
    send_email(title, content)

@email_switch
def send_live():
    title = "HA-AP Timing alarm clock"
    content = "I'm still alive"
    send_email(title, content)


if __name__ == '__main__':
    send_test()
    # a = [['2020-04-29 16:36:42', '10.203.1.4', 'engine0', 2, 'Engine reboot 6674 secends ago']]
    # send_warnmail(a)
