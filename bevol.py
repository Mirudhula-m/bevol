# -*- coding: utf-8 -*-
"""bevol.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eEmQhvJfVH-I6pcKBTriloiN8Vp-Z6jD
"""

# from google.colab import drive
# drive.mount('/content/drive')

from numpy import random
import numpy as np
import matplotlib.pyplot as plt
import math 
import time 
import scipy.integrate as it
# import random

"""# Initialize parameters

"""

# initialization parameters
global population

global n_generations
n_generations = 1000

global population_size
population_size = 5

global init_genome_size
init_genome_size = 1000

#decoding parameters
global consensus
consensus = np.array([0,1,0,1,0,1,1,0,0,1,1,1,0,0,1,0,0,1,0,1,1,0])
global shine_delgarno
shine_delgarno = np.array([0.,1.,1.,0.,1.,1.])
global start
start = [0,0,0]
global stop
stop = [0,0,1]
global dmax
dmax = 4
global stem_loop
stem_size = 4
global loop_size
loop_size = 3

global wmax
wmax = 0.0051

# selection parameters
k_stressed = 1000 #extra - not being used now 
k_wildtype = 750 
k_relaxed = 250 

# mutation rates
global u_point
u_point = 5*10**-5
global u_smalli
u_smalli = 5*10**-5
global u_smalldel
u_smalldel = 5*10**-5
global u_largedel
u_largedel = 5*10**-5
global u_duplic
u_duplic = 5*10**-5
global u_inv
u_inv = 5*10**-5
global u_transloc
u_transloc = 5*10**-5
global mut_array

class Population:
  def __init__(self, n):
    self.n_individuals = n
    #self.individuals = genomes #list
    #self.offsprings = np.zeros((len(self.individuals)))
    # self.u_point = 5*10**-6
    # self.u_smalli = 5*10**-6
    # self.u_smalldel = 5*10**-6
    # self.u_largedel = 5*10**-6
    # self.u_duplic = 5*10**-6
    # self.u_inv = 5*10**-6
    # self.u_transloc = 5*10**-6

class Protein:
  def __init__(self, m, w, h, e):
    self.m = m
    self.w = w
    self.h = h 
    self.e = e

class Individual:
  def __init__(self, genome):
    self.genome = genome
    self.genome_size = genome.shape[0]
    # self.proteins = Protein(m, w, h, e) #list
    # self.num_offspring =  num_offspring 
    # self.fp = fp #list of discrete fp values

"""# Init """

def firstGene(randomCodons):
  gene = []
  for c in randomCodons:
    if c==0:
      gene = np.concatenate((gene, [1,0,0]))
      # aa = ['M', '0']
    elif c==1:
      gene = np.concatenate((gene, [1,0,1]))
      # aa = ['M', '1']
    elif c==2:
      gene = np.concatenate((gene, [0,1,0]))
      # aa = ['W', '0']
    elif c==3:
      gene = np.concatenate((gene, [0,1,1]))
      # aa = ['W', '1']
    elif c==4:
      gene = np.concatenate((gene, [1,1,0]))
      # aa = ['H', '0']
    elif c==5:
      gene = np.concatenate((gene, [1,1,1]))
      #aa = ['H', '1']
  
  return gene

def InitializeIndividual():  
  seq = np.random.choice([0,1], size=init_genome_size)

  promoter = consensus.copy()
  d = np.random.choice(np.arange(dmax),size=1)
  mask_i = np.random.randint(0,len(promoter), size=d)

  for i in mask_i:
    if promoter[i]==0:
      promoter[i]=1
    elif promoter[i]==1:
      promoter[i]=0
  
  # print(f'Initialize Individual.............')

  # Transcription is delimited by promoter and terminator
  stem = np.random.choice([0,1], size=stem_size)
  loop = np.random.choice([0,1], size=loop_size)
  terminator = np.concatenate((stem, loop, stem[::-1]))
  
  # Translation is delimited by start and stop, where start must follow the shine_delgarno init
  # first gene must not contain stop or start codon
  init = np.hstack((shine_delgarno, np.random.choice([0,1], size=4)))
  randomSeq = np.random.choice(np.arange(6), size=30)
  gene = firstGene(randomSeq)
  coding = np.hstack((init, start, gene, stop))
  
  # First coding sequence is inserted into a random spot in the genome
  rand_i = np.random.randint(0,len(seq)-5)
  chromosome = np.hstack((seq[:rand_i], promoter, seq[rand_i:rand_i+5], coding, seq[rand_i+5:], terminator))

  i = Individual(chromosome)

  return i

