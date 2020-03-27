import sys
import pika
import pymqi
from datetime import datetime,date
import datetime as d
import pyodbc
import requests
import time
import os
import re


#CONFIGURAÇÕES DO ROBÔ
#Caminho para salvar os logs
path= ''

def check_wmq():
    queue_manager = ''
    channel = ''
    host = ''
    port = ''
    queue_name = ''
    conn_info = '%s(%s)' % (host, port)
    user = ''
    password = '@@'

    #pega hora da conexão
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    try:
        #faz a conexão com a fila
        qmgr = pymqi.connect(queue_manager, channel, conn_info,user,password)
        queue = pymqi.Queue(qmgr, queue_name)
        qmgr.disconnect()

        arq = open(path+'log_check_wmq_cal_sendlistedequitytocal_inp.csv','a')
        arq.write('%s;%s;conectado;status ok;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1)))
        arq.close
    except Exception as erro:
        arq = open(path+'log_check_wmq_cal_sendlistedequitytocal_inp.csv','a')
        arq.write('%s;%s;erro;%s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),erro))
        arq.close

def check_rabbit_mq():
    host_name = ''
    port_number=''
    user=''
    password =''
    queue_name = ''
    
    #pega hora da conexão
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    try:
        #conexão com host internal-edm-dev-1944263457.sa-east-1.elb.amazonaws.com
        pika_conn_params = pika.ConnectionParameters(host=host_name, port=port_number,credentials=pika.credentials.PlainCredentials(user, password),)
        connection = pika.BlockingConnection(pika_conn_params)
        channel = connection.channel()
        queue = channel.queue_declare(queue=queue_name)

        arq = open(path+'check_rabbit_mq_manual_taxbatch_queue.csv','a')
        arq.write('%s;%s;conectado;numero de mensagens na fila: %s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),queue.method.message_count))
        arq.close
    except Exception as erro:
        arq = open(path+'check_rabbit_mq_manual_taxbatch_queue.csv','a')
        arq.write('%s;%s;erro;%s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),erro))
        arq.close

def check_conexao_sqlserver():
    server = ''
    database = ''
    username = ''
    password = ''
    driver= '{SQL Server Native Client 11.0}'
    
    #pega hora da conexão
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    try:
        #conexão com o banco de dados
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cnxn.close()
        arq = open(path+'check_conexao_sqlserver.csv','a')
        arq.write('%s;%s;conectado;status ok;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1)))
        arq.close
    except Exception as erro:
        arq = open(path+'check_conexao_sqlserver.csv','a')
        arq.write('%s;%s;erro;%s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),erro))
        arq.close
    

def check_requisicao_https():
    url=''
    #pega hora da conexão
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    #faz a requisição
    try:
        r = requests.get(url)
        if(r.status_code==200):
            arq = open(path+'check_requisicao_https.csv','a')
            arq.write('%s;%s;conectado;%s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),r.status_code))
            arq.close
        else:
            arq = open(path+'check_requisicao_https.csv','a')
            arq.write('%s;%s;erro;%s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),r.status_codes))
        
            arq.close
    except Exception as erro:
            arq = open(path+'check_requisicao_https.csv','a')
            arq.write('%s;%s;erro;%s;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),erro))
            arq.close

def check_arquivo_local():
    listaFolder=()
   
    #pega hora da conexão
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    yesterday= date.today() - d.timedelta(days=1)
    ontem_formatado=yesterday.strftime("%Y%m%d")
    lista_arquivos = {}
    num_arquivos=0
    for folder in listaFolder:
        try:
            path_local = r'\\dddddd\dddddddd\%s\dddddddd\%s'%(folder,ontem_formatado)

            arquivos = os.listdir(path_local)
            for file_txt in arquivos:
                num_arquivos +=1
        except Exception as erro:
            print(erro)
            continue 
    print('numero de arquivos encontrados: %s'%num_arquivos)
    
    if(num_arquivos>0):
        arq = open(path+'check_arquivos_local.csv','a')
        arq.write('%s;%s;encontrado;%s arquivos;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),num_arquivos))
        arq.close
    else:
        arq = open(path+'check_arquivos_local.csv','a')
        arq.write('%s;%s;erro;%s arquivos;\n'% (re.match("(\d+).(\d+)",str(timestamp)).group(1),re.match("([\d\-\s:]+).(\d+)",str(now)).group(1),num_arquivos))
        arq.close

#INÍCIO DO ROBÔ
#aqui pega o parâmetro que é passado por linha de comando           
arg = sys.argv[1]

if(arg == 'wmq'):
    check_wmq()
    print('check-wmq')

elif(arg == 'rabbit'):
    check_rabbit_mq()
    print('rabbit')

elif(arg == 'sqlserver'):
    check_conexao_sqlserver()
    print('sqlserver')

elif(arg == 'https'):
    check_requisicao_https()
    print('https')

elif(arg == 'local'):
    check_arquivo_local()
    print('local')

else:
    print('nenhum argumento foi passado')



