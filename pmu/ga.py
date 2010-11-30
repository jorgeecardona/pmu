from random import randint, random


class Genome(object):

    def __init__(self, dna=None, mutation_factor=0.95):
        self.dna = dna
        self._mutation_factor = mutation_factor

    def random(self, size):
        self.dna = []
        for i in range(size):
            self.dna.append(randint(0, 1))

    def __add__(self, other):
        # Combination.

        # Get dna
        dna_1 = self.dna
        dna_2 = other.dna

        # Point
        point = len(dna_1) / 2

        # New dna
        dna = []
        for i in range(0, point):
            dna.append(dna_1[i])

        for i in range(point, len(dna_1)):
            dna.append(dna_2[i])

        # Mutations.
        for i in range(len(dna_1)):
            if random() > self._mutation_factor:
                dna[i] = 1 - dna[i]

        # Child
        return Genome(dna)


class World(object):
    def __init__(self, fitness, population=10, dna_size=10, mutation_factor=0.9):
        self.fitness = fitness

        self.bests = []

        self.population = []
        for i in range(population):
            gen = Genome(mutation_factor=mutation_factor)
            gen.random(dna_size)
            self.population.append(gen)

    def fitness_cut(self, cut=0.9):
        fitness = {}
        for p in self.population:
            fitness[p] = self.fitness(p)

        cut_point = int(len(self.population) * cut)
        # sort.
        fitness = fitness.items()
        fitness.sort(lambda x, y: x[1] - y[1])
        return [fit for fit in fitness[:cut_point]]

    def new_generation(self, grow_factor=0.99, cut=0.8):

        new_population = []

        bests = self.fitness_cut(cut)
        self.bests += bests
        
        while len(new_population) < int(len(self.population) * grow_factor):

            a = randint(0, len(self.bests) - 1)
            b = randint(0, len(self.bests) - 1)

            a = self.bests[a][0]
            b = self.bests[b][0]

            new_population.append(a + b)
            new_population.append(b + a)

        self.population = new_population

        # Global bests
        self.bests.sort(lambda x, y: x[1] - y[1])
        self.bests = self.bests[:10]
        ####

        return bests

if __name__ == "__main__":
    import pmu

    # Open power system.
    power_system = pmu.PowerSystem.open("/home/jcardona/Downloads/ieee118cdf.txt")

    def fitness(org):

        # Fit
        fit = 0

        power_system.pmu_reset()
        busses = power_system.busses.values()
        n = len(busses)
        locations = [busses[i].number for i in range(n) if org.dna[i] == 1]

        # Pmu number
        fit = len(locations)

        power_system.pmu_location(locations)

        for branch in power_system.branches:
            if branch.measure == pmu.Measure():
                fit += 10

        for bus in power_system.busses.values():
            if bus.measure == pmu.Measure():
                fit += 20

        return fit

    w = World(fitness, population=60, dna_size=118, mutation_factor=0.5)

    for i in range(1000):

        bests = w.new_generation(cut=0.6)

        print "Global: "
        for i in range(5):
            for gen in w.bests[i][0].dna:
                print gen,
            print w.bests[i][1]

        print "Local: "
        for p in bests[:10]:
            for gen in p[0].dna:
                print gen,
            print p[1]

        print "New generation"