def Initialize(n):
  
  population = Population(n)
  
  individuals = []

  for _ in range(n):
    individuals.append(InitializeIndividual())
  
  population.individuals = individuals
  # print(f'population.individuals type leaving Initialize = {type(population.individuals)}')

  return population

"""# Trancription and Translation

Initially, the genome will be randomly generated with at least one coding region. A loose form of transcription will occur between 22 bp promoters and stop codons. We will assign an expression level to the transcript $e=1-\frac{d}{1+d_{max}}$ where $d$ represents the hamming distance between the promoter and a pre-defined consensus. The artificial genetic code will used be sequentially translate each 3 bp codon into one of 6 possible amino acids M0, M1, W0, W1, H0, H1, or the start or stop codon. This sequence of amino acids will then be used to compute the phenotypic contribution for each protein which may be inhibitory.

Given the sequence of amino acids, we will calculate $m$, $w$, and $h$, where the protein may be represented as a triangle graph as a function of these values. $m$ represents the mean "cellular process" of the protein, $w$ represents the range of pleiotropy that this protein exhibits, and $h$ represents the efficiency of the protein. 

In computational terms, the codons form the Gray codes of the three parameters $m$, $w$, and $h$. For example, if the amino acid sequence is M1,H0,W1,M0,H1, then the Gray code for $m$ is 10, for $w$ is 1, and for $h$ is 01.
!!!!!!!!!!!Need to discuss these normalizations!!!!!!!!!!! $w$ is then normalized by multiplying by $w*\frac{w_{max}}{2^{n_{w}}-1}$ where $n_w$ is the number of W0 or W1 in the sequence; $m$ is normalized similarly between 0 and 1 and $h$ between -1 and 1. !!!!!!!!!!! With these values of $m$, $w$, and $h$ defining each protein, the global phenotype of the individual may be calculated.

##Pattern matching for Promoter
"""

def isPromoter(candidate):
  valid = True
  
  d = 0
  for i, (nucP, nucC) in enumerate(zip(candidate, consensus)):
    if nucP != nucC:
      d += 1
    if d > dmax:
      valid=False
      break

  return valid

def isTerminator(candidate):
  valid = False

  if (candidate[0:4]==candidate[::-1][0:4]).all():
          valid = True

  return valid

def hamming_dist(promoter):
  d=0
  for (nucP, nucC) in zip(promoter, consensus):
    if nucP != nucC:
      d += 1
  return d




def isInitiationSignal(candidate):
  valid = False
  if len(candidate)>=len(shine_delgarno+4):
    if np.array_equal(candidate[:len(shine_delgarno)], shine_delgarno):
      if np.array_equal(candidate[len(shine_delgarno)+4:], start):
        valid = True
  return valid

# find coding sequence in the delimited region.
# The delimited region must be at least 3 codons
def findCodingSeq(delimited):
  codingSeq = []

  if len(delimited)>=len(shine_delgarno)+4+len(start)+9+len(stop):
    # Sliding window for finding initialization sequence in the given delimited
    
    for i in range(0,len(delimited)-len(shine_delgarno)+4+len(start)):
      init_candidate = delimited[i:i+len(shine_delgarno)+4+len(start)].copy()
      if isInitiationSignal(init_candidate):
        codingSeq = delimited[i+len(shine_delgarno)+4+len(start):].copy()
    
    hasStop = False
    for i in range(0, len(codingSeq)-3, 3):
      if (codingSeq[i:i+3]==stop).all():
        codingSeq = codingSeq[:i].copy()
        hasStop = True
        break
    
    if hasStop == False:
      codingSeq = []
  

  return codingSeq

