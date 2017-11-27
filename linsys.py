# -*- coding: utf-8 -*-
from decimal import Decimal, getcontext
from copy import deepcopy

from vector import Vector
from plane import Plane

getcontext().prec = 30


class LinearSystem(object):

    ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG = 'All planes in the system should live in the same dimension'
    NO_SOLUTIONS_MSG = 'No solutions'
    INF_SOLUTIONS_MSG = 'Infinitely many solutions'

    def __init__(self, planes):
        try:
            d = planes[0].dimension
            for p in planes:
                assert p.dimension == d

            self.planes = planes
            self.dimension = d

        except AssertionError:
            raise Exception(self.ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG)


    def swap_rows(self, row1, row2):
        pass # add your code here
        # tmp = self.planes[row1]
        # self.planes[row1] = self.planes[row2]
        # self.planes[row2] = tmp
        # return self.planes

        self[row1],self[row2]= self[row2],self[row1]


    def multiply_coefficient_and_row(self, coefficient, row):
        pass # add your code here
        n = self.planes[row].normal_vector
        k = self.planes[row].constant_term
        new_normal_vector = n.times_scalar(coefficient)
        new_constant_term = k * coefficient
        self[row] = Plane(normal_vector=new_normal_vector,constant_term=new_constant_term)


    def add_multiple_times_row_to_row(self, coefficient, row_to_add, row_to_be_added_to):
        pass # add your code here
        n1 = self.planes[row_to_add].normal_vector
        k1 = self.planes[row_to_add].constant_term
        n2 = self.planes[row_to_be_added_to].normal_vector
        k2 = self.planes[row_to_be_added_to].constant_term

        new_normal_vector = n1.times_scalar(coefficient).plus(n2)
        new_constant_term = (k1 * coefficient) + k2
        self[row_to_be_added_to] = Plane(normal_vector=new_normal_vector,constant_term=new_constant_term)

        # normal_vector = self.planes[row_to_add].normal_vector.times_scalar(coefficient)
        # constant_term = self.planes[row_to_add].constant_term * coefficient
        # new_plane = Plane(normal_vector,constant_term)
        # self.planes[row_to_be_added_to].normal_vector = new_plane.normal_vector.plus(self.planes[row_to_be_added_to].normal_vector)
        # self.planes[row_to_be_added_to].constant_term += new_plane.constant_term
        # # 重新设置选点
        # self.planes[row_to_be_added_to].set_basepoint()
        #
        # return self.planes[row_to_be_added_to]


    # 计算主编量索引，每行首项变量索引l列表
    def indices_of_first_nonzero_terms_in_each_row(self):
        num_equations = len(self)
        num_variables = self.dimension

        indices = [-1] * num_equations

        for i,p in enumerate(self.planes):
            try:
                indices[i] = p.first_nonzero_index(p.normal_vector)
            except Exception as e:
                if str(e) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                    continue
                else:
                    raise e

        return indices


    def __len__(self):
        return len(self.planes)


    def __getitem__(self, i):
        return self.planes[i]


    def __setitem__(self, i, x):
        try:
            assert x.dimension == self.dimension
            self.planes[i] = x

        except AssertionError:
            raise Exception(self.ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG)


    def __str__(self):
        ret = 'Linear System:\n'
        temp = ['Equation {}: {}'.format(i+1,p) for i,p in enumerate(self.planes)]
        ret += '\n'.join(temp)
        return ret

    # 构造三角形状
    def compute_triangular_form(self):
        system = deepcopy(self)

        # 方程数量
        num_equations = len(system)
        # 维度（变量数量）
        num_variables = system.dimension

        j = 0
        for i in range(num_equations):
            while j < num_variables:
                # 第i个方程的第j个变量
                c = MyDecimal(system[i].normal_vector[j])
                if c.is_near_zero():
                    swap_succeeded = system.swap_with_row_below_for_nonzero_coefficient_if_able(i,j)
                    if not swap_succeeded:
                        j += 1
                        continue

                system.clear_coefficients_below(i,j)
                j += 1
                break

        return system

    # 与其它非零行进行行行交换
    def swap_with_row_below_for_nonzero_coefficient_if_able(self,row,col):
        num_equations = len(self)

        for k in range(row+1,num_equations):
            coefficient = MyDecimal(self[k].normal_vector[col])
            if not coefficient.is_near_zero():
                self.swap_rows(row ,k)
                return True

        return False

    # 清除当前方程变量下面所有系数
    def clear_coefficients_below(self,row,col):
        num_equations = len(self)
        beat = MyDecimal(self[row].normal_vector[col])

        for k in range(row + 1, num_equations):
            n = self[k].normal_vector
            gamma = n[col]
            alpha = -gamma/beat
            self.add_multiple_times_row_to_row(alpha,row,k)

    # 构造简化阶梯型（rref）
    def compute_rref(self):
        tf = self.compute_triangular_form()

        num_equations = len(self)
        pivot_indices = tf.indices_of_first_nonzero_terms_in_each_row()

        for i in range(num_equations)[::-1]: #[5,4,3,2,1,0]自下而上处理变量
            j = pivot_indices[i]
            if j<0:
                continue

            tf.scale_row_to_make_coefficient_equal_one(i,j)
            # 清除当前方程当前变量以上的变量
            tf.clear_coefficient_above(i,j)

        return tf

    # 将指定行的指定变量乘以自己系数的倒数，将系数变成1
    def scale_row_to_make_coefficient_equal_one(self,row,col):
        n = self[row].normal_vector
        beta = Decimal('1.0')/n[col]
        self.multiply_coefficient_and_row(beta,row)

    # 从指定行开始自下而上清除变量
    def clear_coefficient_above(self,row,col):
        for k in range(row)[::-1]: #[5,4,3,2,1,0]从本行开始自下而上处理变量
            n = self[k].normal_vector
            alpha = -(n[col])
            self.add_multiple_times_row_to_row(alpha,row,k)

    # 计算方程组的结果
    def compute_solution(self):
        try:
            # return self.do_gaosi_elimination_and_extract_solution()
            return self.do_gaosi_elimination_and_parametrize_solution()
        except Exception as e:
            # if(str(e) == self.NO_SOLUTIONS_MSG or str(e) == self.INF_SOLUTIONS_MSG):
            if(str(e) == self.NO_SOLUTIONS_MSG):
                return str(e)
            else:
                return e

    # def do_gaosi_elimination_and_extract_solution(self):
    def do_gaosi_elimination_and_parametrize_solution(self):
        rref = self.compute_rref()
        # 检查0=k情况
        rref.raise_exception_if_contradictory_equation()
        # rref.raise_exception_if_too_few_pivots()

        # 提取参数化的方向向量
        direction_vectors = rref.extract_direction_vectors_for_parametrization()
        # 提取参数化的基点
        basepoint = rref.extract_basepoint_for_parametrization()
        # print direction_vectors
        # print basepoint

        return Parametrization(basepoint=basepoint,direction_vectors=direction_vectors)


        # num_variables = rref.dimension
        # # 因为已经将变量系数处理为1，所以值就是解
        # solution_coordinates = [rref.planes[i].constant_term for i in range(num_variables)]
        #
        # return Vector(solution_coordinates)

    # 检查是否存在0=k的情况，如果有代表无解
    def raise_exception_if_contradictory_equation(self):
        for p in self.planes:
            try:
                p.first_nonzero_index(p.normal_vector)
            except Exception as e:
                if str(e) == 'No nonzero elements found':
                    constant_term = MyDecimal(p.constant_term)
                    if not constant_term.is_near_zero():
                        raise Exception(self.NO_SOLUTIONS_MSG)
                else:
                    raise e

    # 检查每个方程主元情况，如果主元总数比方程维度少，则表示存在0=0情况，方程有多个解
    def raise_exception_if_too_few_pivots(self):
        pivot_indices = self.indices_of_first_nonzero_terms_in_each_row()
        num_pivots = sum([1 if index>=0 else 0 for index in pivot_indices])
        num_variables = self.dimension

        if num_pivots < num_variables:
            raise Exception(self.INF_SOLUTIONS_MSG)

    def extract_direction_vectors_for_parametrization(self):
        # 方程组维度（即变量个数）
        num_variables = self.dimension
        # 每个方程主元位置列表
        pivot_indices = self.indices_of_first_nonzero_terms_in_each_row()
        free_variables_indices = set(range(num_variables)) - set(pivot_indices) #差值为自由变量的位置列表

        direction_vectors = []

        for free_var in free_variables_indices:
            vector_coords = [0] * num_variables
            vector_coords[free_var] = 1
            for i,p in enumerate(self.planes):
                pivot_var = pivot_indices[i]
                if pivot_var < 0:
                    break
                vector_coords[pivot_var] = -p.normal_vector[free_var]
            direction_vectors.append(Vector(vector_coords))

        return direction_vectors

    def extract_basepoint_for_parametrization(self):
        num_variables = self.dimension
        pivot_indices = self.indices_of_first_nonzero_terms_in_each_row()

        basepoint_coords = [0] * num_variables
        for i,p in enumerate(self.planes):
            pivot_var = pivot_indices[i]
            if pivot_var < 0:
                break
            basepoint_coords[pivot_var] = p.constant_term

        return Vector(basepoint_coords)

