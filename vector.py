# -*- coding: utf-8 -*-
import math
from decimal import Decimal,getcontext

# 全局设置小数点后30位
getcontext().prec = 30

class Vector(object):
    def __init__(self, coordinates):
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple([Decimal(x) for x in coordinates])
            self.dimension = len(self.coordinates)

        except ValueError:
            raise ValueError('The coordinates must be nonempty')

        except TypeError:
            raise TypeError('The coordinates must be an iterable')


    def __getitem__(self,index):
        return Decimal(self.coordinates[index])


    # print时调用的方法
    def __str__(self):
        return 'Vector: {}'.format(self.coordinates)


    def __eq__(self, v):
        return self.coordinates == v.coordinates

    def plus(self, other):
        new_res = [x+y for x,y in zip(self.coordinates,other.coordinates)]
        return Vector(new_res)

    def minus(self, other):
        new_res = [x-y for x,y in zip(self.coordinates,other.coordinates)]
        return Vector(new_res)

    # 常量与向量相乘
    def times_scalar(self, c):
        new_res = [Decimal(c)*x for x in self.coordinates]
        return Vector(new_res)

    # 向量大小 勾股定理
    def xiangliang_val(self):
        res = [x**2 for x in self.coordinates]
        # 使用Decimal模块内置了一个计算开方的函数，返回decimal类型，否则判断平行时会因为精度问题判断错误
        return sum(res).sqrt()

    # 单位向量
    def unit_xiangliang(self):
        try:
            magnitude = self.xiangliang_val()
            return self.times_scalar(Decimal('1.0')/Decimal(magnitude))
        except ZeroDivisionError:
            raise Exception('xiangliang da xiao buneng wei 0')

    # 向量相乘
    def xiangliang_chengfa(self, v):
        new_res = [x*y for x, y in zip(self.coordinates, v.coordinates)]
        return sum(new_res)

    # 向量夹角cos值
    def xiangliang_hudu(self, other,type=''):
        unit_v = self.unit_xiangliang()
        unit_w = other.unit_xiangliang()
        try:
            cos_val = unit_v.xiangliang_chengfa(unit_w)
            hudu = math.acos(cos_val)
            if type == 'jiaodu':
                # 返回角度值
                degree_per_radian = 180./math.pi
                return hudu * degree_per_radian
            # 返回弧度值
            return hudu
        except ZeroDivisionError:
            raise Exception('xiangliang da xiao chengji buneng wei 0')

    # 是否正交，向量乘积（内积）为0
    def zhengjiao(self,v,tolerance=1e-10):
        ji = self.xiangliang_chengfa(v)
        return abs(ji) < tolerance

    # 是否平行
    def pingxing(self,v):
        return self.is_zero() or v.is_zero() or self.xiangliang_hudu(v) == math.pi or self.xiangliang_hudu(v) == 0

    # 是否是零向量
    def is_zero(self,tolerance=1e-10):
        return self.xiangliang_val()<tolerance

    # 计算向量投影
    def touying(self,b):
        try:
            unit_b = b.unit_xiangliang()
            tmp = self.xiangliang_chengfa(unit_b)
            return unit_b.times_scalar(tmp)
        except Exception as e:
            # 基向量为零向量无法标准化
            if str(e) == self.CANNOT_NORMALIZE_ZERO_VECTOR_MSG:
                raise Exception(self.CANNOT_NORMALIZE_ZERO_VECTOR_MSG)
            else:
                raise e

    # 计算v垂直
    def chuizhi(self,b):
        try:
            pingxing = self.touying(b)
            return self.minus(pingxing)
        except Exception as e:
            # 向量与基向量平行，无垂直向量
            if str(e) == self.NO_UNIQUE_PARALLEL_COMPONENT_MSG:
                raise Exception(self.NO_UNIQUE_PARALLEL_COMPONENT_MSG)
            else:
                raise e


    # 向量积
    def xiangliangji(self,w):
        try:
            x1,y1,z1 = self.coordinates
            x2,y2,z2 = w.coordinates
            return Vector([y1*z2-y2*z1,-(x1*z2-x2*z1),x1*y2-x2*y1])
        except Exception as e:
            msg = str(e)
            if msg == 'need more than 2 values to unpack':
                # 如果向量为二维（有两个值）则增加第三个值为0
                a = Vector(self.coordinates+('0',))
                b = Vector(w.coordinates+('0',))
                return a.xiangliangji(b)
            elif (msg == 'too many values to unpack' or msg == 'need more than 1 values to unpack'):
                # 如果向量值超过3个或者少于2个，报错
                raise Exception(self.ONLY_DEFINED_IN_TWO_THREE_DIMS_MSG)
            else:
                raise e

    # 两个向量组成平行四边形的面积
    def pingxingsibianxing_mianji(self,w):
        ji = self.xiangliangji(w)
        return Vector(ji).xiangliang_val()

    # 两个向量组成三角形的面积
    def sanjiaoxing_mianji(self, w):
        ji = self.xiangliangji(w)
        return Vector(ji).xiangliang_val()/Decimal('2.0')


# test = Vector([1,2])
# test1 = Vector([1,2])
# print(test.xiangliangji(test1))

# test = Vector([-8.987,-9.838,5.031])
# test1 = Vector([-4.268,-1.861,-8.866])
# print(test.sanjiaoxing_mianji(test1))
#
# test = Vector([1.5,9.547,3.691])
# test1 = Vector([-6.007,0.124,5.772])
# print(test.sanjiaoxing_mianji(test1))
#
# test = Vector([-7.579,-7.88])
# test2 = Vector([22.737,23.64])
# print(test.pingxing(test2))
# print(test.zhengjiao(test2))
# # print(test.xiangliang_hudu(test2,'jiaodu'))
# test = Vector([-2.029,9.97,4.172])
# test2 = Vector([-9.231,-6.639,-7.245])
# print(test.pingxing(test2))
# print(test.zhengjiao(test2))
#
# test = Vector([-2.328,-7.284,-1.214])
# test2 = Vector([-1.821,1.072,-2.94])
# print(test.pingxing(test2))
# print(test.zhengjiao(test2))
#
# test = Vector([2.118,4.827])
# test2 = Vector([0,0])
# print(test.pingxing(test2))
# print(test.zhengjiao(test2))