def FindTranscripts(ch):

  # transcript_list is a list
  transcript_list = []
  e_list = []

  # for every window starting position
  for i in range(0,len(ch)-len(consensus)+1):

    # consider candidate window
    p_candidate = ch[i:i+len(consensus)]

    if isPromoter(p_candidate):
      # print(f'Found promoter: {p_candidate}')
      d = hamming_dist(p_candidate)
      e = 1-(d/(1+dmax))

      # sliding window for finding terminator:
      # promoter will be followed by terminator and delimit transcript
      for j in range (i+9, len(ch)-(2*stem_size+loop_size)+1):

        # consider candidate window
        t_candidate = ch[j:j+stem_size+stem_size+loop_size]

        if isTerminator(t_candidate):

          delimited = ch[i+len(consensus)+1:j].copy()

          codingSeq = findCodingSeq(delimited)
          
          if len(codingSeq)>0:
            transcript_list.append(codingSeq)
            e_list.append(e)
            break

  return transcript_list, e_list

"""##Decoding for Translation"""

def decode(codon):
  aa = []
  if (codon==[1,0,0]).all():
    aa = ['M', '0']
  elif (codon==[1,0,1]).all():
    aa = ['M', '1']
  elif (codon==[0,1,0]).all():
    aa = ['W', '0']
  elif (codon==[0,1,1]).all():
    aa = ['W', '1']
  elif (codon==[1,1,0]).all():
    aa = ['H', '0']
  elif (codon==[1,1,1]).all():
    aa = ['H', '1']
  
  return aa
  
def GrayCode(aaSeq):
  nM = 0
  mSeq = []
  nW = 0
  wSeq = []
  nH = 0
  hSeq = []

  for aa in aaSeq:

    if len(aa)>0:
      if aa[0]=='M':
        nM += 1
        mSeq.append(aa[1])
      elif aa[0]=='W':
        nW += 1
        wSeq.append(aa[1])
      elif aa[0]=='H':
        nH += 1
        hSeq.append(aa[1])
  
  
  m, w, h = 0, 0, 0

  if nM!=0 and nW!=0 and nH!=0:
    #normalize to 0 to 1
    M = int("".join(mSeq))
    Mmax = int("".join(np.random.choice(['1'], size=nM)))
    m = M /(Mmax)
    
    # normalize to 0 to wmax
    W = int("".join(wSeq))
    Wmax = int("".join(np.random.choice(['1'], size=nW)))
    w = W * wmax/Wmax
    
    # normalize to -1 to 1
    H = int("".join(hSeq))
    Hmax = int("".join(np.random.choice(['1'], size=nH)))
    h = (2*(H+1)/Hmax)-1
  
  return m, w, h


def DNAtoProtein(codingSeq):

  aaSeq = []
  
  i=0
  while i < len(codingSeq)-3:
    aa = decode(codingSeq[i:i+3])
    aaSeq.append(aa)
    i += 3
  
  m, w, h = GrayCode(aaSeq)

  return m, w, h

def Translate(transcripts, e_levels):
  proteins = []
  for t, e in zip(transcripts, e_levels):
    m, w, h = DNAtoProtein(t)
    if m!=0 and w!=0 and h!=0:
      protein = Protein(m, w, h, e)
      proteins.append(protein)
  
  return proteins

"""# Protein to Phenotype
input - list of proteins (each with w, m, h, e)

output - list of fp
"""

'''
Input list of proteins 
Returns a list of m
'''
def get_m_list(proteins):
  m_list = []
  for protein in proteins:
    m_list.append(protein.m)
  return set(m_list)

