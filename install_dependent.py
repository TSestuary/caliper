#!/usr/bin/env python
#-*- encoding:UTF-8 -*-

import os
from Tkinter import *
import tkMessageBox
import ttk
import threading
from subprocess import Popen, PIPE
import pexpect
import shutil

path =  os.getcwd()
script_path = os.path.join(path, 'utils/automation_scripts/Scripts')
home_path = os.getcwd().split('/')
caliper_output_path = os.path.join(os.environ['HOME'], 'caliper_output')
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

class install_dependency_thread(threading.Thread):
    def __init__(self, dependency, display, run_command):
        threading.Thread.__init__(self)
        self.command = run_command
        self.display = display
        self.dependency = dependency

    def run(self):
        if self.dependency == 'target':
            target_log_button.configure(state=DISABLED)
            target_view_button.configure(state=DISABLED)
            target_install_button.configure(state=DISABLED)
            os.chdir(script_path)
            exec_log(self.display, self.command, target_log_path)
            self.copy_key(target_ip_value, target_password_value)
            target_log_button.configure(state=NORMAL)
            target_install_button.configure(state=NORMAL)
            target_view_button.configure(state=NORMAL)
            display_line(target_text, '*******************Install finished**********************')
        elif self.dependency == 'TestNode':
            node_log_button.configure(state=DISABLED)
            node_view_button.configure(state=DISABLED)
            node_install_button.configure(state=DISABLED)
            os.chdir(script_path)
            exec_log(self.display, self.command, node_log_path)
            self.copy_key(node_ip_value, node_password_value)
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
                input_password = child.expect(["password", pexpect.TIMEOUT])
                if input_password == 0:
                    child.sendline(dependency_password_value)
                elif input_password == 1:
                    display_line(self.display, '********************ssh copy time out***********************')
                    f = open('%s/caliper_output/%s_dependency_output_summary.txt' % (os.environ['HOME'], self.dependency),'a')
                    f.write('ERROR-IN-AUTOMATION:Fail to cp ssh key \n')
                    f.close()
                display_line(self.display, child.before)  # Print the result of the ls command.
            except pexpect.EOF , e:
                display_line(self.display, e)
                f = open('%s/caliper_output/%s_dependency_output_summary.txt' % (os.environ['HOME'], self.dependency), 'a+')
                f.write('ERROR-IN-AUTOMATION:Fail to cp ssh key ')
                f.close()
        else:
            f = open('%s/caliper_output/%s_dependency_output_summary.txt' % (os.environ['HOME'], self.dependency), 'a+')
            f.write('ERROR-IN-AUTOMATION:No id_rsa.pub file')
            f.close()

class install_host_thread(threading.Thread):
    def __init__(self, run_command):
        threading.Thread.__init__(self)
        self.command = run_command

    def run(self):
        host_view_button.configure(state=DISABLED)
        host_install_button.configure(state=DISABLED)
        host_log_button.configure(state=DISABLED)
        #check expect
        expect_check = os.popen("dpkg-query -W -f='${Status}' expect | grep -c "+'"ok installed"')
        expect_check = expect_check.read().replace('\n', '')
        print expect_check
        if int(expect_check) != 1:
            display_line(host_text, 'Install expect......')
            expect_install = pexpect.spawn('sudo apt-get install expect', timeout=5)
            try:
                install_expect = expect_install.expect(["[sudo]", pexpect.TIMEOUT])
                if install_expect == 0:
                    expect_install.sendline(host_pc_password_value)
                    display_line(host_text, expect_install.before)
                install_yes = expect_install.expect(["Do you want to continue", pexpect.TIMEOUT])
                if install_yes == 0:
                    expect_install.sendline('y')
                    display_line(host_text, expect_install.before)
                elif install_yes == 1:
                    pass
                else:
                    display_line(host_text, '*******************Install expect fail**********************')
            except pexpect.EOF , e:
                display_line(host_text, e)
                display_line(host_text, '*******************Install expect fail**********************')

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
    except OSError, e:
        display_line(display, e)
        f.write(e)

