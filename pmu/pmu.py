class Measure(object):
    def __init__(self, items=None):
        self.items = items

    def measure(self):
        if self.items is None:
            return -1
        return len(self.items)

    def __lt__(self, other):
        return self.measure() < other.measure()

    def __le__(self, other):
        return self.measure() <= other.measure()

    def __gt__(self, other):
        return self.measure() > other.measure()

    def __ge__(self, other):
        return self.measure() >= other.measure()

    def __eq__(self, other):
        return self.measure() == other.measure()

    def __ne__(self, other):
        return self.measure() != other.measure()

    def __add__(self, other):
        if isinstance(other, Measure):
            return Measure(self.items.union(other.items))

        elif isinstance(other, Branch):
            return Measure(self.items.union(set([other])))


class Bus(object):
    def __init__(self, number, name=None):
        self.number = number
        if name is None:
            name = "Bus %d" % (self.number, )
        self.name = name
        self.branches = []
        self.measure = Measure()

    def _add_branch(self, branch):
        if (branch._a != self) and (branch._b != self):
            raise Exception("Bus is not connected to this branch.")

        if branch in self.branches:
            raise Exception("Branch already connected.")

        self.branches.append(branch)

    def _del_branch(self, branch):
        i = self.branches.index(branch)
        self.branches.pop(i)

    def __repr__(self):
        return '<Bus number="%(number)d" name="%(name)s">' % {
            'number': self.number,
            'name': self.name}

    def _expand_measure(self, measure):
        if Measure() < self.measure < measure:
            # If actual measure is better don't do anything
            return True

        # Set measure
        self.measure = measure

        # Expand measures to neighbours
        for bus in self.neighbours():
            branch = self._branch_with(bus)
            if branch.measure > Measure():
                bus._expand_measure(self.measure + branch.measure + branch)
            elif bus.measure > Measure():
                branch._expand_measure(self.measure + bus.measure + branch)

    def _branch_with(self, bus):
        for branch in self.branches:
            if bus == branch._other(self):
                return branch

    def neighbours(self, level=1):
        # Search neighbours in a level fashion
        # 0-level is the self.
        # 1-level are the normal neighbours
        # i-level are the busses reached only by n-steps

        levels = {}
        levels[0] = set([self])

        for i in range(1, level + 1):
            # Previous busses
            busses = levels[i - 1]
            levels[i] = set()
            for bus in busses:
                more_n = [branch._other(bus) for branch in bus.branches]
                levels[i] = levels[i].union(set(more_n))

            for j in range(i):
                levels[i] -= levels[j]

        return levels[level]


class Branch(object):
    def __init__(self, a, b):
        self._a = a
        self._b = b

        # Addd to branches lists
        self._a._add_branch(self)
        self._b._add_branch(self)

        # Measure.
        self.measure = Measure()

    def disconnect(self):
        self._a._del_branch(self)
        self._b._del_branch(self)
        self._a = None
        self._b = None

    def __repr__(self):
        return '<Bus terminal_a="%(a)s" terminal_b="%(b)s">' % {
            'a': self._a,
            'b': self._b}

    def _expand_measure(self, measure):
        if Measure() < self.measure < measure:
            return True

        self.measure = measure

        if self._a.measure > Measure() and self._b.measure > Measure():
            # Both terminal have measures.
            return True
        elif self._a.measure > Measure() and self._b.measure < Measure(set()):
            # Measure in a but not in b.
            # Expand measure to b.
            self._b._expand_measure(self._a.measure + self.measure + self)
        elif self._b.measure > Measure() and self._a.measure < Measure(set()):
            # Measure in a but not in a.
            # Expand measure to a.
            self._a._expand_measure(self._b.measure + self.measure + self)

        terminal_a = 0
        all_measures_a = Measure(set())
        for branch in self._a.branches:
            if branch.measure > Measure():
                terminal_a += 1
                all_measures_a += branch.measure

        terminal_b = 0
        all_measures_b = Measure(set())
        for branch in self._b.branches:
            if branch.measure > Measure():
                terminal_b += 1
                all_measures_b += branch.measure

        if terminal_a + 1 >= len(self._a.neighbours()):
            for branch in self._a.branches:
                branch._expand_measure(all_measures_a)

        if terminal_b + 1 >= len(self._b.neighbours()):
            for branch in self._b.branches:
                branch._expand_measure(all_measures_b)

    def _other(self, bus):
        if bus == self._a:
            return self._b
        elif bus == self._b:
            return self._a
        raise Exception("Bus not found.")


class PowerSystem(object):
    def __init__(self):
        self.busses = {}
        self.branches = []

    def _add_bus(self, bus):
        self.busses[bus.number] = bus

    def _locate_one_pmu(self, i):
        self.busses[i]._expand_measure(Measure(set()))
        for branch in self.busses[i].branches:
            branch._expand_measure(Measure(set()))

    def pmu_location(self, locations):
        for l in locations:
            self._locate_one_pmu(l)

    def pmu_reset(self):
        for branch in self.branches:
            branch.measure = Measure()

        for bus in self.busses:
            self.busses[bus].measure = Measure()

    def _del_bus(self, bus):
        # Delete branches
        for branch in bus.branches:
            branch.disconnect()
            i = self.branches.index(branch)
            self.branches.pop(i)
            del branch

        # Delete from busses list
        for key in self.busses:
            if self.busses[key] == bus:
                break    
        self.busses.pop(key)

        del bus

    @classmethod
    def open(cls, filename):
        # Create PowerSystem
        power_system = cls()

        # Read a file in IEEE format
        fd = open(filename)
        data = fd.read()
        fd.close()

        # Split lines.
        lines = data.split("\n")

        # Search for message "BUS DATA FOLLOWS"
        while "bus data" not in lines[0].lower():
            # Delete first line
            lines.pop(0)
        lines.pop(0)

        # Read busses until -999
        while "-999" not in lines[0].lower():
            # Work with first line
            line = lines.pop(0)

            # Number of the bus
            number = int(line[0:5])

            # Name of the bus
            # name = line[5:15].strip()

            # Add bus
            power_system._add_bus(Bus(number))

        # Search for message "BUS DATA FOLLOWS"
        while "branch data" not in lines[0].lower():
            # Delete first line
            lines.pop(0)
        lines.pop(0)

        while "-999" not in lines[0].lower():
            # Work with first line
            line = lines.pop(0)

            # Number of busses
            number_a = int(line[0:5])
            number_b = int(line[5:10])

            # Connect busses
            branch = Branch(power_system.busses[number_a],
                            power_system.busses[number_b])
            power_system.branches.append(branch)

        return power_system


if __name__ == "__main__":
    print "Test usage of pmu"

    # Open power system.
    power_system = PowerSystem.open("/home/jcardona/Downloads/ieee14cdf.txt")

    power_system.pmu_location([12, 3, 4])

    for i, bus in power_system.busses.items():
        print "No: %02d, Measure: %d" % (bus.number, bus.measure.measure())

    for branch in power_system.branches:
        print "A: %02d B: %02d Measure: %d" % (branch._a.number, branch._b.number, branch.measure.measure())
