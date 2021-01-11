#coding = utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import getopt

inputFileName="input.csv"
outputFileName = "result.csv"
mpi_low =5
mpi_high=30
kick=30
ampi=30
ampiP =55

CsvData =pd.DataFrame ()
IsAway =False
def mikeRemoveDuplicated (name):
    global CsvData
    print ("mikeRemoveDuplicated ",name)
    data =CsvData.loc[CsvData['filename']==name]
    
    test=data.loc[data['Obj_size']!=data['Obj_size'].max()]
    CsvData['Drop'][test.index]=True

 
def dataPreProcessing():

    global CsvData

    body =""
    x1 =""
    y1 =""
    x2 =""
    y2 =""
    obj_size = ""
    obj_class=""
    count = 0
    ishead=True
    
    repeatNames =CsvData.loc[CsvData['IsRepeat']==True]['filename']

    for i in range (0,len (repeatNames)):
        
        mikeRemoveDuplicated (repeatNames.values[i])

    CsvData=CsvData.loc[CsvData['Drop']!=True]
    CsvData=CsvData.reset_index()
    t=CsvData.loc[CsvData['body_conf.'].isnull()]
    CsvData['N/A tag'][t.index]="N/A"
    
    for i in range (0,len( CsvData)):

        if (CsvData['N/A tag'][i]=='N/A'):
            count+=1
            CsvData['Obj_size'][i] =obj_size
            CsvData['body_conf.'][i]=body
            CsvData['x1'][i]=x1
            CsvData['x2'][i]=x2
            CsvData['y1'][i]=y1
            CsvData['y2'][i]=y2
            CsvData['class'][i]=obj_class
            if count >=90 and ishead==True:
                IsAway =True
                
                
                CsvData['MPI tag'][i] ="AWAY"
                body =""
                x1 =""
                y1 =""
                x2 =""
                y2 =""
                obj_size = ""
                obj_class="" 
        else:
            ishead =True
            
            obj_class=CsvData['class'][i]
            obj_size=CsvData['Obj_size'][i]
            body =CsvData['body_conf.'][i]
            x1 =CsvData['x1'][i]
            x2 =CsvData['x2'][i]
            y1 =CsvData['y1'][i]
            y2 =CsvData['y2'][i]

            if count >= 90:
                CsvData['Clean'][i]=1
            count=0
        print (i ," Finish")


