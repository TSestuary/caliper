#!/usr/bin/env python
#-*- encoding:UTF-8 -*-

import os
import time
from Tkinter import *
import tkMessageBox
import ttk
import threading,thread
from subprocess import Popen, PIPE
import pexpect
import shutil
from ScrolledText import ScrolledText


path =  os.getcwd()
if os.path.exists(os.path.join(path, 'caliper')):
    if os.path.isfile(os.path.join(path, 'caliper')):
        script_path = os.path.join(path, 'utils/automation_scripts/Scripts')
    else:
        script_path = os.path.join(path, 'caliper/utils/automation_scripts/Scripts')
else:
    script_path = os.path.join(path, 'Scripts')

caliper_output_path = os.path.join(os.environ['HOME'], 'caliper_output')
if not os.path.exists(caliper_output_path):
    os.makedirs(caliper_output_path,0775)
target_log_path = caliper_output_path + os.sep + 'target_export_log.txt'
host_log_path = caliper_output_path + os.sep + 'host_export_log.txt'
node_log_path = caliper_output_path + os.sep + 'TestNode_export_log.txt'
log_file = ['%s/target_dependency_output_summary.txt'%caliper_output_path, '%s/TestNode_dependency_output_summary.txt'%caliper_output_path, '%s/host_dependency_output_summary.txt'%caliper_output_path, target_log_path, host_log_path, node_log_path]
for log in log_file:
    if os.path.exists(log):
        os.remove(log)

class Result():
    def __init__(self):
        pass
    def target_result(self):
        self.top = Toplevel()
        self.top.title('target install result')
        f = open('%s/caliper_output/target_dependency_output_summary.txt'%os.environ['HOME'])
        lines = f.read().split('\n')
        for line in lines:
            line = line.replace('\n', '').replace('\t', '').replace('\t', '')
            if line != '':
                if 'ERROR-IN-AUTOMATION' in line:
                    line = line.split(':')[1]
                    Label(self.top, text=line, fg = 'RED').grid(sticky=W)
                else:
                    Label(self.top, text=line).grid(sticky=W)

    def open_target_log(self):
        tkMessageBox.showinfo("target log", "target log path : %s"%target_log_path)
        # os.system("gedit '%s'"%target_log_path)

    def node_result(self):
        self.top = Toplevel()
        self.top.title('node install result')
        f = open('%s/caliper_output/TestNode_dependency_output_summary.txt'%os.environ['HOME'])
        lines = f.read().split('\n')
        for line in lines:
            line = line.replace('\n', '').replace('\t', '').replace('\t', '')
            if line != '':
                if 'ERROR-IN-AUTOMATION' in line:
                    line = line.split(':')[1]
                    Label(self.top, text=line, fg = 'RED').grid(sticky=W)
                else:
                    Label(self.top, text=line).grid(sticky=W)

    def open_node_log(self):
        tkMessageBox.showinfo("node log", "node log path : %s" % node_log_path)
        # os.system("gedit '%s'"%node_log_path)

    def host_result(self):
        self.top = Toplevel()
        self.top.title('host install result')
        f = open('%s/caliper_output/host_dependency_output_summary.txt'%os.environ['HOME'])
        lines = f.read().split('\n')
        for line in lines:
            line = line.replace('\n', '').replace('\t', '').replace('\t', '')
            if line != '':
                if 'ERROR-IN-AUTOMATION:' in line:
                    line = line.split(':')[1]
                    Label(self.top, text=line, fg = 'RED').grid(sticky=W)
                else:
                    Label(self.top, text=line).grid(sticky=W)

    def open_host_log(self):
        tkMessageBox.showinfo("host log", "host log path : %s" % host_log_path)
        # os.system("gedit '%s'"%host_log_path)

class install_caliper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    '''install caliper'''
    def run(self):
        os.chdir('caliper')
        exec_log(host_text, 'git branch -a', host_log_path)
        if len(sys.argv)>1:
            exec_log(host_text, 'git checkout download_caliper', host_log_path)
        else:
            exec_log(host_text, 'git checkout caliper_deploy_gui', host_log_path)
        display_line(host_text,'Start install caliper ...')
        install_caliper = pexpect.spawn('sudo python setup.py install', timeout=180)
        try:
            input_password = install_caliper.expect(["[sudo]"])
            if input_password == 0:
                install_caliper.sendline(host_pc_password_value)
            for line in install_caliper.readlines():
                display_line(host_text, line)
        except pexpect.TIMEOUT:
            display_line(host_text, 'timeout!')