def display_line(display, line):
    display.grid(row=8, column=0, columnspan=10, rowspan=10, sticky=W+E+N+S)
    display.insert(INSERT, "%s\n" % line)
    display.see(END)
    display.update()


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
    global host_pc_password_value
    host_pc_password_value = host_pc_password.get()
    Thread_test = install_host_thread('./host_dependency.exp y %s'%(host_pc_password_value))
    Thread_test.start()


def node_install():
    global node_ip_value, node_password_value
    node_password_value = node_password_entry.get()
    node_user_value = node_entries[0].get()
    node_ip_value = node_entries[1].get()
    Thread_test = install_dependency_thread('TestNode', node_text, './TestNode_dependency.exp y %s %s %s %s'%(node_user_value, node_ip_value, node_password_value, os.environ['HOME']))
    Thread_test.start()


if __name__ == "__main__":
    master = Tk()
    var = IntVar()
    master.resizable(0, 0)
    screenwidth = master.winfo_screenwidth()
    screenheight = master.winfo_screenheight()
    master.geometry('%dx%d'%(screenwidth/3, screenheight/2))
    master.title('Caliper Install GUI')

    #create note book
    tabControl = ttk.Notebook(master)
    host_ui = ttk.Frame(tabControl)  # Add a second tab
    tabControl.add(host_ui, text='Install Host')  # Make second tab visible
    target_ui = ttk.Frame(tabControl)  # Create a tab
    tabControl.add(target_ui, text='Install target')  # Add the tab
    node_ui = ttk.Frame(tabControl)  # Add a third tab
    tabControl.add(node_ui, text='Install Node')  # Make second tab visible
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
        entry = Entry(target_ui, width=screenwidth/50)
        entry.grid(row=i, column=1, sticky=W)
        entries.append(entry)

    password_entry = Entry(target_ui, width=screenwidth/50, show = '*')
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

    #make host ui
    Label(host_ui, text="host pc password: ").grid(sticky=W)

    #weight layout
    # package_installation_choice.grid(row=0, column=1, sticky=W)
    host_pc_password = Entry(host_ui, width=screenwidth/50, show = '*')
    host_pc_password.grid(row=0, column=1, sticky=W)

    #Install button
    global host_install_button
    host_install_button = Button(host_ui, text='Install', command=host_install)
    host_install_button.grid(row=6, column=2)

    #View result button
    global host_view_button
    host_view_button = Button(host_ui, text='View result', command=result.host_result)
    host_view_button.grid(row=6, column=3)
    host_view_button.configure(state = DISABLED)

    # log button
    global host_log_button
    host_log_button = Button(host_ui, text='Log', command=result.open_host_log)
    host_log_button.grid(row=6, column=4)
    host_log_button.configure(state=DISABLED)

    #
    global host_text, target_text, node_text
    host_text = Text(host_ui, height=screenheight/35, wrap=WORD)
    target_text = Text(target_ui, height=screenheight/35, wrap=WORD)
    node_text = Text(node_ui, height=screenheight/35, wrap=WORD)

    #make node ui
    #weight layout
    Label(node_ui, text="TestNode user: ").grid(sticky=W)
    Label(node_ui, text="TestNode ip: ").grid(sticky=W)
    Label(node_ui, text="TestNode password: ").grid(sticky=W)

    #value weight
    node_entries = []
    # i value is:target_user, target_ip, target_password, disk_name
    for i in range(0,2):
        node_entry = Entry(node_ui, width=screenwidth/50)
        node_entry.grid(row=i, column=1, sticky=W)
        node_entries.append(node_entry)

    node_password_entry = Entry(node_ui, width=screenwidth/50, show = '*')
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

    #loop tk
    mainloop()


