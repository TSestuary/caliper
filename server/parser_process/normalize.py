import yaml
import json
import os
import glob
from caliper.server.shared import caliper_path
from caliper.server.shared.caliper_path import folder_ope as Folder


def normalise():
    dicList = []
    for filename in glob.glob(os.path.join(Folder.yaml_dir, '*_score_post.yaml')):
        dicList.append(yaml.load(open(filename)))
    normalize_files(dicList)
    return

def normalize_files(dicList):
    #generate ideal template
    dic_ideal = {}
    newDic = dicList[0]
    for top,category in newDic.iteritems():
        if top == 'results':
            for category,sub_category in category.iteritems():
                for sub_category,scenario in sub_category.iteritems():
                        dic = {}
                        value_Sub = []
                        value_Sub_Normalize = []
                        index = 0
                        for dic in dicList:
                            try:
                                value_Sub.append(dic[top][category][sub_category]['Total_Scores'])
                            except KeyError:
                                value_Sub.append(0)
                        for value in value_Sub:
                            if max(value_Sub) > 0:
                                if value > 0:
                                    value_Sub_Normalize.append(round(100*value/max(value_Sub),2))
                                else:
                                    value_Sub_Normalize.append(0)
                            else:
                                value_Sub_Normalize.append(0)

                        for dic in dicList:
                            try:
                                dic[top][category][sub_category]['Total_Scores'] = value_Sub_Normalize[index]
                                index+=1
                            except KeyError:
                                pass
                        for scenario,division in scenario.iteritems():
                            if scenario != "Total_Scores":
                                for division,key in division.iteritems():
                                    if division == "Total_Scores":
                                        dic = {}
                                        value_Sub_Normalize = []
                                        value_Sub = []
                                        index = 0
                                        for dic in dicList:
                                            try:
                                                value_Sub.append(dic[top][category][sub_category][scenario][division])
                                            except KeyError:
                                                value_Sub.append(0)
                                        for value in value_Sub:
                                            if max(value_Sub) > 0:
                                                if value > 0:
                                                    value_Sub_Normalize.append(round(100*value/max(value_Sub),2))
                                                else:
                                                    value_Sub_Normalize.append(0)
                                            else:
                                                value_Sub_Normalize.append(0)

                                        for dic in dicList:
                                            try:
                                                dic[top][category][sub_category][scenario][division] = value_Sub_Normalize[index]
                                                index+=1
                                            except KeyError:
                                                pass
                                    else:
                                        for key,value in key.iteritems():
                                            dic = {}
                                            value_Sub_Normalize = []
                                            value_Sub = []
                                            index = 0
                                            for dic in dicList:
                                                try:

                                                    value_Sub.append(dic[top][category][sub_category][scenario][division][key])
                                                except KeyError:
                                                    value_Sub.append(0)
                                            sub1_scenario = ''
                                            sub2_scenario = ''
                                            for value in value_Sub:
                                                if type(value) == dict:
                                                    sub1_scenario = value.keys()[0]
                                                    for va in value:
                                                        if type(value[va]) == dict:
                                                            sub2_scenario = value[va].keys()[0]
                                                            for v in value[va]:
                                                                sub_value = value[va][v]
                                                            max_list = value[va].values()
                                                        else:
                                                            max_list = value.values()
                                                            sub_value = value[va]
                                                else:
                                                    sub_value = value
                                                    max_list = value_Sub
                                                if max(max_list) > 0:
                                                    if sub_value > 0:
                                                        value_Sub_Normalize.append(round(100*sub_value/max(max_list),2))
                                                    else:
                                                        value_Sub_Normalize.append(0)
                                                else:
                                                    value_Sub_Normalize.append(0)

                                            for dic in dicList:
                                                try:
                                                    if sub2_scenario:
                                                        dic[top][category][sub_category][scenario][division][key][sub1_scenario][sub2_scenario] = value_Sub_Normalize[index]
                                                    elif sub1_scenario:
                                                        dic[top][category][sub_category][scenario][division][key][sub1_scenario] = \
                                                            value_Sub_Normalize[index]
                                                    else:
                                                        dic[top][category][sub_category][scenario][division][key] = value_Sub_Normalize[index]
                                                    index+=1
                                                except KeyError:
                                                   pass
    for dic in dicList:
            delete(dic, "normalise")
    save(dicList)


def delete(dic, option):
    try:
        del dic['results']['Functional']['peripheral']
    except:
        pass
    try:
            del dic['results']['Functional']['kernel']['EFIFS']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['posix']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['network']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['syscall']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['vm']
    except KeyError:
            pass
    if option == "normalise" :
        try:
                del dic['results']['Performance']['application']['hadoop']['Point_Scores']['HadoopSleep']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['cpu']['Point_Scores']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['memory']['Point_Scores']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['file/vm']['Point_Scores']['Page_fault']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['rttest']['Point_Scores']['pi-stress']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['application']['nginx_32_core_cross_wrps']['Point_Scores']['max_cpu_load']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['application']['nginx_32_core_local_wrps']['Point_Scores']['max_cpu_load']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['application']['nginx_64_core_wrps']['Point_Scores']['max_cpu_load']
        except KeyError:
                pass

    elif option == "report":
        try:
                del dic['results']['Performance']['application']['hadoop']['HadoopSleep']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['cpu']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['memory']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['file/vm']['Page fault']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['rttest']['pi-stress']
        except KeyError:
                pass

def save(dicList):
    for dic in dicList:
        try:
            dic['name']
        except:
            dic['name'] = caliper_path.platForm_name
        outputyaml = open(os.path.join(Folder.yaml_dir, dic['name'] + "_score_post.yaml"),'w')
        outputjson = open(os.path.join(Folder.yaml_dir , dic['name'] + "_score_post.json"),'w')
        outputyaml.write(yaml.dump(dic, default_flow_style=False))
        outputjson.write(json.dumps(dic,indent=0,sort_keys=True))
        outputyaml.close()
        outputjson.close()