'''
Input:
proteins - list of proteins
Output: 
fi - a dictionary of the m mapped to the probability for activators
fj - a dictionary of the m mapped to the probability for inhibitors
m_list - list of all m 
'''
def summation_protiens(individual):
  m_list = get_m_list(individual.proteins)
  fi = {}
  fj = {}
  for protein in individual.proteins:
    if protein.h > 0:
      if protein.m not in fi.keys():
        fi[protein.m] = protein.e * np.abs(protein.h) * protein.w
      else: 
        fi[protein.m] += protein.e * np.abs(protein.h) * protein.w
    if protein.h < 0:
      if protein.m not in fj.keys():
        fj[protein.m] = protein.e * np.abs(protein.h) * protein.w
      else:
        fj[protein.m] += protein.e * np.abs(protein.h) * protein.w
  return fi, fj, m_list

"""
Input: 
fi -  sum of activators
fj - sum of inhibitors

Output:
fp - dict of phenotype of the individual at each m
"""
def get_fp(fi, fj, m_list):
  fp = {}
  fi_keys = fi.keys()
  fj_keys = fj.keys()
  for m in m_list:
    if (m in fi_keys) and (m in fj_keys):
      fp[m] = (max(min(fi[m], 1) - min(fj[m], 1), 0)) 
    elif m in fi_keys:
      fp[m] = (max(min(fi[m], 1.0), 0.0))
    elif m in fj_keys:
      fp[m] = 0
  return fp

"""# Fitness Step"""

def find_gap(fe_integrate, fp_x:list, fp_y:list) -> float:
  
  # print(f'fe_integrate = {fe_integrate}')
  with open('console.log', 'a') as f:
    f.write("\nfe_integrate = " + str(fe_integrate))
  fp_integrate = it.trapz(fp_y, fp_x)
  g = fe_integrate - fp_integrate

  return g

def generate_points(num_points:int) -> np.array:
  points = []
  for _ in range(num_points):
    points.append(random.random())
  points = np.array(points)
  
  return points

"""# Decode"""

fe_x = generate_points(50_000)
fe_y = generate_points(50_000)
fe_integrate = it.trapz(fe_x, fe_y)

def Decode_Evaluate(population):
  g = []
  for individual in population.individuals:
    transcripts, e_levels = FindTranscripts(individual.genome) # list of lists of transcripts and expression
    proteins = Translate(transcripts, e_levels) # list of m, w, h, and e for each protein in an individual
    individual.proteins = proteins

    #Emma
    fi, fj, m_list = summation_protiens(individual)
    with open('console.log', 'a') as f:
      f.write(f"\nm_list = {m_list}")
    fp = get_fp(fi, fj, m_list)
    with open('console.log', 'a') as f:
      f.write(f"\nfp = {fp}")

    #Sriram
    fp_x = list(fp.keys())
    fp_y = list(fp.values())
    g.append(find_gap(fe_integrate, fp_x, fp_y))
  return g

"""# Selection

"""

def Selection(population, g, k):
  #calculate the probability of reproduction of each individual
  n = len(population.individuals)
  reproP = np.zeros((n))
  
  sum = 0.0
  for i in range(0, len(g)):
    sum += math.exp(-k*g[i])
  
  #print("reproP error tracking", -k*g[0], math.exp(-k*g[0]))

  for i in range(0, len(g)):
    reproP[i] = math.exp(-k*g[i])/ float(sum) 

  # with open('console.log', 'a') as f:
  #   f.write("\nreproP = "+str(reproP))

  population.offsprings = np.random.multinomial(n, reproP)

  # return np.random.multinomial(n, reproP)

"""# Mutation """

def Mutation(population,mut_array):
  print("Entering Mutation step")
  with open('console.log', 'a') as f:
    f.write("\nENTERING MUTATION STEP")
  population.individuals,mut_array = mut(population.individuals, population.offsprings,mut_array)
  return mut_array

