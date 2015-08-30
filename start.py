from flask import Flask , request , session , url_for , redirect
import os,sys
import json
import libvirt

app = Flask(__name__)

##########################            GLOBAL VARIABLES        ############################


full_vm_img = {}
pm_ips = {}
pm_final = ""
mark=0

##########################            VM API's                 #############################




@app.route('/vm/create', methods=['GET'])   #complete
def VM_Creation():
    """     VM  Creation    """
    argument = requests.args
    vm_name = str(argument['name'])
    vm_type_id = int(argument['instance_type'])
    Vm_image_id = int(args['image_id'])
    vm_details = getVmType(vm_type_id)

    vm_cpu = vm_details['cpu']
    vm_ram = vm_details['ram']
    vm_disk = vm_details['disk']

    vm_image_path = full_vm_img[vm_image_id]
    pm_final = schedule(vm_cpu,vm_ram,vm_disk)

    setup(vm_image_path,pm_final)


@app.route('/vm/types', methods['GET'])
def VM_Type():
     f = open(sys.argv[3], "r")
     l = f.read()
     return l

@app.route('/vm/destroy', methods['GET'])  #complete
def VM_Destroy():
    argument = requests.args
    vmid = int(argument['vmid'])


@app.route('vm/query',methods['GET'])   #complete
def VM_Query():
    argument = requests.args
    vmid = int(argument['vmid'])


############################            IMAGE SERVICE API's            ############################



@app.route('/image/list', methods=['GET'])
def List_Images():

    """     LIST OF IMAGES    """
    d = {"images":[{"id":key,"name":value.split('/')[-1]} for key,value in full_vm_image.items()]}
    json_string = json.dumps(d)
    return json_string



############################            RESOURCE SERVICE API's           ############################



@app.route('/pm/query/', methods=['POST','GET'])   #complete
def PM_Query():
    """   capacity and free storage     """
    return json_string


@app.route('/pm/listvms', methods=['POST','GET'])
def List_VMs():
    d = {"vmids":[{key} for key in full_vm_image.items()]}
    json_string = json.dumps(d)
    return json_string


@app.route('/pm/listvms', methods=['POST','GET'])   #complete
def List_PMs():
    return json_string



###########################            SUPPORTING FUNCTIONS           #############################




def getVMType(tid=None):
    f = open(VM_TYPES, "r")
    data = json.loads(f.read())[u'types']
    if tid!=None:
        for i in data:
            if i[u'tid'] == tid:
                return i
    else:
        return data        ### Correct This
    return 0



def Schedule(cpu, ram, disk):   # improve schedule function
        """  selection of Physical Machine """
        pm_ips_len = len(pm_ips)
        for ips in range(len(pm_ips)):
            if ips == mark:
                mark = (pms + 1)%pm_ips_len
                os.system("ssh " + pm_ips[ips] +"free -k | grep 'Mem:' | awk '{ print $4 }' >> file")
                os.system("ssh " + pm_ips[ips] +"grep processor /proc/cpuinfo | wc -l >> file")
                f = open("file", "r")
                pm_ram = f.readline().strip("\n")
                pm_cpu = f.readline().strip("\n")
                os.system("rm -rf file")
                if int(pm_ram) >= int(ram):
                    if int(pm_cpu) >= int(cpu):
                        return pm_ips[ips]
                if ips == pm_ips_len-1:
                    ips = 0


def setup(vm_image_path , ip):
    vm_image_path = vm_image_path.strip("\r")
    if ip == vm_image_path.split(":")[0]:
        return
    os.system("ssh " + ip + " rm /home/" + ip.split("@")[0] + "/" + vm_image_path.split("/")[-1])
    os.system("scp " + vm_image_path + " " + ip + ":/home/" + ip.split("@")[0] + "/")


#############################          MAIN FUNCTION            #############################



if __name__ == '__main__':
    f = open(sys.argv[2], "r")
    machPath = []
    for i in f.readlines():
        i = i.strip("\r")
        machPath.append(i.strip("\n"))
        j=1
        for image in machPath:
            full_vm_image[j] = image
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
