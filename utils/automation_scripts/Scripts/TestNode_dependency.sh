#!/bin/bash

TestNode_dependency="TestNode_dependency_dir"

architecture_x86_64=`uname -a | grep -c "x86_64"`
architecture_arm64=`uname -a | grep -c "aarch64"`

Osname_Ubuntu=`cat /etc/*release | grep -c "Ubuntu"`
Osname_Centos=`cat /etc/*release | grep -c "CentOS"`

if [ ! -d $TestNode_dependency ]
then
    sudo mkdir -p $TestNode_dependency
fi
cd $TestNode_dependency

file_present=TestNode_dependency_output_summary.txt
if [ -f $file_present ]
then
    sudo rm TestNode_dependency_output_summary.txt
fi

logpath="$HOME/$TestNode_dependency/$file_present"
ERROR="ERROR-IN-AUTOMATION"
dependency=('qperf' 'netperf' 'iperf3')
UPDATE=0
flag=(1 1 1)
clear
echo "TestNode"
echo -e "\n\t\tTestNode Dependency"
for i in `seq 0 $((${#dependency[@]}-1))`
do
    check=`sudo find /usr -name ${dependency[$i]} | grep -c ${dependency[$i]}`
        if [ $check -ne 0 ];then
            if [ ${dependency[$i]} == 'netperf' ];then
                check_version=`netperf -V | grep -c "2.7.0"`
                if [ $check_version -eq 0 ];then
                    echo "please install netperf 2.7.0 version" >> $logpath
                else
                    echo -e "\n${dependency[$i]} is already installed" >> $logpath
                fi
            elif [ ${dependency[$i]} == 'iperf3' ];then
                check_version=`iperf3 --version | grep -c "3.1.4"`
                if [ $check_version -eq 0 ];then
                    echo -e "please install iperf3 3.1.4 version" >> $logpath
                else
                    echo -e "\n${dependency[$i]} is already installed" >> $logpath
                fi
            elif [ ${dependency[$i]} == 'qperf' ];then
                check_version=`qperf -V | grep -c "0.4.9"`
                if [ $check_version -eq 0 ];then
                    echo "please install qperf 0.4.9 version" >> $logpath
                else
                    echo -e "\n${dependency[$i]} is already installed" >> $logpath
                fi
            fi
        else
            # if force option is passed thn forcefully run the scripts
            if [ $1 = "y" ];then
                choice="y"
            else
                echo "${dependency[$i]} is not installed, would you like to install(y/n)" >> $logpath
            fi
            if [ $choice == 'y' ];then
                if [ ${dependency[$i]} == qperf ];then
                    wget https://www.openfabrics.org/downloads/qperf/qperf-0.4.9.tar.gz 2>/dev/null
                    if [ $? -eq 0 ];then
                        tar xvf qperf-0.4.9.tar.gz
                        cd qperf-0.4.9
                        if [ $architecture_x86_64 -eq 1 ];then
                            ./configure --build=x86_64-unknown-linux-gnu
                        elif [ $architecture_arm64 -eq 1 ];then
                            ./configure --build=aarch64-unknown-linux-gnu
                        fi
                        sudo make && sudo make install
                        cd ..
                        qperfcheck=`sudo find /usr -name qperf | grep -c qperf`
                        if [ $qperfcheck -ne 0 ];then
                            echo "qperf is installed" >> $logpath
                        else
                            echo -e "\n$ERROR :qperf is not installed" >> $logpath
                        fi
                    else
                        echo -e "\n$ERROR :download qperf fail" >> $logpath
                    fi
                elif [ ${dependency[$i]} == 'netperf' ];then
                    wget ftp://ftp.netperf.org/netperf/netperf-2.7.0.tar.gz 2 >/dev/null
                    if [ $? -eq 0 ];then
                        tar xf netperf-2.7.0.tar.gz
                        cd netperf-2.7.0
                        if [ $architecture_x86_64 -eq 1 ];then
                            ./configure --build=x86_64-unknown-linux-gnu
                        elif [ $architecture_arm64 -eq 1 ];then
                            ./configure --build=aarch64-unknown-linux-gnu
                        fi
                        sudo make && sudo make install
                        sudo netserver
                        cd ..
                        netperfcheck=`sudo find /usr -name netperf | grep -c netperf`
                        if [ $netperfcheck -ne 0 ];then
                            echo "netperf is installed" >> $logpath
                        else
                            echo -e "\n$ERROR :netperf install " >> $logpath
                        fi
                    else
                        echo -e "\n$ERROR :download netperf fail" >> $logpath
                    fi

                else
                    wget https://github.com/esnet/iperf/archive/3.1.4.zip 2 >/dev/null
                    if [ $? -eq 0 ];then
                        unzip 3.1.4.zip
                        cd iperf-3.1.4
                        ./configure
                        make
                        sudo make install
                        cd ..
                        iperf3check=`sudo find /usr -name iperf3 | grep -c iperf3`
                        if [ $iperf3check -ne 0 ];then
                            echo "iperf3 is installed" >> $logpath
                        else
                            echo "$ERROR:iperf3 is not installed" >> $logpath
                        fi
                    else
                        echo -e "\n$ERROR :download iperf 3.1.4.zip fail" >> $logpath
                    fi

                fi
            fi
        fi
done

if [ ! -f ~/caliper_redis/redis_benchmark ];then
    wget http://www.estuarydev.org/caliper/redis-3.2.4.tar.gz
    tar xvf redis-3.2.4.tar.gz
    cd redis-3.2.4/src
    make all
    mkdir ~/caliper_redis
    cp redis-benchmark redis-cli ~/caliper_redis/
fi

for i in `seq 0 $((${#flag[@]}-1)) ` 
do    
    j=${flag[$i]}
    if [ $j -eq 1 -a $i -eq 0 ];then
        if  ! ps -ef | grep "netserver" | grep -v grep ;then 
            echo -e "\n\t\tnetperf service not running"
            sudo netserver
            wait
            echo "\n\t\tdone restarting netperf"
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Netperf please try again" >> $logpath
                exit 1
            fi
        fi
    elif [ $j -eq 1 -a $i -eq 1 ];then
        if  ! ps -ef | grep "iperf3" | grep -v grep  ;then 
            iperf3 -s &
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Iperf please try again" >> $logpath
                exit 1
            fi
        fi
    elif [ $j -eq 1 -a $i -eq 2 ];then
        if  ! ps -ef | grep "qperf" | grep -v grep  ;then 
            qperf &
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Qperf please try again" >> $logpath
                exit 1
            fi
        fi
   fi         
done
