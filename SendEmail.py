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
email_host_port = emailcfg.email_host_port()
email_enable = emailcfg.email_enable()
email_host = emailcfg.email_host()
email_password = emailcfg.email_password()
email_sender = emailcfg.email_sender()
email_receiver = emailcfg.email_receiver()
email_receiver_list = email_receiver.split(',')
email_sub = emailcfg.email_sub()
email_ssl = emailcfg.email_ssl()
email_host_port_ssl = emailcfg.email_host_port_ssl()


def send_email(content):
    msg = MIMEMultipart()
    msg['Subject'] = email_sub
    msg['From'] = email_sender
    msg['To'] = ",".join(email_receiver_list)
    context = MIMEText(content, _subtype='html', _charset='utf-8')
    msg.attach(context)
    try:
        if email_ssl == 'yes':
            send_smtp = smtplib.SMTP_SSL(email_host, email_host_port_ssl)
            send_smtp.connect(email_host)
        else:
            send_smtp = smtplib.SMTP()
            send_smtp.connect(email_host, email_host_port)
            send_smtp.ehlo()
            send_smtp.starttls()
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


def send_warnmail(warninfo_email):
    if email_enable == 'no':
        return
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
    html = """\
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
    send_email(html)


def send_test():
    text = "This is a HA-AP test email!"
    send_email(text)

def send_live():
    text = "I'm still alive"
    send_email(text)