class download(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    '''creat caliper_outpt folder for collect caliper log and result'''
    def create_dir(self, mode=0755):
        CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], 'caliper_output')
        if not os.path.exists(CALIPER_TMP_DIR):
            os.makedirs(CALIPER_TMP_DIR, mode)

    '''download caliper code'''
    def clone(self):
        if len(sys.argv)>1:
            exec_log(host_text, 'git clone https://github.com/Putter/caliper.git 2>&1', host_log_path)
        else:
            exec_log(host_text, 'git clone https://github.com/TSestuary/caliper.git 2>&1', host_log_path)

    def judge_tool_installed(self, tool):
        try:
            output = Popen('which %s'%tool, shell=True, stdout=PIPE)
        except Exception:
            return 0
        else:
            if output.stdout.readlines():
                display_line(host_text, "%s is already installed" % (tool))
                return 1
            else:
                return 0

    def judge_dependent_installed(self, tool):
        try:
            output = os.popen("dpkg-query -W -f='${Status}' %s | grep -c "+'"ok installed"'%tool).read()
        except Exception:
            return 0
        else:
            if '0' in output:
                return 0
            else:
                return 1

    def run_install(self):
        tool_list = ['python', 'git']
        for tool in tool_list:
            flag = self.judge_tool_installed(tool)
            if flag != 1:
                try:
                    display_line(host_text, "apt-get update")
                    update_apt = pexpect.spawn('sudo apt-get update', timeout=60)
                    try:
                        input_password = update_apt.expect(["[sudo]"])
                        if input_password == 0:
                            update_apt.sendline(host_pc_password_value)
                    except pexpect.TIMEOUT:
                        display_line(host_text,
                                     'timeout!Maybe you are uisng non-English OS. Please change to  English OS or set env LANG=C')
                    display_line(host_text, update_apt.readlines(-1))
                    display_line(host_text, "install %s" % tool)
                    update_tool = pexpect.spawn('sudo apt-get install %s' % tool, timeout=60)
                    try:
                        input_password = update_tool.expect(["[sudo]"])
                        if input_password == 0:
                            update_tool.sendline(host_pc_password_value)
                            for line in update_tool.readlines():
                                print line
                                display_line(host_text, line)
                    except pexpect.TIMEOUT:
                        display_line(host_text, 'timeout!Maybe you are uisng non-English OS. Please change to  English OS or set env LANG=C')
                    try:
                        input_c = update_tool.expect(["continue?"], timeout=60)
                        if input_c == 0:
                            update_tool.sendline("Y")
                            for line in update_tool.readlines():
                                print line
                                display_line(host_text, line)
                    except pexpect.TIMEOUT:
                        display_line(host_text, 'timeout!Maybe you are uisng non-English OS. Please change to  English OS or set env LANG=C')
                except OSError, e:
                    display_line(host_text, e)
                    pass
        display_line(host_text, 'Start download ...')
        self.clone()
        display_line(host_text, '*******************Download finished**********************')

    def run(self):
        version = os.popen('cat /etc/issue').read().replace('\n','')
        print version
        display_line(host_text, version)
        global host_pc_password_value
        host_pc_password_value = host_pc_password.get()
        # check os version, caliper only support ubuntu 16.04 and ubuntu 14.04
        if '16.04' in version:
            self.run_install()
            install_caliper_button.configure(state=NORMAL)
            host_install_button.configure(state=NORMAL)
        elif '14.04' in version:
            self.run_install()
            install_caliper_button.configure(state=NORMAL)
            host_install_button.configure(state=NORMAL)
        else:
            display_line(host_text, 'OS error : caliper only support ubuntu 16.04 and ubuntu 14.04')

