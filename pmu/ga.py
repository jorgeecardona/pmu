from random import randint, random


class Genome(object):

    def __init__(self, dna=None, mutation_factor=0.95):
        self.dna = dna
        self._mutation_factor = mutation_factor

    def random(self, size):
        self.dna = []
        for i in range(size):
            self.dna.append(randint(0, 1))

    def __eq__(self, other):
        return self.dna == other.dna

    def __ne__(self, other):
        return self.dna != other.dna

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
        self.bests = list(set(self.bests))
        self.bests.sort(lambda x, y: x[1] - y[1])
        self.bests = self.bests[:10]
        ####

        return bests

if __name__ == "__main__":
    import single
