#!/bin/bash

#短信接口的用户名
messusername=aaa

#短信接口的密码
messpwd=bbb

#报警短信需要发送的手机号
alertmobile=13900000058
date=$(date +"%Y-%m-%d_%H:%M:%S")

#获取apache的进程号
apachecheck=`pgrep httpd`
if [ -n "$apachecheck" ]; then
        exit
else
#没有apache的进程则使用curl调用短信接口
        msg="apache_error_at_"$date
        curl -d "func=sendsms&username="$messusername"&password="$messpwd"&mobiles="$alertmobile"&message="$msg"&smstype=0&timerflag=0&timervalue=&timertype=0&timerid=0" "http://短信接口的url（找第三方申请，有免费的）"
	#尝试启动apache（apachectl根据自己的系统路径写，都不一样）
        /app/apache2/bin/apachectl start
fi

#同apache一样监控mysql进程
mysqlcheck=`pgrep mysql`

if [ -n "$mysqlcheck" ]; then
        exit
else
        msg="mysql_error_at_"$date
        curl -d "func=sendsms&username="$messusername"&password="$messpwd"&mobiles="$alertmobile"&message="$msg"&smstype=0&timerflag=0&timervalue=&timertype=0&timerid=0" "http://短信接口的url"
	#尝试启动mysql（启动方式根据自己的系统启动方式写）
        /app/mysql/bin/mysqld_safe &
fi

#ping检测，检测其它服务器是否存活，ping三次
ping=`ping -c 3 192.168.1.1|awk 'NR==7 {print $4}'`
if [ $ping != 0 ];then
        exit
else
        msg="192.168.1.1_server_error_at_"$date
        curl -d "func=sendsms&username="$messusername"&password="$messpwd"&mobiles="$alertmobile"&message="$msg"&smstype=0&timerflag=0&timervalue=&timertype=0&timerid=0" "http://短信接口的url"
fi
