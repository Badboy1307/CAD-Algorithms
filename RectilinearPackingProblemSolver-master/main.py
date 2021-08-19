# here put the import lib
from setting import settings
from nest import Nester
from nest import find_fitness
from tools.calculate_npf import NFP_Calculater
from tools import input_utls
import os
import sys
import time
import math
import argparse
import subprocess
import re

# MPI
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def master(data):



    Args:
        data (str): 

    if settings.DEBUG:
        import time
        start_time = time.time()
    from nest import content_loop_rate

    n = Nester()
    global nWorker
    n.nWorker=nWorker

    file_path,file_name=os.path.split(data)
    if settings.LINUXOS:
        file_path="/home/eda20303/project/verify_results"
    file_id=re.findall("\d+",file_name)[0]

    #s = input_utls.input_polygon('tools/f6.dxf')
    shapes,shapes_str=input_utls.load_input_file(data)
    n.add_objects(shapes,shapes_str)
    nshapes=len(shapes)
    if settings.USE_FORMULA:
        if nshapes<10:
            settings.SQRT_LENTH_SCALE=1.1102
        elif nshapes>900:
            settings.SQRT_LENTH_SCALE=1.0645
        else:
            settings.SQRT_LENTH_SCALE=(-8.2175e-11)*(nshapes**3)+(1.9941e-07)*(nshapes**2)-(1.6552e-04)*nshapes+1.1118
            #settings.SQRT_LENTH_SCALE=(nshapes^3)*(-6.6730e-11)+(nshapes^2)*(2.0656e-07)+nshapes*(-2.0632e-04)+1.1292;
    if nshapes<=90:
        settings.STOP_GENERATION=10
    else:
        settings.STOP_GENERATION=1
        
    
    sqrt_lenth=math.sqrt(n.shapes_total_area)

    bin_width=sqrt_lenth*settings.SQRT_LENTH_SCALE
    
    if bin_width>300*settings.SCALE:
        bin_width=300*settings.SCALE
    
    settings.BIN_NORMAL[1][1] = bin_width   
    settings.BIN_NORMAL[2][1] = bin_width    

    settings.BIN_NORMAL[2][0] = int(sqrt_lenth*settings.SQRT_LENTH_SCALE2)   
    settings.BIN_NORMAL[3][0] = int(sqrt_lenth*settings.SQRT_LENTH_SCALE2)
    
    print(settings.BIN_NORMAL)
    
    n.add_container(settings.BIN_NORMAL)

   
    n.run()

    best = n.best

    
    content_loop_rate(best, n,file_path=file_path,file_id=file_id, loop_time=settings.STOP_GENERATION,height=settings.BIN_NORMAL[1][1]) 
    stopAllWorkers()

    if settings.DEBUG:
        end_time = time.time()
        print("run time:",end_time-start_time)

def batchMpiEval(nWorker,pop):


    Args:
        nWorker (int):
        pop (type)

    Returns:
        [int]: fitness
    
    nSlave = nWorker-1
    nJobs = len(pop)
    nBatch= math.ceil(nJobs/nSlave) 
    reward =[]
    i = 0 
    for iBatch in range(nBatch):
        for iWork in range(nSlave): 
            if i < nJobs:
                signal_type = i 
                message   = pop[i] 
                comm.send(signal_type, dest=(iWork)+1, tag=1)
                comm.send(  message, dest=(iWork)+1, tag=2) 
            else: 
                signal_type = -1 
                comm.send(signal_type,  dest=(iWork)+1) 
            i = i+1 
        i -= nSlave
        for iWork in range(1,nSlave+1):
            if i < nJobs:
                workResult =comm.recv(source=iWork,tag=0) #TODO:complete 
                reward.append(workResult)
            i+=1
    return reward