class install_dependency_thread(threading.Thread):
    def __init__(self, dependency, display, run_command):
        threading.Thread.__init__(self)
        self.command = run_command
        self.display = display
        self.dependency = dependency

    def run(self):
        if self.dependency == 'target':
            target_gpw_pb_ivar.set(0)
            target_log_button.configure(state=DISABLED)
            target_view_button.configure(state=DISABLED)
            target_install_button.configure(state=DISABLED)
            os.chdir(script_path)
            exec_log(self.display, self.command, target_log_path)
            # self.copy_key(target_ip_value, target_password_value)
            target_gpw_pb_ivar.set(29)
            target_log_button.configure(state=NORMAL)
            target_install_button.configure(state=NORMAL)
            target_view_button.configure(state=NORMAL)
            display_line(target_text, '*******************Install finished**********************')
        elif self.dependency == 'TestNode':
            node_gpw_pb_ivar.set(0)
            node_log_button.configure(state=DISABLED)
            node_view_button.configure(state=DISABLED)
            node_install_button.configure(state=DISABLED)
            os.chdir(script_path)
            exec_log(self.display, self.command, node_log_path)
            # self.copy_key(node_ip_value, node_password_value)
            node_gpw_pb_ivar.set(7)
            node_view_button.configure(state=NORMAL)
            node_install_button.configure(state=NORMAL)
            node_log_button.configure(state=NORMAL)
            display_line(node_text, '*******************Install finished**********************')
        os.chdir(path)

    def copy_key(self, dependency_ip_value, dependency_password_value):
        ssh_check = os.popen('ls %s/.ssh/' % os.environ['HOME'])
        ssh_check = ssh_check.read()
        if '.pub' in ssh_check:
            try:
                child = pexpect.spawn('ssh-copy-id -i %s/.ssh/id_rsa.pub root@%s'%(os.environ['HOME'], dependency_ip_value), timeout=5)
                input_password = child.expect(["sudo", pexpect.TIMEOUT])
                if input_password == 0:
                    child.sendline(dependency_password_value)
                    # child.sendline(dependency_password_value+'\r')
                elif input_password == 1:
                    display_line(self.display, '********************ssh copy time out***********************')
                    f = open('%s/caliper_output/%s_dependency_output_summary.txt' % (os.environ['HOME'], self.dependency),'a')
                    f.write('ERROR-IN-AUTOMATION:Fail to cp ssh key \n')
                    f.close()
                print child.after
                print child.before
                display_line(self.display, child.before)  # Print the result of the ls command.
            except pexpect.EOF , e:
                display_line(self.display, e)
                f = open('%s/caliper_output/%s_dependency_output_summary.txt' % (os.environ['HOME'], self.dependency), 'a')
                f.write('ERROR-IN-AUTOMATION:Fail to cp ssh key \n')
                f.close()
        else:
            f = open('%s/caliper_output/%s_dependency_output_summary.txt' % (os.environ['HOME'], self.dependency), 'a')
            f.write('ERROR-IN-AUTOMATION:No id_rsa.pub file\n')
            f.close()

