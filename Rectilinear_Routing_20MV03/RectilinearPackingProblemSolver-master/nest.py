
# here put the import lib
from tools import placement_worker, nfp_utls
import math
import json
import random
import copy
from Polygon import Polygon
import pyclipper
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
#from settings import SPACING, ROTATIONS, POPULATION_SIZE, MUTA_RATE,DEBUG,DRAWPIC,SCALE,COMPLEX_FIRST_STRATEGY,COMPLEX_FIRST_AREA_SECOND_STRATEGY,MIXED_COMPLEX_STRATEGY,STOP_GENERATION
from setting import settings
from GAlgo import genetic_algorithm



class ThisClass():
   
    config = {
                'curveTolerance': 0,                    
                'spacing': settings.SPACING,                
                'rotations': settings.ROTATIONS,           
                'populationSize': settings.POPULATION_SIZE,
                'mutationRate': settings.MUTA_RATE,         
                'useHoles': False,                         
                'exploreConcave': False                    
            }
    container = None
    container_bounds=None
    nfp_cache = {} 




class Nester:
  
    def __init__(self, container=None, shapes=None):
        
        self.originalshapes=[]
        self.container = container 
        self.shapes = shapes       
        self.shapes_total_area=None
        #self.shapes_max_length = 0 
        self.results = list()      
        self.nfp_cache = {}         
       
        self.config = ThisClass.config
        self.GA = None              
        self.best = None           
        self.worker = None         
        self.container_bounds = None 
    def add_objects(self, objects,objects_str):
        

        Args:
            objects (list):
            objects_str (str): 
    
        if not isinstance(objects, list):
            objects = [objects]
        if not self.shapes:
            self.shapes = []

        self.originalshapes=objects_str
        p_id = 0
        total_area = 0
        for obj in objects:
            points = self.clean_polygon(obj)
            shape = {
                'area': 0,
                'p_id': str(p_id),
                'points': [{'x': p[0], 'y': p[1]} for p in points]
            }

            area = nfp_utls.polygon_area(shape['points'])
            if area > 0:
                shape['points'].reverse()

            shape['area'] = abs(area)
            total_area += shape['area']
            self.shapes.append(shape)

        self.shapes_total_area=total_area

       
    def add_container(self, container):
    

        Args:
            container (dict): 
        if not self.container:
            self.container = {}

        self.origin_container=container

        container = self.clean_polygon(container)

        self.container['points'] = [{'x': p[0], 'y':p[1]} for p in container]
        self.container['p_id'] = '-1'
        xbinmax = self.container['points'][0]['x']
        xbinmin = self.container['points'][0]['x']
        ybinmax = self.container['points'][0]['y']
        ybinmin = self.container['points'][0]['y']

        for point in self.container['points']:
            if point['x'] > xbinmax:
                xbinmax = point['x']
            elif point['x'] < xbinmin:
                xbinmin = point['x']
            if point['y'] > ybinmax:
                ybinmax = point['y']
            elif point['y'] < ybinmin:
                ybinmin = point['y']

        self.container['width'] = xbinmax - xbinmin
        self.container['height'] = ybinmax - ybinmin

        self.container_bounds = nfp_utls.get_polygon_bounds(self.container['points'])

       self.calculateNFP()

 
    def calculateNFP(self):

        #self.nfp_cache     
        nfp_pairs = []      
        new_cache = {}   
        place_list=copy.deepcopy(self.shapes)
        #print(place_list)
        
        for i in range(0, len(place_list)):
           
            part = place_list[i]
            key = {
                'A': '-1',
                'B': str(i), 
                'inside': True,
                'A_rotation': 0,
                'B_rotation': 0
            }
            tmp_json_key = json.dumps(key)
            if not tmp_json_key in self.nfp_cache: 
                nfp_pairs.append({
                    'A': self.container,
                    'B': part, # {'area': 169.0, 'p_id': '0', 'points': [{'x': 165, 'y': 233}, {'x': 152, 'y': 233}, {'x': 152, 'y': 220}, {'x': 165, 'y': 220}]}
                    'key': key 
                })
             else: 
                 new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]
            
          
            for j in range(0, len(place_list)):
                placed = place_list[j]
                key = {
                    'A': str(j),
                    'B': str(i),
                    'inside': False,
                    'A_rotation': 0,
                    'B_rotation': 0
                }
                tmp_json_key = json.dumps(key)
                if not tmp_json_key in self.nfp_cache:
                    nfp_pairs.append({
                        'A': placed,
                        'B': part,
                        'key': key
                    })
                 else:
                   new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]
    


        
                 
        # from tool.calculate_npf import NFP_Calculater
        # nfp_calculater=NFP_Calculater(self.config)
        # pair_list = []
        # for pair in nfp_pairs: #计算待计算NFP
        #     pair_list.append(nfp_calculater.process_nfp(pair))

        from main import batchNFPCalculate
        pair_list=batchNFPCalculate(self.nWorker,nfp_pairs)


        #print(pair_list)
        

        if pair_list:
            for i in range(0, len(pair_list)):
                if pair_list[i]:#{'key': pair['key'], 'value': nfp}
                    key = json.dumps(pair_list[i]['key'])
                    self.nfp_cache[key] = pair_list[i]['value']#{"pair['key']":nfp}
                    

       
        from main import batchSendContainerAndNFPCache
        batchSendContainerAndNFPCache(self.nWorker,self.container,self.nfp_cache)

    def polygon_offset(self, polygon, offset):
  
        Args:
            polygon (list): 
            offset ([type]): 

        Returns:
            list: 
     
        is_list = True
        if isinstance(polygon[0], dict):
            polygon = [[p['x'], p['y']] for p in polygon]
            is_list = False

        miter_limit = 2
        co = pyclipper.PyclipperOffset(miter_limit, self.config['curveTolerance'])
        co.AddPath(polygon, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        result = co.Execute(1*offset)
        if not is_list:
            result = [{'x': p[0], 'y':p[1]} for p in result[0]]
        return result

    def clear(self):

        self.shapes = None

    def run(self):

        
        if self.GA is None:
            faces = list()
            for i in range(0, len(self.shapes)):
                shape = copy.deepcopy(self.shapes[i])
                shape['points'] = self.polygon_offset(shape['points'], self.config['spacing'])
                faces.append([str(i), shape])

            faces = sorted(faces, reverse=True, key=lambda face: face[1]['area'])

            if settings.COMPLEX_FIRST_STRATEGY:
                do1=True
                do2=False
                do3=False
            elif settings.COMPLEX_FIRST_AREA_SECOND_STRATEGY:
                do1=True
                do2=True
                do3=False
            elif settings.MIXED_COMPLEX_STRATEGY:
                do1=True
                do2=False
                do3=True
            if do1:
                list_Dio=[]
                list_L=[]
                list_Square=[]
                for item in faces:
                    if len(item[1]["points"])>6:
                        list_Dio.append(item)
                    elif len(item[1]["points"])==6:
                        list_L.append(item)
                    else:
                        list_Square.append(item)
                if do2:
                    percent=0.9
                    BigDio=list_Dio[0:int(len(list_Dio)*percent)]
                    SmallDio=list_Dio[int(len(list_Dio)*percent):]
                    BigL=list_L[0:int(len(list_L)*percent)]
                    SmallL=list_L[int(len(list_L)*percent):]
                    BigS=list_Square[0:int(len(list_Square)*percent)]
                    SmallS=list_Square[int(len(list_Square)*percent):]
                    faces=BigDio+BigL+BigS+SmallDio+SmallL+SmallS
                elif do3:
                    percent=0.5
                    SmallS=list_Square[int(len(list_Square)*percent):]
                    BigS=list_Square[0:int(len(list_Square)*percent)]
                    Mixed=list_Dio+list_L+BigS
                    Mixed=sorted(Mixed, reverse=True, key=lambda Mixed: Mixed[1]['area'])
                    print(Mixed)
                    print("****")
                    print(SmallS)
                    faces=Mixed+SmallS
                else:
                    faces=list_Dio+list_L+list_Square
            self.launch_workers(faces)
        else:
            self.launch_workers()
    
    def launch_workers(self, adam=None):


        Args:
            adam (list, optional):
        if self.GA is None:
            offset_bin = copy.deepcopy(self.container)
            offset_bin['points'] = self.polygon_offset(self.container['points'], self.config['spacing'])
            self.GA = genetic_algorithm(adam, offset_bin, self.config)
        else:
            self.GA.generation()

        # for i in range(0, self.GA.config['populationSize']):
        #     res = self.find_fitness(self.GA.population[i])
        #     self.GA.population[i]['fitness'] = res['fitness']
        #     self.results.append(res)

        from main import batchMpiEval
        self.results=batchMpiEval(self.nWorker,self.GA.population)
        for i in range(0, self.GA.config['populationSize']):
            self.GA.population[i]['fitness'] = self.results[i]['fitness']


        if len(self.results) > 0:
            best_result = self.results[0]

            for p in self.results:
                if p['fitness'] < best_result['fitness']:
                    best_result = p

            if self.best is None or best_result['fitness'] < self.best['fitness']:
                self.best = best_result

        self.results [{'placements': all_placements, 'fitness': fitness,'min_width':min_width, 'paths': paths, 'area': bin_area}]
 	self.best
        print(self.best)

    def clean_polygon(self, polygon):
      

        Args:
            polygon ([type]): [description]

        Returns:
            [type]: [description]
        """
        simple = pyclipper.SimplifyPolygon(polygon, pyclipper.PFT_NONZERO)

        if simple is None or len(simple) == 0:
            return None

        biggest = simple[0]
        biggest_area = pyclipper.Area(biggest)
        for i in range(1, len(simple)):
            area = abs(pyclipper.Area(simple[i]))
            if area > biggest_area:
                biggest = simple[i]
                biggest_area = area

        clean = pyclipper.CleanPolygon(biggest, self.config['curveTolerance'])
        if clean is None or len(clean) == 0:
            return None
        return clean


from tools.calculate_npf import NFP_Calculater
def find_fitness(individual,container,nfp_cache):
   

    Args:
        individual (dict): 
        container (dict): 
        nfp_cache (dict):

    Returns:
        dict: 
   
    place_list = copy.deepcopy(individual['placement'])
    rotations = copy.deepcopy(individual['rotation'])
    ids = [p[0] for p in place_list]

    for i in range(0, len(place_list)):
        place_list[i].append(rotations[i])
    

    nfp_pairs = list()
    for i in range(0, len(place_list)):
    
        part = place_list[i]
        key = {
            'A': '-1',
            'B': part[0],
            'inside': True,
            'A_rotation': 0,
            'B_rotation': rotations[i]
        }

        tmp_json_key = json.dumps(key)
        if not tmp_json_key in nfp_cache:
            nfp_pairs.append({
                'A': container,
                'B': part[1],
                'key': key
            })

        for j in range(0, i):
            placed = place_list[j]
            key = {
                'A': placed[0],
                'B': part[0],
                'inside': False,
                'A_rotation': rotations[j],
                'B_rotation': rotations[i]
            }
            tmp_json_key = json.dumps(key)
            if not tmp_json_key in nfp_cache:
                nfp_pairs.append({
                    'A': placed[1],
                    'B': part[1],
                    'key': key
                })
    pair_list = list()
    for pair in nfp_pairs:
        pair_list.append(NFP_Calculater.process_nfp(pair))
    if pair_list:
        for i in range(0, len(pair_list)):
            if pair_list[i]:#{'key': pair['key'], 'value': nfp}
                key = json.dumps(pair_list[i]['key'])
                nfp_cache[key] = pair_list[i]['value']#{"pair['key']":nfp}

    worker = placement_worker.PlacementWorker(
            container, place_list, ids, rotations, ThisClass.config, nfp_cache)
    result=worker.place_paths()
    return result

def draw_result(shift_data, polygons,polygons_str, bin_polygon, bin_bounds,file_path,file_id):
  
    def myrotate_polygon(contour, angle):
        rotated = []
        #angle = angle * math.pi / 180
        if angle==0:
            cosangle=1
            sinangle=0
        elif angle==90:
            cosangle=0
            sinangle=1
        elif angle==180:
            cosangle=-1
            sinangle=0
        elif angle==270:
            cosangle=0
            sinangle=-1
        for x,y in contour:
            rotated.append([
                x *cosangle - y * sinangle,
                x * sinangle + y *cosangle
            ])
        return Polygon(rotated)


    #print(polygons)
    shapes = list()
    for polygon in polygons:
        contour = [[p['x'], p['y']] for p in polygon['points']]
        shapes.append(Polygon(contour))

    bin_shape = Polygon([[p['x'], p['y']] for p in bin_polygon['points']])
    
    shape_area = bin_shape.area(0)

    solution = list()
    rates = list()
    #loops=1
    #print(shift_data)
    shapes_before=copy.deepcopy(shapes)
    for s_data in shift_data:
        #print(loops)
        #loops=loops+1
       
        tmp_bin = list()
        total_area = 0.0
        for move_step in s_data:
            if move_step['rotation'] > 0:

                print("before",[p for p in shapes[int(move_step['p_id'])].contour(0)])
                shapes[int(move_step['p_id'])].rotate(math.pi / 180 * move_step['rotation'], 0, 0)
                shapes[int(move_step['p_id'])]= myrotate_polygon(shapes[int(move_step['p_id'])].contour(0),move_step['rotation'])   
                print("after",[p for p in shapes[int(move_step['p_id'])].contour(0)])
                shapes[int(move_step['p_id'])]=  shapes[int(move_step['p_id'])]
   
            shapes[int(move_step['p_id'])].shift(move_step['x'], move_step['y'])
            tmp_bin.append(shapes[int(move_step['p_id'])])
            total_area += shapes[int(move_step['p_id'])].area(0)
            #print("total_area",total_area)

        rates.append(total_area)
        solution.append(tmp_bin)

    idx=0
    myresult=""
    max_x=0
    max_y=0
    while(idx<len(shapes)):
        inpolygon= polygons_str[idx]
        # inpolygon=""
        # for x,y in shapes_before[idx].contour(0):
        #     inpolygon=inpolygon+"({x},{y})".format(x=x/SCALE,y=y/SCALE)
        outpolygon=""
        for x,y in shapes[idx].contour(0):
            if x>max_x:max_x=x 
            if y>max_y:max_y=y
            outpolygon=outpolygon+"({x},{y})".format(x=x/settings.SCALE,y=y/settings.SCALE)
        text=\
"""In Polygon:
{inpolygon}
Out Polygon:
{outpolygon}\n""".format(inpolygon=inpolygon,outpolygon=outpolygon)
        myresult=myresult+text
        idx=idx+1
    myresult=myresult.rstrip("\n")
    result_file=file_path+"/result_"+file_id+".txt"
    import os
  if os.path.exists(file_path+"/result.txt"):
        i=1 
        flag=1
      while flag:
          if os.path.exists(file_path+"/result_"+str(i)+".txt"):
              i=i+1
                continue
          result_file=file_path+"/result_"+str(i)+".txt"
            flag=0
    with open(result_file,"w")as file_hand:
        file_hand.write(myresult)
    if settings.DEBUG:
        print("polygon total area:",rates[-1]/(settings.SCALE*settings.SCALE))
        print("bin:",max_x/10,max_y/10)
        print("occupation:",rates[-1]/(max_x*max_y))
    if settings.DRAWPIC:
        draw_polygon(solution, rates, bin_bounds, bin_shape,max_x,max_y,rates[-1]/(max_x*max_y))


def draw_polygon(solution, rates, bin_bounds, bin_shape,packed_x,packed_y,occupation):
 

    Args:
        solution (dict): 
        rates (list): rates
        bin_bounds (dict): 
        bin_shape (dict): 
        packed_x (float): 
        packed_y (float): 
        occupation (float): 

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    base_width = 8
    base_height = base_width * bin_bounds['height'] / bin_bounds['width']
    num_bin = len(solution)
    fig_height = num_bin * base_height
    # fig1 = Figure(figsize=(base_width, fig_height))
    # FigureCanvas(fig1)
    fig1 = plt.figure(figsize=(base_width, fig_height))
    fig1.suptitle('Polygon packing', fontweight='bold')

    i_pic = 1  
    for shapes in solution:

        ax = plt.subplot(num_bin, 1, i_pic, aspect='equal')
       
        ax.set_title('%0.4f,%0.4f,%0.4f'%(packed_x,packed_y,occupation))
        i_pic += 1
        ax.set_xlim(bin_bounds['x'] - 10, bin_bounds['width'] + 50)
        ax.set_ylim(bin_bounds['y'] - 10, bin_bounds['height'] + 50)

        output_obj = list()
        output_obj.append(patches.Polygon(bin_shape.contour(0),fc="white"))
        output_obj.append(patches.Polygon([(0,0),(packed_x,0),(packed_x,packed_y),(0,packed_y)],lw=1,edgecolor='m'))
        #output_obj.append(patches.Polygon(bin_shape.contour(0), fc='green'))
        for s in shapes:
            color=[random.random(),random.random(),random.random()]
            output_obj.append(patches.Polygon(s.contour(0),color=color,alpha=0.5))

            #output_obj.append(patches.Polygon(s.contour(0), fc='yellow', lw=1, edgecolor='m'))
        for p in output_obj:
            ax.add_patch(p)
    plt.show()
    # fig1.save()

def content_loop_rate(best, n,file_path,file_id, loop_time=20,height=100):


    Args:
        best (dict):
        n (NEST):
        file_path (str): 
        file_id (str): 
        loop_time (int, optional):
        height (int, optional):
    """
    print("STOP_GENERATION",settings.STOP_GENERATION)
    res = best
    run_time = loop_time
    loops=1
    if settings.DEBUG:
        import time
        current_time=time.time()
        last_time=current_time
        generation_time=[]
        best_fitness_for_all_generation=[]
        best_fitness_for_current_generation=[]
        square_like_for_all_generation=[]
        square_like_for_current_generation=[]
    while run_time:
        #print("content_loop_rate",loops)
        loops=loops+1
        n.run()
        best = n.best
        #print (best['fitness'])
        if best['fitness'] <= res['fitness']:
            res = best
            #print ('change', res['fitness'])
 
 
        #self.results [{'placements': all_placements, 'fitness': fitness,'min_width':min_width, 'paths': paths, 'area': bin_area}]

        if settings.DEBUG:
            current_time=time.time()
            generation_time.append(10*(current_time-last_time))
            last_time=current_time
            best_fitness_for_all_generation.append(res['fitness'])
            best_fitness_for_current_generation.append(best['fitness'])
            square_like_for_all_generation.append(res['min_width']/height)
            square_like_for_current_generation.append(best['min_width']/height)
        ####################################################

        run_time -= 1

 
        if n.shapes_total_area/(best['min_width']*settings.BIN_NORMAL[2][1])>settings.SMALLCASE_EXPECTATION:
            print("***",n.shapes_total_area/(best['min_width']*settings.BIN_NORMAL[2][1]))
            print(n.shapes_total_area,best['min_width'],settings.BIN_NORMAL[2][1])
            run_time=False

    if settings.DEBUG:
        print("best_fitness_for_all_generation",best_fitness_for_all_generation)
    if settings.DRAWPIC:
        from matplotlib import pyplot as plt
        from matplotlib.pyplot import MultipleLocator

        x = range(1,len(best_fitness_for_all_generation)+1)       

        plt.grid(axis='x',color='0.95')
        plt.step(x,best_fitness_for_all_generation, label="best_fitness_for_all_generation",color='red',marker='^')
        plt.step(x,best_fitness_for_current_generation, label="best_fitness_for_current_generation",color='blue')
        plt.xlabel('generation')
        plt.ylabel('fitness',color='b')
       ax.legend()
       x_major_locator=MultipleLocator(1)
      ax.xaxis.set_major_locator(x_major_locator) 

        plt.figure(2)
        plt.step(x,square_like_for_all_generation, label="square_like_for_all_generation",linestyle="--",color='red',marker='^')
        plt.step(x,square_like_for_current_generation, label="square_like_for_current_generation",linestyle="--",color='blue')
        plt.xlabel('generation')
        plt.ylabel('square_like',color='r')
        plt.title('Sample Run')

        plt.figure(3)
        plt.bar(x, generation_time, color='rgb', tick_label=x)

    draw_result(res['placements'], n.shapes,n.originalshapes, n.container, n.container_bounds,file_path,file_id)

