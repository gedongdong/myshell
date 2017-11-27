# -*- coding: utf-8 -*-
from decimal import Decimal, getcontext

from vector import Vector

getcontext().prec = 30


class Plane(object):

    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'

    def __init__(self, normal_vector=None, constant_term=None):
        self.dimension = 3

        if not normal_vector:
            all_zeros = ['0']*self.dimension
            normal_vector = Vector(all_zeros)
        self.normal_vector = normal_vector

        if not constant_term:
            constant_term = Decimal('0')
        self.constant_term = Decimal(constant_term)

        self.set_basepoint()


    def set_basepoint(self):
        try:
            n = self.normal_vector
            c = self.constant_term
            basepoint_coords = ['0']*self.dimension

            initial_index = Plane.first_nonzero_index(n)
            initial_coefficient = n[initial_index]

            basepoint_coords[initial_index] = c/initial_coefficient
            self.basepoint = Vector(basepoint_coords)

        except Exception as e:
            if str(e) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e


    def __str__(self):

        num_decimal_places = 3

        def write_coefficient(coefficient, is_initial_term=False):
            coefficient = round(coefficient, num_decimal_places)
            if coefficient % 1 == 0:
                coefficient = int(coefficient)

            output = ''

            if coefficient < 0:
                output += '-'
            if coefficient > 0 and not is_initial_term:
                output += '+'

            if not is_initial_term:
                output += ' '

            if abs(coefficient) != 1:
                output += '{}'.format(abs(coefficient))

            return output

        n = self.normal_vector

        try:
            initial_index = Plane.first_nonzero_index(n)
            terms = [write_coefficient(n[i], is_initial_term=(i==initial_index)) + 'x_{}'.format(i+1)
                     for i in range(self.dimension) if round(n[i], num_decimal_places) != 0]
            output = ' '.join(terms)

        except Exception as e:
            if str(e) == self.NO_NONZERO_ELTS_FOUND_MSG:
                output = '0'
            else:
                raise e

        constant = round(self.constant_term, num_decimal_places)
        if constant % 1 == 0:
            constant = int(constant)
        output += ' = {}'.format(constant)

        return output


    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not MyDecimal(item).is_near_zero():
                return k
        raise Exception(Plane.NO_NONZERO_ELTS_FOUND_MSG)

    # 两平面是否平行
    def pingxing(self,other):
        n1 = self.normal_vector
        n2 = other.normal_vector
        return n1.pingxing(n2)

    # 两平面是否相等
    def __eq__(self, other):
        if self.normal_vector.is_zero():
            # 如果一个平面法向量为0向量
            if not other.normal_vector.is_zero():
                # 如果另一平面法向量不为零向量，则两平面不相等
                return False,1
            else:
                # 如果另一平面法向量也为零向量，常量差值为0时两平面相等，差值不为0时两平面不相等
                diff = self.constant_term - other.constant_term
                return MyDecimal(diff).is_near_zero()
        elif other.normal_vector.is_zero():
            # 一平面法向量不为0，另一条法向量为0
            return False,2

        # 两平面法向量均不为0
        if not self.pingxing(other):
            return False,3

        x0 = self.basepoint
        y0 = other.basepoint
        basepoint_diff = x0.minus(y0)

        # 如果两个点组成的向量与其中的一个法向量正交，则两平面相等
        n = self.normal_vector
        return basepoint_diff.zhengjiao(n)


class MyDecimal(Decimal):
    def is_near_zero(self, eps=1e-10):
        return abs(self) < eps


# line1 = Plane(normal_vector=Vector(['-0.412','3.806','0.728']),constant_term='-3.46')
# line2 = Plane(normal_vector=Vector(['1.03','-9.515','-1.82']),constant_term='8.65')
# print line1.pingxing(line2)
# print line1==line2
#
# line1 = Plane(normal_vector=Vector(['2.611','5.528','0.283']),constant_term='4.6')
# line2 = Plane(normal_vector=Vector(['7.715','8.306','5.342']),constant_term='3.76')
# print line1.pingxing(line2)
# print line1==line2
#
# line1 = Plane(normal_vector=Vector(['-7.926','8.625','-7.212']),constant_term='-7.952')
# line2 = Plane(normal_vector=Vector(['-2.642','2.875','-2.404']),constant_term='-2.443')
# print line1.pingxing(line2)
# print line1==line2