class install_host_thread(threading.Thread):
    def __init__(self, run_command):
        threading.Thread.__init__(self)
        self.command = run_command

    def run(self):
        global host_pc_password_value
        host_pc_password_value = host_pc_password.get()
        host_view_button.configure(state=DISABLED)
        host_install_button.configure(state=DISABLED)
        host_log_button.configure(state=DISABLED)
        #check expect
        output = Popen('which expect', shell=True, stdout=PIPE)
        if not output.stdout.readlines():
            display_line(host_text, 'Install expect......')
            expect_install = pexpect.spawn('sudo apt-get install expect', timeout=60)
            try:
                install_expect = expect_install.expect(["[sudo]", pexpect.TIMEOUT])
                if install_expect == 0:
                    expect_install.sendline(host_pc_password_value)
                    display_line(host_text, expect_install.before)
            except pexpect.TIMEOUT:
                display_line(host_text,
                            'timeout!Maybe you are uisng non-English OS. Please change to  English OS or set env LANG=C')
            try:
                install_yes = expect_install.expect(["continue?", pexpect.TIMEOUT])
                if install_yes == 0:
                    expect_install.sendline('y')
                    display_line(host_text, expect_install.before)
            except pexpect.TIMEOUT:
                display_line(host_text,
                             'timeout!Maybe you are uisng non-English OS. Please change to  English OS or set env LANG=C')
        script_path = os.path.join(path, 'caliper/utils/automation_scripts/Scripts')
        os.chdir(script_path)
        exec_log(host_text, self.command, host_log_path)
        shutil.copyfile( os.path.join(script_path, 'host_dependency_dir/host_dependency_output_summary.txt'), '%s/caliper_output/host_dependency_output_summary.txt' % (os.environ['HOME']))
        ssh_check = os.popen('ls %s/.ssh/'%(os.environ['HOME']))
        ssh_check = ssh_check.read()
        if '.pub' not in ssh_check:
            try:
                f = open('%s/caliper_output/host_dependency_output_summary.txt' % (os.environ['HOME']),
                         'a+')
                child = pexpect.spawn('ssh-keygen -t rsa', timeout=5)
                except_co = child.expect(["Enter file in which to save the key", pexpect.TIMEOUT])
                if except_co == 0:
                    print 'enter'
                    child.send('\r')
                if except_co == 1:
                   pass
                Overwrite = child.expect(["Overwrite (y/n)?", pexpect.TIMEOUT])
                if Overwrite == 0:
                    child.sendline('y')
                else:
                    f.write('ERROR-IN-AUTOMATION:Fail to create ssh key ')

                enter_passphrase = child.expect(["Enter passphrase", pexpect.TIMEOUT])
                if enter_passphrase == 0:
                    child.send('\r')
                else:
                    f.write('ERROR-IN-AUTOMATION:Fail to create ssh key ')
                enter_same = child.expect(["Enter same passphrase again:", pexpect.TIMEOUT])
                if enter_same == 0:
                    child.send('\r')
                else:
                    f.write('ERROR-IN-AUTOMATION:Fail to create ssh key ')
                display_line(host_text, child.before)  # Print the result of the ls command.
            except pexpect.EOF, e:
                print 'fail'
                display_line(host_text, e)
                host_log = open(host_log_path)
                host_log.write(e)
                host_log.close()
                f = open('%s/caliper_output/host_dependency_output_summary.txt' % (os.environ['HOME']), 'a+')
                f.write('ERROR-IN-AUTOMATION:Fail to create ssh key ')
                f.close()
        os.chdir(path)
        gpw_pb_ivar.set(33)
        display_line(host_text, '*******************Install finished**********************')
        host_install_button.configure(state=NORMAL)
        host_view_button.configure(state=NORMAL)
        host_log_button.configure(state=NORMAL)

def exec_log(display, command, text):
    f = open(text, 'a+')
    try:
        if (command != ""):
            adb_pipe = Popen(command, stdin=PIPE, stdout=PIPE, bufsize=1, shell=True)
            for line in iter(adb_pipe.stdout.readline, ''):
                print line
                display_line(display, line)
                f.write(line)
                if 'host finished' in line:
                    gpw_pb_ivar.set(gpw_pb_ivar.get() + 1)
                if 'host finished install' in line:
                    line = line.split('finished')[1].replace(' ', '', 1).replace('\n', '') + ' finished'
                    display_status(status_host, line)
                if 'host ERROR-IN-AUTOMATION' in line:
                    line = line.split(':')[1]
                    display_status(status_host, line)
                if 'target finished' in line:
                    target_gpw_pb_ivar.set(target_gpw_pb_ivar.get() + 1)
                if 'target finished install' in line:
                    line = line.split('finished')[1].replace(' ', '', 1).replace('\n', '') + ' finished'
                    display_status(status_target, line)
                if 'target ERROR-IN-AUTOMATION' in line:
                    line = line.split(':')[1]
                    display_status(status_target, line)
                if 'TestNode successful' in line:
                    node_gpw_pb_ivar.set(node_gpw_pb_ivar.get() + 1)
                if 'TestNode successful install' in line:
                    line = line.split('successful')[1].replace(' ', '', 1).replace('\n', '')+' finished'
                    display_status(status_node, line)
                if 'TestNode ERROR-IN-AUTOMATION' in line:
                    line = line.split(':')[1]
                    display_status(status_node, line)
    except OSError, e:
        display_line(display, e)
        f.write(e)

# display log
def display_line(display, line):
    display.grid(row=20, column=0, columnspan=10, rowspan=10, sticky=W+E+N+S)
    display.insert(INSERT, "%s\n" % line)
    display.see(END)
    display.update()

# display install status
def display_status(statu, line):
    statu.insert(INSERT, "%s\n" % line)
    statu.see(END)
    statu.update()