def mut(individuals, numOffspring,mut_array):
  # get the index of the largest numOffspring
  mut_idx = np.argmax(np.array(numOffspring))

  num_ind = len(individuals)
  children = []#np.array(()).reshape(num_ind,0)
  for index in range(num_ind):
    if index == mut_idx:
      measure_mut = True
    else:
      measure_mut = False
    ind = individuals[index].genome
    n = numOffspring[index]
    for ch in range(n):
      with open('console.log', 'a') as f:
        f.write("\n\n####### PARENT-CHILD NUMBER = "+str(index)+" "+str(ch)+"\n")
      child = ind.copy()
      # Find length of genome
      L = child.shape[0]
      # Find the number of each type of mutations that should occur
      # Numbers for Rearrangement Mutations
      N_largedel = random.binomial(L,u_largedel) # 0
      N_duplic = random.binomial(L,u_duplic) # 1
      N_inv = random.binomial(L,u_inv) # 2
      N_transloc = random.binomial(L,u_transloc) # 3
      # Conduct Rearrangement mutations
      # choose a random number from 0 to 3 inclusive
      # this is done to conduct the mutations in random order
      rand_mut = np.random.permutation(4)
      for k in rand_mut:
        if k == 0:
            child,mut_array = large_deletion(child,N_largedel,mut_array,measure_mut)
        elif k == 1:
              child,mut_array = duplication(child,N_duplic,mut_array,measure_mut)
        elif k == 2:
            child,mut_array = inversion(child,N_inv,mut_array,measure_mut)
        else:
            child,mut_array = translocation(child,N_transloc,mut_array,measure_mut)

      # Find length of genome again
      L = child.shape[0]
      # Local Mutations
      N_point = random.randint(L) # 0
      N_smalli = random.randint(L) # 1
      N_smalldel = random.randint(L) # 2

      # Conduct Local Mutations
      # choose a random number from 0 to 2 inclusive
      # this is done to conduct the mutations in random order
      rand_mut = np.random.permutation(3)
      for k in rand_mut:
        if k == 0:
            child,mut_array = point(child,N_point,u_point,mut_array,measure_mut)
        elif k == 1:
            child,mut_array = small_insert(child,N_smalli,u_smalli,mut_array,measure_mut)
        else:
            child,mut_array = small_deletion(child,N_smalldel,u_smalldel,mut_array,measure_mut)
      
      children.append(Individual(child))
  return children,mut_array

# Make large deletions to the genome
def large_deletion(ind,n,mut_array,measure_mut=False):
  for i in range(n):
    # length of genome
    L = ind.shape[0]-15
    pos1 = random.randint(0,L-3)
    n_bp = round(3*random.randn()+15)
    pos2 = random.randint(pos1,pos1+n_bp)
    if pos2 > L:
      pos2 = L-2
    ind = np.delete(ind,np.arange(pos1,pos2+1))
    if measure_mut == True:
      mut_array[0] += 1
  # print("Large Deletion",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nLarge Deletion "+str(ind.shape))
  return ind,mut_array

# Make inversions of genome
def inversion(ind,n,mut_array,measure_mut=False):
  for i in range(n):
    # length of genome
    L = ind.shape[0]-15
    pos1 = random.randint(0,L-3)
    n_bp = round(3*random.randn()+15)
    pos2 = random.randint(pos1,pos1+n_bp)
    if pos2 > L:
      pos2 = L-2
    ind[pos1:pos2+1] = np.flip(ind[pos1:pos2+1])
    if measure_mut == True:
      mut_array[1] += 1
  # print("Inversion",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nInversion "+str(ind.shape))
  return ind,mut_array

