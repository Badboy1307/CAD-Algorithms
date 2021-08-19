# here put the import lib
import copy
from tools import  nfp_utls
import random


class genetic_algorithm():


    def __init__(self, adam, bin_polygon, config):
        
        :param adam:
        :param bin_polygon: 
        :param config:
   
        self.bin_bounds = bin_polygon['points']
        self.bin_bounds = {
            'width': bin_polygon['width'],
            'height': bin_polygon['height'],
        }
        self.config = config
        self.bin_polygon = bin_polygon
        angles = list()
        shapes = copy.deepcopy(adam)
        for shape in shapes:
            #angles.append(0)
            angles.append(self.random_angle(shape))

       
        #print("-----------------first population-----------------------")
        self.population = [{'placement': shapes, 'rotation': angles}]
        #print(self.population)
        #print("-----------------end of first population-----------------------")

        for i in range(1, self.config['populationSize']):
            mutant = self.mutate(self.population[0])
            self.population.append(mutant)

    def random_angle(self, shape):
        """
        :param shape:
        :return:
        """
        angle_list = list()
        for i in range(0, self.config['rotations']):
            angle_list.append(i * (360/self.config['rotations']))

    
        def shuffle_array(data):
            for i in range(len(data)-1, 0, -1):
                j = random.randint(0, i)
                data[i], data[j] = data[j], data[i]
            return data
            

        angle_list = shuffle_array(angle_list)

       
        for angle in angle_list:
            rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], angle)
            
            if rotate_part['width'] < self.bin_bounds['width'] and rotate_part['height'] < self.bin_bounds['height']:
                return angle_list[i]
                #return 0

        return 0

    def mutate(self, individual):
        clone = {
            'placement': individual['placement'][:],
            'rotation': individual['rotation'][:]
        }
        for i in range(0, len(clone['placement'])):
            if random.random() < 0.01 * self.config['mutationRate']:
                if i+1 < len(clone['placement']):
                    clone['placement'][i],clone['placement'][i+1] = clone['placement'][i+1], clone['placement'][i]
            if random.random() < 0.01 * self.config['mutationRate']:
                clone['rotation'][i] = self.random_angle(clone['placement'][i])

        # for i in range(int(len(clone['placement'])*0.9), len(clone['placement'])):
        #     if 1:
        #         if i+1 < len(clone['placement']):
        #             clone['placement'][i],clone['placement'][i+1] = clone['placement'][i+1], clone['placement'][i]
        #     if 1:
        #         clone['rotation'][i] = self.random_angle(clone['placement'][i])


        return clone

    def generation(self):

        self.population = sorted(self.population, key=lambda a: a['fitness'])
        new_population = [self.population[0]]
        while len(new_population) < self.config['populationSize']:
            male = self.random_weighted_individual()
            female = self.random_weighted_individual(male)
            children = self.mate(male, female)


            new_population.append(self.mutate(children[0]))

            if len(new_population) < self.config['populationSize']:
                new_population.append(self.mutate(children[1]))
        # print("------------------new population----------------------")
        # print ('new :', new_population)
        # print("------------------end new population----------------------")
        self.population = new_population

    def random_weighted_individual(self, exclude=None):

        pop = self.population
        if exclude and pop.index(exclude) >= 0:
            pop.remove(exclude)
        rand = random.random()
        lower = 0
        weight = 1.0 / len(pop)
        upper = weight
        pop_len = len(pop)
        for i in range(0, pop_len):
            if (rand > lower) and (rand < upper):
                return pop[i]
            lower = upper
            upper += 2 * weight * float(pop_len-i)/pop_len
        return pop[0]

    def mate(self, male, female):
        cutpoint = random.randint(0, len(male['placement'])-1)
        gene1 = male['placement'][:cutpoint]
        rot1 = male['rotation'][:cutpoint]

        gene2 = female['placement'][:cutpoint]
        rot2 = female['rotation'][:cutpoint]

        def contains(gene, shape_id):
            for i in range(0, len(gene)):
                if gene[i][0] == shape_id:
                    return True
            return False

        for i in range(len(female['placement'])-1, -1, -1):
            if not contains(gene1, female['placement'][i][0]):
                gene1.append(female['placement'][i])
                rot1.append(female['rotation'][i])

        for i in range(len(male['placement'])-1, -1, -1):
            if not contains(gene2, male['placement'][i][0]):
                gene2.append(male['placement'][i])
                rot2.append(male['rotation'][i])

        return [{'placement': gene1, 'rotation': rot1}, {'placement': gene2, 'rotation': rot2}]


    def minkowski_difference(A, B):

        Ac = [[p['x'], p['y']] for p in A['points']]
        Bc = [[p['x'] * -1, p['y'] * -1] for p in B['points']]
        solution = pyclipper.MinkowskiSum(Ac, Bc, True)
        largest_area = None
        clipper_nfp = None
        for p in solution:
            p = [{'x': i[0], 'y':i[1]} for i in p]
            sarea = nfp_utls.polygon_area(p)
            if largest_area is None or largest_area > sarea:
                clipper_nfp = p
                largest_area = sarea

        clipper_nfp = [{
                        'x': clipper_nfp[i]['x'] + Bc[0][0] * -1,
                        'y':clipper_nfp[i]['y'] + Bc[0][1] * -1
                    } for i in range(0, len(clipper_nfp))]
        return [clipper_nfp]