def target_install():
    # global define target_user and target_ip value
    global target_user_value, target_ip_value, target_password_value
    target_user_value = entries[0].get()
    target_ip_value = entries[1].get()
    target_password_value = password_entry.get()
    run_command = './target_dependency.exp y %s %s %s %s'%(target_user_value, target_ip_value, target_password_value, os.environ['HOME'])
    #Thread
    Thread_test = install_dependency_thread('target', target_text, run_command)
    Thread_test.start()

def host_install():
    Thread_test = install_host_thread('./host_dependency.exp y %s'%(host_pc_password_value))
    Thread_test.start()

def node_install():
    global node_ip_value, node_password_value
    node_password_value = node_password_entry.get()
    node_user_value = node_entries[0].get()
    node_ip_value = node_entries[1].get()
    Thread_test = install_dependency_thread('TestNode', node_text, './TestNode_dependency.exp y %s %s %s %s'%(node_user_value, node_ip_value, node_password_value, os.environ['HOME']))
    Thread_test.start()

def download_code():
    download_code = download()
    download_code.start()

if __name__ == "__main__":
    master = Tk()
    var = IntVar()
    master.resizable(0, 0)
    master.geometry('%dx%d'%(640, 600))
    master.title('Caliper Installer')

    #create note book
    tabControl = ttk.Notebook(master)
    host_ui = ttk.Frame(tabControl)  # Add a second tab
    tabControl.add(host_ui, text='Host')  # Make Host tab visible
    target_ui = ttk.Frame(tabControl)  # Create a tab
    tabControl.add(target_ui, text='Target')  # Add Target tab
    node_ui = ttk.Frame(tabControl)  # Add a third tab
    tabControl.add(node_ui, text='TestNode')  # Make TestNode tab visible
    tabControl.pack(expand=1, fill="both") # Pack to make visible

    #make target ui
    #weight layout
    Label(target_ui, text="target user: ").grid(sticky=W)
    Label(target_ui, text="target ip: ").grid(sticky=W)
    Label(target_ui, text="target password: ").grid(sticky=W)

    #value weight
    akt_b, entries = [], []
    # i value is:target_user, target_ip, target_password, disk_name
    for i in range(0,2):
        akt_bb = StringVar()
        entry = Entry(target_ui, width=40)
        entry.grid(row=i, column=1, sticky=W)
        entries.append(entry)

    password_entry = Entry(target_ui, width=40, show = '*')
    password_entry.grid(row=2, column=1, sticky=W)

    #Install button
    global target_install_button
    target_install_button = Button(target_ui, text='Install', command=target_install)
    target_install_button.grid(row=6, column=2)

    #View result button
    global target_view_button
    result = Result()
    target_view_button = Button(target_ui, text='View result', command=result.target_result)
    target_view_button.grid(row=6, column=3)
    target_view_button.configure(state = DISABLED)

    # log button
    global target_log_button
    target_log_button = Button(target_ui, text='Log', command=result.open_target_log)
    target_log_button.grid(row=6, column=4)
    target_log_button.configure(state=DISABLED)

    global target_gpw_pb_ivar
    target_var = IntVar()
    target_gpw_pb_ivar = target_var
    target_gpw_pb_ivar.set(0)
    target_progressbar = ttk.Progressbar(target_ui, mode='determinate', maximum=29, variable=target_gpw_pb_ivar)
    target_progressbar.grid(row=8, column=0, columnspan=10, rowspan=1, sticky=W + E + N + S)

    #make host ui
    Label(host_ui, text="host pc password: ").grid(sticky=W)

    #weight layout
    # package_installation_choice.grid(row=0, column=1, sticky=W)
    host_pc_password = Entry(host_ui, width=25, show = '*')
    host_pc_password.grid(row=0, column=1, sticky=W)

    # Download button
    download_button = Button(host_ui, text='download caliper', command=download_code)
    download_button.grid(row=6, column=1, sticky=E)

    global install_caliper_button
    install = install_caliper()
    install_caliper_button = Button(host_ui, text='Install Caliper', command=install.start)
    install_caliper_button.grid(row=6, column=2)
    install_caliper_button.configure(state=DISABLED)

    #Install button
    global host_install_button
    host_install_button = Button(host_ui, text='Install', command=host_install)
    host_install_button.grid(row=6, column=3)
    host_install_button.configure(state=DISABLED)

    #View result button
    global host_view_button
    host_view_button = Button(host_ui, text='View result', command=result.host_result)
    host_view_button.grid(row=6, column=4)
    host_view_button.configure(state = DISABLED)

    # log button
    global host_log_button
    host_log_button = Button(host_ui, text='Log', command=result.open_host_log)
    host_log_button.grid(row=6, column=5)
    host_log_button.configure(state=DISABLED)

    global gpw_pb_ivar
    gpw_pb_ivar = var
    gpw_pb_ivar.set(0)
    progressbar = ttk.Progressbar(host_ui, mode='determinate', maximum = 33, variable = gpw_pb_ivar)
    progressbar.grid(row=8, column=0, columnspan=10, rowspan=1, sticky=W+E+N+S)

    stauts_label = ttk.LabelFrame(host_ui, text='status')
    stauts_label.grid(row=9, column=0, columnspan=10, rowspan=10, padx=8, pady=4, sticky=W+E+N+S)

    target_stauts_label = ttk.LabelFrame(target_ui, text='status')
    target_stauts_label.grid(row=9, column=0, columnspan=10, rowspan=10, padx=8, pady=4, sticky=W + E + N + S)

    global status_host, status_target
    status_host = ScrolledText(stauts_label, bg='white', height = 8, width=85)
    status_host.grid(row=0, column=0, sticky=E)
    status_target = ScrolledText(target_stauts_label, bg='white', height=8, width=85)
    status_target.grid(row=0, column=0, sticky=E)


    #export log
    host_log_label = ttk.LabelFrame(host_ui, text='log')
    host_log_label.grid(row=20, column=0, columnspan=10, rowspan=10, padx=8, pady=4, sticky=W + E + N + S)
    target_log_label = ttk.LabelFrame(target_ui, text='log')
    target_log_label.grid(row=20, column=0, columnspan=10, rowspan=10, padx=8, pady=4, sticky=W + E + N + S)


    global host_text, target_text, node_text
    host_text = ScrolledText(host_log_label, height = 20, bg='white', width=85)
    target_text = ScrolledText(target_log_label, height=20, bg='white', width=85)


    #make node ui
    #weight layout
    Label(node_ui, text="TestNode user: ").grid(sticky=W)
    Label(node_ui, text="TestNode ip: ").grid(sticky=W)
    Label(node_ui, text="TestNode password: ").grid(sticky=W)

    #value weight
    node_entries = []
    # i value is:target_user, target_ip, target_password, disk_name
    for i in range(0,2):
        node_entry = Entry(node_ui, width=37)
        node_entry.grid(row=i, column=1, sticky=W)
        node_entries.append(node_entry)

    node_password_entry = Entry(node_ui, width=37, show = '*')
    node_password_entry.grid(row=2, column=1, sticky=W)

    #Install button
    global node_install_button
    node_install_button = Button(node_ui, text='Install', command=node_install)
    node_install_button.grid(row=6, column=2)

    #View result button
    global node_view_button
    result = Result()
    node_view_button = Button(node_ui, text='View result', command=result.node_result)
    node_view_button.grid(row=6, column=3)
    node_view_button.configure(state = DISABLED)

    # log button
    global node_log_button
    node_log_button = Button(node_ui, text='Log', command=result.open_node_log)
    node_log_button.grid(row=6, column=4)
    node_log_button.configure(state=DISABLED)

    global node_gpw_pb_ivar
    node_var = IntVar()
    node_gpw_pb_ivar = node_var
    node_gpw_pb_ivar.set(0)
    target_progressbar = ttk.Progressbar(node_ui, mode='determinate', maximum=7, variable=node_gpw_pb_ivar)
    target_progressbar.grid(row=8, column=0, columnspan=10, rowspan=1, sticky=W + E + N + S)


    global status_node
    node_stauts_label = ttk.LabelFrame(node_ui, text='status')
    node_stauts_label.grid(row=9, column=0, columnspan=10, rowspan=10, padx=8, pady=4, sticky=W + E + N + S)
    status_node = ScrolledText(node_stauts_label, bg='white', height=8, width=85)
    status_node.grid(row=0, column=0, sticky=E)
    node_log_label = ttk.LabelFrame(node_ui, text='log')
    node_log_label.grid(row=20, column=0, columnspan=10, rowspan=10, padx=8, pady=4, sticky=W + E + N + S)
    node_text = ScrolledText(node_log_label, height=20, bg='white', width=85)

    #loop tk
    mainloop()


