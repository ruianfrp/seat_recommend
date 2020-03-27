class isPointInRect(object):

    def __int__(self):
        self.__isInRectFlag = False

    def cross_product(self, xp, yp, x1, y1, x2, y2):
        return (x2 - x1) * (yp - y1)-(y2 - y1) * (xp - x1)

    def compute_para(self, xp, yp, xa, ya, xb, yb, xc, yc, xd, yd):
        cross_product_ab = isPointInRect().cross_product(xp, yp, xa, ya, xb, yb)
        cross_product_bc = isPointInRect().cross_product(xp, yp, xb, yb, xc, yc)
        cross_product_cd = isPointInRect().cross_product(xp, yp, xc, yc, xd, yd)
        cross_product_da = isPointInRect().cross_product(xp, yp, xd, yd, xa, ya)
        return cross_product_ab,cross_product_bc,cross_product_cd,cross_product_da

    def is_in_rect(self, aa, bb, cc, dd):
        if (aa > 0 and bb > 0 and cc > 0 and dd > 0) or (aa < 0 and bb < 0 and cc < 0 and dd < 0):
            print("This point is in the rectangle.")
            self.__isInRectFlag = True
        else:
            print("This point is not in the rectangle.")
            self.__isInRectFlag = False

        return self.__isInRectFlag


if __name__ == '__main__':
    aa, bb, cc, dd = isPointInRect().compute_para(600, 550, 508, 451, 730, 470, 718, 615, 495, 596)
    print(isPointInRect().is_in_rect(aa, bb, cc, dd))