def dataProcessing():


    global CsvData
    global ampiP
    ampiP =ampiP/100.0
    kickP =kick/100.0
    
    CsvData=CsvData.filter(['filename','class','body_conf.','x1','y1','x2','y2','Obj_size'])
    CsvData['Obj_size']=CsvData['Obj_size'].str.replace('%','').astype (float)
    CsvData['IsRepeat']=CsvData['filename'].duplicated()
    CsvData['Drop']=None
    CsvData['N/A tag']=None
    CsvData['MPI tag']=None
    CsvData['Area']=None
    
    CsvData['count']=None
    CsvData['MPI']=None
    CsvData['MLI']=None
    CsvData['IsATW']=0
    CsvData['IsATWT']=None
    CsvData['Clean']=0
    CsvData['ex']=None
    
    dataPreProcessing()

    CsvData['AWAY']=CsvData['MPI tag']
    
    CsvData.to_csv('testindex.csv')
    CsvData['x1'] = CsvData['x1'].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    CsvData['x2'] = CsvData['x2'].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    CsvData['y1'] = CsvData['y1'].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    CsvData['y2'] = CsvData['y2'].apply(pd.to_numeric, errors='coerce').fillna(0.0)

    CsvData['Area']=(CsvData['x2']-CsvData['x1']) *(CsvData['y2']-CsvData['y1'])

    CsvData['test']=CsvData['Area']-CsvData['Area'].shift(1)
    CsvData['MLI']=CsvData['test'].abs()/CsvData['Area'].shift(1)

    
    
    #CsvData.loc [extraCondition,'MLI']=CsvData['test'].abs()/CsvData['Area'].shift(1)
    
    
    
    CsvData['if >10%']=CsvData['MLI'] >0.10
    CsvData['if >10%']=CsvData['if >10%'].astype(int)
    CsvData['MPI']=CsvData['MPI'].astype(float)
    CsvData['MPI'] =CsvData['if >10%'].rolling(window = 90).sum().shift()/90.0
    
        
    CsvData.loc[CsvData['MPI']<mpi_low/100.0,'MPI tag']="Asleep"
    CsvData.loc[ (CsvData['MPI']>=mpi_low/100.0) & (CsvData['MPI']<=mpi_high/100.0) ,'MPI tag']="Move Around"
    CsvData.loc[CsvData['MPI']>mpi_high/100.0,'MPI tag']="About to wake"
    CsvData.loc[CsvData['MPI']>mpi_high/100.0,'IsATW']=1
    CsvData['AWAY']=CsvData['AWAY'].astype (str)
    CsvData.loc[CsvData['AWAY']=="AWAY",'MPI tag']="AWAY"

    CsvData['Summary']=CsvData['MPI tag']
    CsvData['AMPI tag']="about to awake"
    CsvData['IsATWT']=CsvData['IsATWT'].astype(float)
    CsvData['IsATW']=CsvData['IsATW'].astype(int)
    CsvData['IsATWT']=CsvData['IsATW'].rolling(window = 90).sum().shift()/90.0
    CsvData['MLI tag']=None
    CsvData['IsAway']=0
    CsvData['IsAway']=CsvData['IsAway'].astype(int)
    CsvData['IsAway']=CsvData['Clean'].rolling(window = 90).sum().shift()
    CsvData.loc [CsvData['IsAway']!= 0, 'MPI']=None
    CsvData.loc [CsvData['IsAway']!= 0, 'AMPI tag']=None
    CsvData.loc [CsvData['IsAway']!= 0, 'MLI tag']=None
    
    CsvData.loc [CsvData['IsATWT'] >ampiP,'AMPI tag']="awake"
    CsvData.loc [(CsvData['IsATWT'] >ampiP) & (CsvData['MPI tag']=='About to wake'),'Summary']="awake"
    
    CsvData.loc [CsvData['IsAway']!= 0, 'Summary']=None
    
    CsvData.loc [CsvData['MLI'] >kickP,'MLI tag']="Kick"
    CsvData.loc [CsvData['IsAway']!= 0, 'MLI tag']=None
        
        
    CsvData.loc[CsvData['body_conf.']=="",'x1']=None
    CsvData.loc[CsvData['body_conf.']=="",'y1']=None
    CsvData.loc[CsvData['body_conf.']=="",'y2']=None
    CsvData.loc[CsvData['body_conf.']=="",'x2']=None
    CsvData.loc[CsvData['body_conf.']=="",'Area']=None
    CsvData['MPI'][0:90]=None
    CsvData['if >10%'][0:90]=None
    CsvData['MPI tag'][0:90]=None
    CsvData['AMPI tag'][0:90]=None
    CsvData['AMPI']=CsvData['IsATWT']

    
    extraCondition =(CsvData['MPI tag'].shift(1)=='AWAY')&(CsvData['MPI tag']!="AWAY")
    CsvData.loc[extraCondition,'ex']=-1
    
    extraCondition=CsvData['ex']==-1
    CsvData.loc[extraCondition,'MLI']=None
    CsvData.loc[extraCondition,'Summary']=None
    CsvData.loc[extraCondition,'AMPI tag']=None
    CsvData.loc[extraCondition,'MLI tag']=None
    

    
    extraCondition =(CsvData['MPI tag'].shift(2)!='AWAY')&(CsvData['MPI tag']=="AWAY")&(CsvData['MPI tag'].shift(1)=='AWAY')
    CsvData.loc[extraCondition,'ex']=-2
    extraCondition =CsvData['ex']==-2
    CsvData.loc[extraCondition,'MLI']=None
    CsvData.loc[extraCondition,'MLI tag']=None

    CsvData.loc[CsvData['N/A tag'].shift(1)=='N/A',CsvData['MLI tag']]=None
    

    

    
    d ={"MPI tag": CsvData['Summary'],"MLI tag":CsvData['MLI tag']}
    df = pd.DataFrame(data=d)
    CsvData=CsvData.drop(['IsATWT','IsAway','ex','Clean','IsRepeat','Drop','index','test','IsATW','AWAY'],axis=1)
    CsvData.to_csv(outputFileName)
    df.to_csv('tagData.csv')


def SystemArguments ():
    global inputFileName
    global outputFileName
    global mpi_low
    global mpi_high
    global kick
    global ampi
    global ampiP
    
    argv =sys.argv[1:]
    try:
        opts,args =getopt.getopt(argv,"hi:o:m",['help','input','output','mpi_low','mpg_high','kick_threshold','ampi_threshold'])
    except getopt.GetoptError:
        return

    for opt,arg in opts:
        
        if opt in ("-h",'--help'):
            
            print('-----------------------------------------------------------------')
            print('Help: ')
            print("This application make from Mike_Lu")
            print('-i --input <input file>   default = input.csv')
            print('-o --output <output file>  default = result.csv')
            print('-ml --mpi_low <mpi_low> default = 5')
            print('-mh --mpi_high <mpi_high> default = 30')
            print('-k --kick  default = 30' )
            print('-a --ampi  default = 30' )
            print('-ap --ampip  default = 50' )
            
            print('-----------------------------------------------------------------')
            sys.exit()
            
        elif opt in ('-i','--input'):
            inputFileName =arg
            
        elif opt in ('-o','--ouput'):
            outputFileName =arg
            
        elif opt in ('-ml','--mpi_low'):
            mpi_low =arg
            
        elif opt in ('-mh','--mpi_high'):
            mpi_high =arg
            
        elif opt in ('-k ','--kick'):
            kick=arg
            
        elif opt in ('-a','--ampi'):
            ampi=arg
            
        elif opt in ('-ap', '--ampip'):
            ampiP =arg
            
                    
if __name__=='__main__':
    SystemArguments()
    CsvData =pd.read_csv (inputFileName)
    dataProcessing()