def batchNFPCalculate(nWorker,nfp_pairs):
   

    Args:
        nWorker (int):
        nfp_pairs (dict): 

    Returns:
        list:

    nSlave = nWorker-1
    nJobs = len(nfp_pairs)
    nBatch= math.ceil(nJobs/nSlave) 

    pair_list =[]
    i = 0
    for iBatch in range(nBatch):
        for iWork in range(nSlave):
            if i < nJobs:
                signal_type = -3 
                message   = nfp_pairs[i]  
                comm.send(signal_type, dest=(iWork)+1, tag=1)
                comm.send(  message, dest=(iWork)+1, tag=2) 
          
            i = i+1 
        i -= nSlave
        for iWork in range(1,nSlave+1):
            if i < nJobs:
                workResult =comm.recv(source=iWork,tag=0) 
                pair_list.append(workResult)
            i+=1
    return pair_list

def batchSendContainerAndNFPCache(nWorker,origin_container,nfp_cache):
    
    Args:
        nWorker (int):
        origin_container (dict): 
        nfp_cache (dict): 
   nSlave = nWorker-1
    nJobs = nSlave
    nBatch= math.ceil(nJobs/nSlave) 

    pair_list =[]
    i = 0 
    for iBatch in range(nBatch): 
        for iWork in range(nSlave):
            if i < nJobs:
                signal_type = -4 
                message1 = origin_container  
                message2 = nfp_cache
                comm.send(signal_type, dest=(iWork)+1, tag=1) 
                comm.send(  message1, dest=(iWork)+1, tag=2) 
                comm.send(  message2, dest=(iWork)+1, tag=3)
            i = i+1 

def slave():
    origin_container=None
    nfp_cache=None
    while True:
        signal_type = comm.recv(source=0,
                           tag=1)  
        if signal_type >= 0: 
            message =comm.recv(source=0, tag=2) 
            result = find_fitness(message,origin_container,nfp_cache)  
            #print("rank:",rank,len(nfp_cache))
            comm.send(result, dest=0,tag=0)
        elif signal_type==-3:
            pair =comm.recv(source=0, tag=2)
            result=NFP_Calculater.process_nfp(pair)
            comm.send(result, dest=0,tag=0) 
            
        elif signal_type==-4:
            origin_container=comm.recv(source=0, tag=2)
            nfp_cache=comm.recv(source=0,tag=3)
        if signal_type ==-1:  
            
            break

def stopAllWorkers():
    
    global nWorker
    nSlave = nWorker - 1
   
    for iWork in range(nSlave):
        comm.send(-1, dest=(iWork) + 1, tag=1)

def mpi_fork(n):
   
    Args:
        n (int): 

    Returns:
        str: 
    if n <= 1:  
        return "child"
    if os.getenv("IN_MPI") is None:  
        env = os.environ.copy()
        env.update(MKL_NUM_THREADS="1", OMP_NUM_THREADS="1", IN_MPI="1") 
       
        if settings.LINUXOS:
            mpicmd="mpirun" 
            shellcmd=False
        else:
            mpicmd="mpiexec"
            shellcmd=True
        subprocess.check_call(
            [mpicmd, "-np", str(n), sys.executable] + ['-u'] + sys.argv,
            env=env,
            shell=shellcmd
        ) 
       return "parent"
    else:
        global nWorker, rank
        nWorker = comm.Get_size()  
        rank = comm.Get_rank() 
        #print(nWorker,rank)
        return "child"

def main(argv):
   
    Args:
        argv (dict): 
    
    if (rank == 0):
        master(argv.data)
    else:
        slave()

def run():
    
    parser = argparse.ArgumentParser(description=('Evolve'))
    
    parser.add_argument('-d', '--data', type=str,\
    help='data file', default='data/polygon_area_etc_input_0.txt') #polygon_area_etc_input
    
    parser.add_argument('-n', '--num_worker', type=int,\
    help='number of cores to use', default=settings.NWORKER)
    
    args = parser.parse_args()

    if "parent" == mpi_fork(args.num_worker+1): os._exit(0)

    main(args)                              

if __name__ == "__main__":
    run()    

