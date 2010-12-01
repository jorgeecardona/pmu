import pmu
from ga import World

# Open power system.
power_system = pmu.PowerSystem.open("/home/jcardona/Downloads/ieee30cdf.txt")


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

w = World(fitness, population=60, dna_size=30, mutation_factor=0.5)

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
