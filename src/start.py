# Author : Princu Jain
# IIIT Hyderabad
# Orchestration Layer phase-1

from flask import Flask , request ,jsonify, session , url_for , redirect
import os,sys
import json
import libvirt

app = Flask(__name__)

##########################        GLOBAL VARIABLES        ############################


full_vm_img = {}
pm_ips = {}
pm_final = ""
mark=0
vm_ids = []
vm = {}
vms ={}
check = {}


##########################            VM API's                 #############################



@app.route('/vm/create', methods=['GET'])
def VM_Creation():
    """     VM  Creation    """
    argument = request.args
    vm_name = str(argument['name'])
    vm_type_id = int(argument.get('instance_type'))
    vm_image_id = int(argument.get('image_id'))
    vm_details = getVmType(vm_type_id)
    vm_cpu = vm_details['cpu']
    vm_ram = vm_details['ram']
    vm_disk = vm_details['disk']

    vm_image_path = full_vm_img[vm_image_id]
    pm_final = Schedule(vm_cpu,vm_ram,vm_disk)
    setup(vm_image_path,pm_final)
    global vm_ids
    if len(vm_ids)==0:
        i = 1
    else:
        i = int(vm_ids[-1])+1
    global vm
    vm_ids.append(i)
    vm[i] = {}
    vm[i]['name']  = vm_name
    vm[i]['finalip'] = pm_final
    global check
    global vms
    for pmid, ip  in pm_ips.iteritems():
	if ip == pm_final:
            vm[i]['pmid'] = pmid
            if pmid in check:
                vms[pmid].append(i)
            else:
                vms[pmid] =[]
                vms[pmid].append(i)
                check[pmid] = 1
                vm[i]['pmid'] = pmid
    vm[i]['instance'] = vm_type_id

    xml = """<domain type='qemu' id='%d'>
    <name>%s</name>
    <memory unit='MiB'>%d</memory>
    <vcpu placement='static'>%d</vcpu>
    <os>
    <type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type>
    </os>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>restart</on_crash>
    <devices>
    <disk type='file' device='cdrom'>
    <source file='%s'/>
    <target dev='hdc' bus='ide'/>
    </disk>
    </devices>
    </domain>""" % ( 100 , vm_name, vm_ram, vm_cpu, "/home/pjain" +  '/' + vm_image_path.split('/')[-1])
    try:
        conn = libvirt.open("qemu+ssh://"+ vm[i]['finalip'] + "/system")
        conn.defineXML(xml)
        dom = conn.lookupByName(vm_name)
        dom.create()
        conn.close()
        return jsonify(status=i)
    except:
        conn.close()
        return jsonify(status=-1)


@app.route('/vm/types', methods=['GET'])
def VM_Type():
     f = open(sys.argv[3], "r")
     l = f.read()
     return l



@app.route('/vm/destroy', methods=['GET'])
def VM_Destroy():
    argument = request.args
    vmid = int(argument['vmid'])
    connection = libvirt.open( "qemu+ssh://" + vm[vmid]['finalip'] + "/system" )
    vm_present = connection.lookupByName(vm[vmid]['name'])
    try:
        vm_present.destroy()
        connection.close()
        return jsonify(status = 1)
    except:
        connection.close()
        return jsonify(status = 0)



@app.route('/vm/query',methods=['GET'])
def VM_Query():
    argument = request.args
    vmid = int(argument['vmid'])
    if vmid > len(vm):
        return jsonify(status = 0)
    name = vm[vmid]['name']
    pmid = vm[vmid]['pmid']
    instance = vm[vmid]['instance']
    return jsonify(vmid = vmid, name = name, instace_type = instance,pmid=pmid)



############################            IMAGE SERVICE API's            ############################



@app.route('/image/list', methods=['GET'])
def List_Images():

    """     LIST OF IMAGES    """
    d = {"images":[{"id":key,"name":value.split('/')[-1]} for key,value in full_vm_img.items()]}
    json_string = json.dumps(d)
    return json_string



############################            RESOURCE SERVICE API's           ############################



