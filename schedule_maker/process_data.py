import numpy as np
from functools import cmp_to_key


class GFG:
    def __init__(self, graph):

        self.graph = graph
        self.ppl = len(graph)
        self.friends = len(graph[0])

    def bpm(self, u, matchR, seen):
        for v in range(self.friends):
            if self.graph[u][v] and seen[v] == False:

                seen[v] = True

                if matchR[v] == -1 or self.bpm(matchR[v],
                                               matchR, seen):
                    matchR[v] = u
                    return True
        return False

    def maxBPM(self):

        matchR = [-1] * self.friends

        result = 0
        for i in range(self.ppl):

            seen = [False] * self.friends

            if self.bpm(i, matchR, seen):
                result += 1
        return result, np.array(matchR)


def create_classes(results):
    class pair:
        def __init__(self, students):
            self.students = students
            self.male, self.female, self.islamic, self.behavior = 0, 0, 0, 0
            for student in self.students:
                if results[student][4] == 'M':
                    self.male += 1
                else:
                    self.female += 1
                self.islamic += results[student][2]
                self.behavior += results[student][3]

        def get_student(self, student):
            student_object = results[self.students[student]]
            return {'id': student_object[-1], 'gender': student_object[4], 'islamic': student_object[2],
                    'behavior': student_object[3]}

        def __str__(self):
            return f"Students: {self.students}, Males: {self.male}, Females: {self.female}, Islamic: {self.islamic}, Behavior: {self.behavior}"

    class classroom:
        def __init__(self):
            self.students = []
            self.males = 0
            self.females = 0
            self.islamic = 0
            self.behavior = 0

        def __str__(self):
            return f'{self.students}, {self.males}, {self.females}, {self.islamic}, {self.behavior}'

        def add_students(self, new_student):
            self.students.append(new_student)
            self.males += 1 if new_student['gender'] == 'M' else 0
            self.females += 1 if new_student['gender'] == 'F' else 0
            self.islamic += new_student['islamic']
            self.behavior += new_student['behavior']

    m = len(results)
    islamic, behavior, male, female = 0, 0, 0, 0

    for _ in range(m):
        for index in range(5, 10):
            if results[_][index] == _ + 1:
                if index == 5:
                    results[_][index] = results[_][index + 1]
                else:
                    results[_][index] = results[_][index - 1]
        islamic += 1 if results[_][2] == 1 else 0
        behavior += 1 if results[_][3] == 1 else 0
        if results[_][4] == 'M':
            male += 1
        else:
            female += 1

    students_per_class = m // 10

    # Find mutual friends between the students
    mutuals = {}
    mutual_pairs = []
    used = []
    _ = 0
    while _ < m:
        for i in results[_][5:-1]:
            i -= 1
            if _ + 1 in results[i][5:-1] and _ not in used and i not in used:
                mutuals[_], mutuals[i] = i, _
                new_pair = pair([_, i])
                mutual_pairs.append(new_pair)
                used.append(_)
                used.append(i)
                break
        _ += 1

    adjacency_matrix = np.zeros([m, m])

    # Edits the adjacency matrix so that each student has value 1 for their friends
    for i in range(m):
        if i in used:
            adjacency_matrix[i, mutuals[i]] = 1
            continue
        for j in range(5, 10):
            if j - 1 in used:
                continue
            adjacency_matrix[i, results[i][j] - 1] = 1

    g = GFG(adjacency_matrix)

    maximum_matchings, matchings = g.maxBPM()


    normal_pairs = []
    lookup_pairs = {}
    alone = []

    for _ in range(len(matchings)):
        if matchings[_] == _:
            alone.append(_)
            continue

        new_pair = pair([_, matchings[_]])
        normal_pairs.append(new_pair)
        lookup_pairs[new_pair.students[0]] = new_pair

    class_size = (male + female) // students_per_class

    values = lookup_pairs.copy()
    ordered_pairs = []
    speciai_cases = []
    while len(values) > 0:
        index = list(values.keys())[0]
        to_add = values[index]
        del values[index]

        if to_add.students[1] == -1:
            speciai_cases.append(to_add)
        else:
            ordered_pairs.append(to_add)
            last_student = to_add.students[1]
            while True:
                try:
                    to_add = values[last_student]
                except KeyError:
                    break

                del values[last_student]
                if to_add.students[1] == -1:
                    speciai_cases.append(to_add)
                    break
                ordered_pairs.append(to_add)
                last_student = to_add.students[1]

    ordered_segments = []
    last = 0
    segment = []
    for x in ordered_pairs:
        if x.students[0] != last:
            ordered_segments.append(segment)
            segment = []
        segment.append(x)
        last = x.students[1]


    def get_distribution(students):
        males, females, total_islamic, total_behavior = 0, 0, 0, 0
        for student in students:
            if student['gender'] == 'M':
                males += 1
            else:
                females += 1
            total_islamic += student['islamic']
            total_behavior += student['behavior']
        return males, females, total_islamic, total_behavior

    def get_cost(students):
        if len(students) == 0:
            return 0.0, []
        males, females, total_islamic, total_behavior = get_distribution(students)
        cost = (2 / 3 * abs(males - females) + 1 / 3 * (total_islamic + total_behavior)) / (males + females)
        return cost, [males, females, total_islamic, total_islamic]

    # Custom key to sort the scores based on cost
    def sort_by_cost(a, b):
        if a[0] >= b[0]:
            return 1
        return -1

    def split_equally(students):
        cost_parent, details_parent = get_cost(students)
        if cost_parent <= 0.3 or len(students) < 6:
            return [students], []
        else:
            min_size = 2
            cyclic_array = students[1:] + students
            length = len(students)
            scores = []
            left = 0
            right = length
            while right != len(cyclic_array):
                while right - left != min_size:
                    index = [left, right]
                    remaining_array = []
                    for student in students:
                        if student not in cyclic_array[left:right]:
                            remaining_array.append(student)
                    cost, details = get_cost(cyclic_array[left:right])
                    cost_other, details_other = get_cost(remaining_array)
                    scores.append(
                        [(cost * len(cyclic_array[left:right]) + cost_other * len(remaining_array)) / length, index,
                         details, details_other])
                    right -= 1
                left += 1
                right = length + left
            scores.sort(key=cmp_to_key(sort_by_cost))
            lowest_cost = scores[0][0]
            to_consider = []
            for score in scores:
                if score[0] == lowest_cost:
                    to_consider.append(score)
                else:
                    break
            current_best, current_best_length_diff = None, None

            for score in to_consider:
                indicies = score[1]
                score_diff_between_lengths = abs(
                    (indicies[1] - indicies[0]) - (len(students) - (indicies[1] - indicies[0])))
                if current_best is None or score_diff_between_lengths < current_best_length_diff:
                    current_best, current_best_length_diff = score, score_diff_between_lengths

            best_split = current_best
            if best_split[0] > cost_parent and len(students) <= students_per_class:
                return [students], []
            left, right = best_split[1][0], best_split[1][1]
            array_found = cyclic_array[left:right]
            array_remaining = []
            for student in students:
                if student not in array_found:
                    array_remaining.append(student)
            if len(array_remaining) == 0:
                return [students], []

            return [array_found, array_remaining], [cyclic_array[best_split[1][0] - 1]]

    total = 0
    split_segments = []
    students_with_no_friends = []
    for s in ordered_segments:
        s_students = [x.get_student(0) for x in s]
        if len(s_students) < 6:
            total += len(s_students)
            if len(s_students) == 1:
                alone.append(s_students[0])

            split_segments.append(s_students)
            continue
        if s[0].students[0] != s[-1].students[1]:
            students_with_no_friends.append(s[-1].get_student(0))
        segments, no_friends = split_equally(s_students)
        for student_alone in no_friends:
            if student_alone not in students_with_no_friends:
                students_with_no_friends.append(student_alone)

        for x in segments:
            total += len(x)
            split_segments.append(x)

    single_people = []
    for x in speciai_cases:
        single_people.append(x.get_student(0))
        split_segments.append([x.get_student(0)])

    split_segments.extend(single_people)

    def sort_based_on_length(a, b):
        if len(a) <= len(b):
            return 1
        return -1

    split_segments.sort(key=cmp_to_key(sort_based_on_length))

    classes = [classroom() for _ in range(class_size)]
    filled_classes = []

    used = 0

    for i in range(len(split_segments)):
        if i >= class_size:
            break
        for student in split_segments[0]:
            used += 1
            classes[i].add_students(student)
        del split_segments[0]

    while len(classes) != 0 and len(split_segments) != 0:
        i = 0
        while i < len(classes):
            students_required = students_per_class - len(classes[i].students)
            for x in range(len(split_segments)):
                if type(split_segments[x]) is dict:
                    split_segments[x] = [split_segments[x]]
                if len(split_segments[x]) <= students_required:
                    for student in split_segments[x]:
                        used += 1

                        classes[i].add_students(student)
                    students_required -= len(split_segments[x])
                    del split_segments[x]
                    break
            if students_required == 0:
                filled_classes.append(classes[i])
                del classes[i]
                i -= 1
            i += 1

    return filled_classes, students_with_no_friends+alone, {'Males': male, 'Females': female, 'Islamic Students': islamic, 'Behavioral Students': behavior}

