# -*- coding: utf-8 -*
import frida
import sys


def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)



jscode = """
Java.perform(function () {
send("start")
var IUserManager = Java.use("android.os.IUserManager");
var UserManager = Java.use("android.os.UserManager");

var UserInfo = Java.use("android.content.pm.UserInfo")
var ActivityManagerNative = Java.use("android.app.ActivityManagerNative")
var Integer = Java.use("java.lang.Integer")
var int = Integer.class.getField("TYPE").get(null)

var Application = Java.use("android.app.Application")
Application.attach.implementation = function(context) {
    console.log("Application.attach()")
    console.log("context:"+context)
    this.attach(context)
    
    //1.开始创建用户
    var mUserManager = context.getSystemService("user")
    mUserManager = Java.cast(mUserManager, UserManager)
    console.log("mUserManager:" + mUserManager)
    var mMyParallelSpaceUserInfo = mUserManager.createProfileForUser("MyParallelSpace", 32, 0)
    
    //2.获取创建的用户id #也可以使用 adb shell dumpsys user查看#
    var users = mUserManager.getUsers()
    console.log("users:"+users)
    for (var i=0; i < users.size(); i++) {
        console.log("user" + i + ":"+users.get(i))
        var UserInfo_id = UserInfo.class.getDeclaredField("id")
        var id = UserInfo_id.get(users.get(i))
        console.log("user" + i + ":"+id)
    }
    
    //3.该用户id设置为影子用户(本例为10)
    var id = 10
    var iActivityManager = ActivityManagerNative.class.getMethod("getDefault", null).invoke(null, null)
    var method_startUserInBackground = ActivityManagerNative.class.getMethod("startUserInBackground", [int])
    var isOK = method_startUserInBackground.invoke(iActivityManager, [Integer.$new(id)])
    console.log("startUserInBackground() userId = " + id + " isOK = " + isOK)
    
    //用户数据地址 /data/data = /data/user/0, /data/user/10
}

send("end")
});
"""


device = frida.get_usb_device()
print('device', device)
process = device.attach('com.android.settings')
print('process', process)
script = process.create_script(jscode)
script.on('message', on_message)
print('[*] nexus-user Start...')
script.load()
sys.stdin.read()