@app.route('/pm/query/', methods=['GET'])
def PM_Query():
    """   capacity and free storage     """
    argument = request.args
    pmid = int(argument['pmid'])
    if pmid > len(pm_ips):
        return -1 ##### ERROR
    pmip = pm_ips[pmid]
    os.system("ssh " + pmip +" grep processor /proc/cpuinfo | wc -l >> file")
    os.system("ssh " + pmip + " free -k | grep 'Mem:' | awk '{ print $4 }' >> file")
    os.system("ssh " + pmip +" df -k | grep 1 | awk '{ print $4}' | head -2 | tail -1 >> file")
    f = open("file", "r")
    pm_free={}
    pm_free['cpu'] = f.readline().strip("\n")
    pm_free['ram'] = f.readline().strip("\n")
    pm_free['disk'] = f.readline().strip("\n")
    os.system("rm -rf file")
    os.system("ssh " + pmip +" grep processor /proc/cpuinfo | wc -l >> file")
    os.system("ssh " + pmip + " free -k | grep 'Mem:' | awk '{ print $2 }' >> file")
    os.system("ssh " + pmip +" df -k | grep 1 | awk '{ print $2}' | head -2 | tail -1 >> file")
    f = open("file", "r")
    pm_capacity={}
    pm_total['cpu'] = f.readline().strip("\n")
    pm_total['ram'] = f.readline().strip("\n")
    pm_total['disk'] = f.readline().strip("\n")
    os.system("rm -rf file")
    tvms = vms[pmip]
    return jsonify(pmid = pmid, capacity = pm_capacity , free = pm_free ,vms = tvms)




@app.route('/pm/listvms', methods=['POST','GET'])
def List_VMs():
    argument = request.args
    pmid = int(argument['pmid'])
    return jsonify(vmids = vms[pmid])


@app.route('/pm/listpms', methods=['POST','GET'])
def List_PMs():
    d = {"vmids":[{key} for key in full_vm_img.items()]}
    json_string = json.dumps(d)
    return json_string


###########################            SUPPORTING FUNCTIONS           #############################


def getVmType(tid=None):
    f = open('flavor_file', "r")
    data = json.loads(f.read())[u'types']
    if tid!=None:
        for i in data:
            if i[u'tid'] == tid:
                return i
    else:
        return data
    return 0



def Schedule(cpu, ram, disk):
        """  selection of Physical Machine """
        global mark
        global pm_ips

        l=0
        pm_ips_len = len(pm_ips)
        for ips in range(len(pm_ips)):
            l = l+1;
            if l == pm_ips_len+1:
                return  -1      ###ERRROR here
            if ips == mark:
                mark = (ips + 1)%pm_ips_len
                os.system("ssh " + pm_ips[ips+1] +" free -k | grep 'Mem:' | awk '{ print $4 }' >> file")
                os.system("ssh " + pm_ips[ips+1] +" grep processor /proc/cpuinfo | wc -l >> file")
                f = open("file", "r")
                pm_ram = f.readline().strip("\n")
                pm_cpu = f.readline().strip("\n")
                os.system("rm -rf file")
                if int(pm_ram) >= int(ram):
                    if int(pm_cpu) >= int(cpu):
                        return pm_ips[ips+1]
                if ips == pm_ips_len-1:
                    ips = 0


def setup(vm_image_path , ip):
    vm_image_path = vm_image_path.strip("\r")
    if ip == vm_image_path.split(":")[0]:
        return
    os.system("ssh " + ip + " rm /home/" + ip.split("@")[0] + "/" + vm_image_path.split("/")[-1])
    com = "scp " + vm_image_path + " " + ip + ":/home/" + ip.split("@")[0] + "/"
    os.system(com)


#############################          MAIN FUNCTION            #############################



if __name__ == '__main__':
    global full_vm_img
    global pm_ips
    f = open(sys.argv[2], "r")
    machPath = []
    for i in f.readlines():
        i = i.strip("\r")
        machPath.append(i.strip("\n"))
        j=1
        for image in machPath:
            full_vm_img[j] = image
            j=j+1
    f = open(sys.argv[1], "r")
    ips = []
    for i in f.readlines():
        i = i.strip("\n")
        machPath.append(i.strip("\n"))
        ips.append(i.strip("\r"))
        j=1
        for ip in ips:
            pm_ips[j] = ip
            j = j+1
    app.run()
