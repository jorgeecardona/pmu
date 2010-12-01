import pmu
from ga import World

# Filename
filename = path.join(path.dirname(path.abspath(__file__)), "ieee30cdf.txt")
number_of_busses = 30

# Open power system.
power_system = pmu.PowerSystem.open(filename)
busses_keys = power_system.busses.keys()
systems = [power_system]

# Build a set of systems with n-1 branches.
for key in power_system.busses.keys():

    # Add a new system
    systems.append(
        pmu.PowerSystem.open(filename))

    # Delete one of the branches in the last system
    systems[-1]._del_bus(systems[-1].busses[key])


def fitness(org):
    # Fit
    fit = 0

    # This genom has to fit all the systems.
    for power_system in systems:

        # Reset the pmu locations.
        power_system.pmu_reset()
        n = len(busses_keys)

        # Start with a clean locations set
        locations = []
        for i in range(n):
            # If there is a one in the dna, the try to locate a pmu.
            if org.dna[i] == 1:
                key = busses_keys[i]
                # If the branch is up in the system then locate.
                if key in power_system.busses.keys():
                    locations.append(key)

        # Pmu number
        fit += len(locations)

        # Locate pmu.
        power_system.pmu_location(locations)

        for branch in power_system.branches:
            if branch.measure == pmu.Measure():
                fit += 10

        for bus in power_system.busses.values():
            if bus.measure == pmu.Measure():
                fit += 20

    return fit

w = World(fitness,
          population=60,
          dna_size=number_of_busses,
          mutation_factor=0.7)

for i in range(100):

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

print "Finally: "
for p in w.bests:
    for gen in p[0].dna:
        print gen,
    print p[1]