class MyDecimal(Decimal):
    def is_near_zero(self, eps=1e-10):
        return abs(self) < eps

class Parametrization(object):
    BASEPT_AND_DIR_VECTORS_MUST_BE_IN_SAME_DIM_MSG = 'The basepoint and direction vectors should all live in the same dimension'

    def __init__(self,basepoint,direction_vectors):
        self.basepoint = basepoint
        self.direction_vectors = direction_vectors
        self.dimension = self.basepoint.dimension

        try:
            for v in direction_vectors:
                assert v.dimension ==  self.dimension
        except AssertionError:
            raise Exception(self.BASEPT_AND_DIR_VECTORS_MUST_BE_IN_SAME_DIM_MSG)

    def __str__(self):
        return str(self.basepoint.dimension)


p1 = Plane(normal_vector=Vector(['0.786','0.786','0.588']), constant_term='-0.714')
p2 = Plane(normal_vector=Vector(['-0.138','-0.138','0.244']), constant_term='0.319')
s = LinearSystem([p1,p2])
print s.compute_solution()

# p1 = Plane(normal_vector=Vector(['8.631','5.112','-1.816']), constant_term='-5.113')
# p2 = Plane(normal_vector=Vector(['4.315','11.132','-5.27']), constant_term='-6.775')
# p3 = Plane(normal_vector=Vector(['-2.158','3.01','-1.727']), constant_term='-0.831')
# s = LinearSystem([p1,p2,p3])
# print s.compute_solution()
#
# p1 = Plane(normal_vector=Vector(['5.262','2.739','-9.878']), constant_term='-3.441')
# p2 = Plane(normal_vector=Vector(['5.111','6.358','7.638']), constant_term='-2.152')
# p3 = Plane(normal_vector=Vector(['2.016','-9.924','-1.367']), constant_term='-9.278')
# p4 = Plane(normal_vector=Vector(['2.167','-13.543','-18.883']), constant_term='-10.567')
# s = LinearSystem([p1,p2,p3,p4])
# print s.compute_solution()