# Create duplicates of section of gene
def duplication(ind,n,mut_array,measure_mut=False):
  for i in range(n):
    # length of genome
    L = ind.shape[0]-15
    pos1 = random.randint(0,L-3)
    n_bp = round(3*random.randn()+15)
    pos2 = random.randint(pos1,pos1+n_bp)
    if pos2 > L:
      pos2 = L-2
    # pos3 is calculated such that it falls before or after duplicating genome,
    # but never in between pos1 and pos2
    print(pos1,pos2, [random.randint(pos1+1),random.randint(pos2,L+1)])
    pos3 = random.choice([random.randint(pos1+1),random.randint(pos2,L+1)])
    if pos3 == L-1:
      ind = np.hstack((ind,ind[pos1:pos2+1]))
    else:
      ind = np.insert(ind,pos3-1,ind[pos1:pos2+1])
    if measure_mut == True:
      mut_array[2] += 1
  # print("Duplication",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nDuplication "+str(ind.shape))
  return ind,mut_array

# Make translocations in genome
def translocation(ind, n,mut_array,measure_mut=False):
  for i in range(n):
    # length of genome
    L = ind.shape[0]-15
    pos1 = random.randint(0,L-3) # -1 one here because I don't want the 2 positions to be the same later
    n_bp = round(3*random.randn()+15) # only taking a maximum of 20 bp translocation -- sigma * np.random.randn(...) + mu
    pos2 = random.randint(pos1,pos1+n_bp)
    
    if pos2 > L:
      pos2 = L-2
    print("translocation1",L,pos1,pos2)
    print("translocation",L,pos1,pos2, [random.randint(pos1+1),random.randint(pos2,L+1)])

    pos3 = random.choice([random.randint(pos1+1),random.randint(pos2,L+1)])
    # we want to preserve the position number when deleting and translocating
    # so, we will approach this in two ways:
    # 1) when insertion position is less than deletion position
    # 2) when insertion position is more than deletion position
    trans = ind[pos1:pos2+1]
    if pos3 < pos1:
      ind = np.delete(ind,np.arange(pos1,pos2+1))
      if pos3 == L-1:
        ind = np.hstack((ind,trans))
      else:
        ind = np.insert(ind,pos3,trans)
    else:
      if pos3 == L-1:
        ind = np.hstack((ind,trans))
      else:
        ind = np.insert(ind,pos3,trans)
      ind = np.delete(ind,np.arange(pos1,pos2+1))
    if measure_mut == True:
      mut_array[3] += 1
  # print("Translocation",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nTranslocation "+str(ind.shape))

  return ind,mut_array

# Insert point mutations
def point(ind,n,u,mut_array,measure_mut=False):
  # length of genome
  L = ind.shape[0]
  pos = random.randint(L,size=n)
  mut_prob = random.rand(n)
  mut_pos = mut_prob < u
  for i in range(n):
    if mut_pos[i] == True:
      if measure_mut == True:
        mut_array[4] += 1
      if ind[pos[i]] == 1:
        ind[pos[i]] = 0
      else:
        ind[pos[i]] = 1

  # print("Point Mutation",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nPoint Mutation "+str(ind.shape))
  return ind,mut_array

# Small insertions in genome
def small_insert(ind,n,u,mut_array,measure_mut=False):
  L = ind.shape[0]
  for i in range(n):
    if random.rand() < u:
      if measure_mut == True:
        mut_array[5] += 1
      pos = random.randint(L)
      n_bp = random.randint(1,6)
      insert_seq = random.choice([0, 1], size=n_bp)
      ind = np.insert(ind,pos,insert_seq)
  # print("Small Insertion",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nSmall Insertion "+str(ind.shape))
  return ind,mut_array

# Small deletions in genome
def small_deletion(ind,n,u,mut_array,measure_mut=False):
  L = ind.shape[0]
  pos = random.randint(L,size=n)
  pos = np.sort(pos)[::-1]
  for i in range(n):
    if random.rand() < u:
      if measure_mut == True:
        mut_array[6] += 1
      p = pos[i]
      n_bp = random.randint(1,6)
      if p + n_bp > ind.shape[0]:
        n_bp = ind.shape[0] - p
      ind = np.delete(ind,np.arange(p,p+n_bp))
  # print("Small Deletion",ind.shape)
  with open('console.log', 'a') as f:
    f.write("\nSmall Deletion"+str(ind.shape))
  return ind,mut_array

