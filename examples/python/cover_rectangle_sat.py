# Copyright 2010-2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Fill a 72x37 rectangle by a minimum number of non-overlapping squares."""

from __future__ import print_function
from __future__ import division

from ortools.sat.python import cp_model


def cover_rectangle(num_squares):
    """Try to fill the rectangle with a given number of squares."""
    size_x = 72
    size_y = 37

    model = cp_model.CpModel()

    areas = []
    sizes = []
    x_intervals = []
    y_intervals = []
    sxs = []
    sys = []

    for i in range(num_squares):
        size = model.NewIntVar(1, size_y, 'size_%i' % i)
        startx = model.NewIntVar(0, size_x, 'sx_%i' % i)
        endx = model.NewIntVar(0, size_x, 'ex_%i' % i)
        starty = model.NewIntVar(0, size_y, 'sy_%i' % i)
        endy = model.NewIntVar(0, size_y, 'ey_%i' % i)

        interval_x = model.NewIntervalVar(startx, size, endx, 'ix_%i' % i)
        interval_y = model.NewIntervalVar(starty, size, endy, 'iy_%i' % i)

        area = model.NewIntVar(1, size_y * size_y, 'area_%i' % i)
        model.AddProdEquality(area, [size, size])

        areas.append(area)
        x_intervals.append(interval_x)
        y_intervals.append(interval_y)
        sizes.append(size)
        sxs.append(startx)
        sys.append(starty)

    model.AddNoOverlap2D(x_intervals, y_intervals)
    model.AddCumulative(x_intervals, sizes, size_y)
    model.AddCumulative(y_intervals, sizes, size_x)

    model.Add(sum(areas) == size_x * size_y)

    # Symmetry breaking 1: size are ordered.
    for i in range(num_squares - 1):
        model.Add(sizes[i] <= sizes[i + 1])

    # Symmetry breaking 2: first square in one quadrant.
    model.Add(sxs[0] < 36)
    model.Add(sys[0] < 19)

    # Creates a solver and solves.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(solver.StatusName(status), solver.WallTime(), 'ms')

    if status == cp_model.FEASIBLE:
        display = [[' ' for _ in range(size_x)] for _ in range(size_y)]
        for i in range(num_squares):
            x = solver.Value(sxs[i])
            y = solver.Value(sys[i])
            s = solver.Value(sizes[i])
            c = format(i, '01x')
            for j in range(s):
                for k in range(s):
                    if display[y + j][x + k] != ' ':
                        print('ERROR between %s and %s' %
                              (display[y + j][x + k], c))
                    display[y + j][x + k] = c

        for line in range(size_y):
            print(' '.join(display[line]))
    return status == cp_model.FEASIBLE


for num in range(1, 15):
    print('Trying with size =', num)
    if cover_rectangle(num):
        break