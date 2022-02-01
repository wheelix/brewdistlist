"""Calculate the Brew edit distance of two strings."""

# pylint: disable=superfluous-parens, too-many-locals, too-many-boolean-expressions

# Copyright (C) 2017, 2018 David H. Gutteridge.
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.

from collections import namedtuple
import numbers
import sys
from functools import lru_cache

# Public symbols
__all__ = ("distance", "BrewDistanceException")
__author__ = "David H. Gutteridge"
__version__ = "1.0.1"


class BrewDistanceException(Exception):
    """Brew-Distance-specific exception used with argument validation."""

    pass

# Traceback structure
_Traceback = namedtuple("_Traceback", "cost move traceback")


def _best(sub_move, ins_move, del_move):
    """Determine the optimum edit."""
    (increment, move1, traceback1) = sub_move
    cost_with_sub = increment + traceback1.cost

    (increment, move2, traceback2) = ins_move
    cost_with_ins = increment + traceback2.cost

    (increment, move3, traceback3) = del_move
    cost_with_del = increment + traceback3.cost

    best_cost = cost_with_sub
    move = move1
    traceback = traceback1

    if cost_with_ins < best_cost:
        best_cost = cost_with_ins
        move = move2
        traceback = traceback2

    if cost_with_del < best_cost:
        best_cost = cost_with_del
        move = move3
        traceback = traceback3

    # This is predicated on match having a lower cost than other
    # operations, and so doesn't necessarily work if that doesn't hold.
    if best_cost == traceback.cost:
        move = "MATCH"

    return _Traceback(best_cost, move, traceback)


def _edit_path(string1, string2, cost, flexibleSubst=False):
    """Determine the transformations required to make the first string the same as the second."""
    list1 = list(string1)
    list2 = list(string2)
    len1 = len(list1)
    len2 = len(list2)
    (match_cost, ins_cost, del_cost, subst_cost) = cost
    distances = dict()
    distances[0, 0] = _Traceback(0, "INITIAL", None)

    # Deletions
    for i in range(0, len1):
        so_far = distances[i, 0].cost
        distances[i + 1, 0] = _Traceback(so_far + del_cost, "DEL", distances[i, 0])

    # Insertions
    for j in range(0, len2):
        so_far = distances[0, j].cost
        distances[0, j + 1] = _Traceback(so_far + ins_cost, "INS", distances[0, j])

    # Substitutions
    for i in range(0, len1):
        for j in range(0, len2):
            if list1[i] == list2[j]:
                subst = match_cost
            else:
                subst = _flexible_substitution_cost(list1[i], list2[j]) if flexibleSubst else subst_cost

            distances[i + 1, j + 1] = _best(_Traceback(subst, "SUBST", distances[i, j]),
                                            _Traceback(ins_cost, "INS", distances[i + 1, j]),
                                            _Traceback(del_cost, "DEL", distances[i, j + 1]))

    return distances[len1, len2]


@lru_cache(maxsize=32)
def _flexible_substitution_cost(string1, string2):
    string1 = str.lower(string1)
    string2 = str.lower(string2)
    dist = distance(string1, string2, output="distance")
    cost = dist / max(len(string1), len(string2))
    return cost

def _list_edits(raw_edits):
    """Create a list of the edits made."""
    just_edits = list()

    # (We don't bother reporting the initial match, as that's pointless.)
    while raw_edits.traceback != None:
        just_edits.insert(0, raw_edits.move)
        raw_edits = raw_edits.traceback

    return just_edits

def distance(string1, string2, output="both", cost=(0, 1, 1, 1), flexibleSubst=False):
    """Determine the Brew edit distance between two strings.

    string1 is the string (or list of strings) to be transformed.

    string2 is the transformation target.

    Optional output is a string containing "distance", "edits", or
    "both", which determine results output, see below.

    Optional cost is a four element tuple of numbers used to adjust
    the costs of matches, insertions, deletions, and substitutions.
    (It is not recommended that match costs be adjusted: the algorithm
    is predicated on match having a lower cost than other operations.)

    The results vary depending on the output option:
        "distance": provides the edit distance as a number.
        "edits": provides an array with the list of edit actions.
        "both: provides a tuple containing the output of both
        previous options.
    """
#    if sys.hexversion >= 0x03000000:
#        if not isinstance(string1, str) or not isinstance(string2, str):
#            raise BrewDistanceException("Brew-Distance: non-string input supplied.")
#    else:
#        if not isinstance(string1, basestring) or not isinstance(string2, basestring):
#            raise BrewDistanceException("Brew-Distance: non-string input supplied.")

#        if not isinstance(string1, unicode):
#            string1 = string1.decode("utf-8")

#        if not isinstance(string2, unicode):
#            string2 = string2.decode("utf-8")

    if output != "both" and output != "distance" and output != "edits":
        raise BrewDistanceException("Brew-Distance: invalid output parameter supplied.")
    elif (not isinstance(cost, tuple) or len(cost) != 4 or
          not isinstance(cost[0], numbers.Real) or not isinstance(cost[1], numbers.Real) or
          not isinstance(cost[2], numbers.Real) or not isinstance(cost[3], numbers.Real)):
        raise BrewDistanceException("Brew-Distance: invalid cost parameter supplied.")
    else:
        results = _edit_path(string1, string2, cost, flexibleSubst)

        if output == "distance":
            return results[0]
        elif output == "edits":
            return _list_edits(results, flexibleSubst)
        else:
            return (results[0], _list_edits(results))

if __name__ == "__main__":
    #local path
    directory = ""

    file = open(directory + "titel.txt", "r")
    filenames= file.read().split("\n")
    file.close()
    i = 0
    while i < len(filenames):
        file = open(directory + filenames[i], "r")
        transkriptOrig = file.read().split("\n\n")
        file.close()
        i += 1
        file = open(directory + filenames[i], "r")
        transkriptKorr = file.read().split("\n\n")
        file.close()
        i += 1
        #print(str(distance(transkriptOrig, transkriptKorr, "both", flexibleSubst=True)))
        turntake=namedtuple(
            'turntake',
            'who, what, when'
        )
        del transkriptOrig[0]
        del transkriptKorr[0]
        for lineKorr, lineOrig in zip(transkriptKorr,transkriptOrig):
            if (lineKorr[0] == "A" or lineKorr[0] == "B"):

                turntakeKorr = turntake(lineKorr[0:1],
                                        lineKorr[1:-1],
                                        "")
                turntakeOrig = turntake(lineOrig[0:1],
                                        lineOrig[1:-1].split("#")[0],
                                        lineOrig[1:-1].split("#")[1])
                print(lineOrig)
                print(str(distance(turntakeKorr.who, turntakeOrig.who, "both", flexibleSubst=True)))
                print(str(distance(turntakeKorr.what.split(), turntakeOrig.what.split(), "both", flexibleSubst=True)))
                print(str(distance(turntakeKorr.when, turntakeOrig.when, "both", flexibleSubst=False)))




 #   print(str(distance(["123", "234"], ["123", "abc", "233"], "both", flexibleSubst=False)))
  #  print(str(distance(["123", "234"], ["123", "233", "abc"], "both", flexibleSubst=False))) # yields counter-intuitive result
   # print(str(distance(["123", "234"], ["123", "abc", "233"], "both", flexibleSubst=True)))
    #print(str(distance(["123", "234"], ["123", "233", "abc"], "both", flexibleSubst=True)))