"""# Run"""

def bevol_run(n_generations, k, population,mut_array): 
  avg_genome_size = 0
  for ind in population.individuals:
      avg_genome_size += ind.genome_size
  avg_genome_size /= population.n_individuals
  genome_size = [avg_genome_size]

  for t in range(n_generations):
    # Genome decoding and evaluation
    print("\nGENERATION ",t)
    with open('console.log', 'a') as f:
      f.write("\n\nGENERATION "+str(t)+"\n\n")
    print(f'Entering Decode_Evaluate...')
    g_list = Decode_Evaluate(population)

    # Selection -- uses single k parameter
    Selection(population, g_list, k)
    # Mutation -- uses mutation rate parameters
    mut_array = Mutation(population,mut_array)

    # Return genome size
    avg_genome_size = 0
    for ind in population.individuals:
      avg_genome_size += ind.genome_size
    avg_genome_size /= population.n_individuals
    genome_size.append(avg_genome_size)
    
  return genome_size,mut_array

def copyPop(pop):
  n = pop.n_individuals
  pop2 = Population(n)

  individuals = []
  for ind in pop.individuals:
    ind2 = Individual(ind.genome)
    ind2.genome_size = ind.genome_size
    individuals.append(ind2)
  
  pop2.individuals = individuals.copy()
  return pop2

def main():
  start_time = time.time()

  # Initialize class object
  print(f'Entering Initialize...')
  population = Initialize(population_size)
  population2 = copyPop(population)
  
  print("first genome", population.individuals[0].genome)
  with open('console.log', 'w') as f:
    f.write("First Genome =".join(str(start)))
  
  # Run simulations
  print(f'Entering bevol_run with k = wildtype...')
  mut_array = np.zeros(7)
  with open('console.log', 'w') as f:
    f.write("~~~~~~~~~~~~~Entering bevol_run with k = wildtype...~~~~~~~~~~~~~~~\n")
  genome_sizes_wildtype,mut_array = bevol_run(n_generations, k_wildtype, population,mut_array)
  mut1_count = mut_array.copy()
  print(f'Entering bevol_run with k = relaxed...')
  mut_array = np.zeros(7)
  with open('console.log', 'a') as f:
    f.write("\n~~~~~~~~~~~~~Entering bevol_run with k = relaxed...~~~~~~~~~~~~~~~\n")
  genome_sizes_relaxed,mut_array = bevol_run(n_generations, k_relaxed, population2,mut_array)
  mut2_count = mut_array.copy()

  # Plot Genome size vs time
  time_steps = np.arange(n_generations+1)
  fig = plt.figure(0)
  plt.title("Genome Size Simulation")
  plt.plot(time_steps,genome_sizes_wildtype, label='k_wildtype')
  plt.plot(time_steps,genome_sizes_relaxed, label='k_relaxed')
  plt.xlabel("Time")
  plt.ylabel("Genome Size")
  plt.legend()
  plt.savefig('testcase_big.png')

  fig1 = plt.subplots(figsize =(12, 8))
  # bar plot
  # Set position of bar on X axis
  barWidth = 0.25
  br1 = np.arange(len(mut1_count))
  br2 = [x + barWidth for x in br1]
  plt.bar(br1, mut1_count, color='r', width=barWidth, label='wildtype')
  plt.bar(br2, mut2_count, color='b', width=barWidth, label='relaxed')
  plt.xlabel('Type',fontweight ='bold', fontsize = 15)
  plt.ylabel('Number of mutations', fontweight ='bold', fontsize = 15)
  plt.xticks([r + barWidth for r in range(len(mut1_count))],['1', '2', '3', '4', '5', '6', '7'])
  plt.savefig('mutations.png')

  plt.show()

  print(f'Total program time = {(time.time()-start_time)/60} min')

if __name__=='__main__':
  random.seed(7)
  # Create a log file for console output
  global f
  f = open("console.log",'w')
  main()
  f.close()




