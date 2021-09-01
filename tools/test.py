import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.patches import Ellipse

def Oval(points):


    # shapes = np.genfromtxt("_data.txt")

    shapes = points

    class CostFunction_circle3:  # from tim
        """Cost function for circle fit (x=[cx,cy,r]. Initialised with points."""

        def __init__(self, pts):
            self.pts = pts

        def f(self, x):
            """Evaluate cost function fitting circle centre (x[0],x[1]) radius x[2]"""
            r2 = np.square(self.pts[0, :] - x[0]) + np.square(self.pts[1, :] - x[1])
            d = np.square(np.sqrt(r2) - x[2])
            return np.sum(d)

    class CostFunction_ellipse3:
        """Cost function for ellipse fit (x=[A B C D E]. Initialised with points."""

        def __init__(self, pts):
            self.pts = pts

        def f(self, x1):
            """Evaluate cost function fitting ellipse"""
            x = self.pts[0, :]
            y = self.pts[1, :]
            x = x[:, np.newaxis]
            y = y[:, np.newaxis]
            x1 = x1[np.newaxis, :]
            D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
            # S = np.dot(D.T,D)
            C = np.zeros([6, 6])
            C[0, 2] = C[2, 0] = 2;
            C[1, 1] = -1
            aa = np.dot(x1, D.T)
            aa = np.dot(aa, D)
            aa = np.dot(aa, x1.T)
            bb = np.dot(x1, C)
            bb = np.dot(bb, x1.T)
            d = aa - bb
            return np.sum(d)

    def solve_ellipse(A, B, C, D, E, F):
        Xc = (B * E - 2 * C * D) / (4 * A * C - B ** 2)
        Yc = (B * D - 2 * A * E) / (4 * A * C - B ** 2)

        FA1 = 2 * (A * Xc ** 2 + C * Yc ** 2 + B * Xc * Yc - F)
        FA2 = np.sqrt((A - C) ** 2 + B ** 2)

        MA = np.sqrt(FA1 / (A + C + FA2))
        SMA = np.sqrt(FA1 / (A + C - FA2)) if A + C - FA2 != 0 else 0

        if B == 0 and F * A < F * C:
            Theta = 0
        elif B == 0 and F * A >= F * C:
            Theta = 90
        elif B != 0 and F * A < F * C:
            alpha = np.arctan((A - C) / B) * 180 / np.pi
            Theta = 0.5 * (-90 - alpha) if alpha < 0 else 0.5 * (90 - alpha)
        else:
            alpha = np.arctan((A - C) / B) * 180 / np.pi
            Theta = 90 + 0.5 * (-90 - alpha) if alpha < 0 else 90 + 0.5 * (90 - alpha)

        if MA < SMA:
            MA, SMA = SMA, MA

        return [Xc, Yc, MA, SMA, Theta]

    # zd 2020/4/12  83-93 from tim
    # Set up a cost function to evaluate how well a circle fits to pts2
    c3 = CostFunction_circle3(shapes)

    # Initialise a 3 element vector to zero (as a start)
    x0 = np.zeros(3)

    # Use Powell's method to fit, starting at x
    res = minimize(c3.f, x0, method='Powell')

    print("Best fit has centre (", res.x[0], ",", res.x[1], ") radius ", res.x[2])

    # plot a circle
    theta = np.arange(0, 2 * np.pi, 0.01)
    x1 = res.x[0] + res.x[2] * np.cos(theta)
    y1 = res.x[1] + res.x[2] * np.sin(theta)

    plt.title("First shape")
    plt.plot(shapes[0, :], shapes[1, :], "o")
    plt.plot(x1, y1)
    plt.show()
    plt.savefig("circles.png")

    # x^2+Axy+By^2+Cx+Dy+E=0
    e3 = CostFunction_ellipse3(shapes)
    x2 = np.array([0.01] * 6, dtype='float64')

    res1 = minimize(e3.f, x2, method='Powell')

    [Xc, Yc, MA, SMA, Theta] = solve_ellipse(res1.x[0], res1.x[1], res1.x[2], res1.x[3], res1.x[4], res1.x[5])

    ell = Ellipse([Xc, Yc], MA * 2, SMA * 2, Theta)

    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
    plt.plot(shapes[0, :], shapes[1, :], "o")
    ax.add_artist(ell)
    ell.set_facecolor("white")
    ell.set_edgecolor("black")
    plt.plot(shapes[0, :], shapes[1, :], "o")

    plt.show()
    plt.savefig("Ellipse.png")



def my_fun(parameters, x_samples, y_samples):
    # 两焦点坐标以及椭圆上的点到两焦点的距离的和作为优化参数
    x_focus_1, y_focus_1, x_focus_2, y_focus_2, sum_of_target_distance_between_edge_and_two_focus = parameters
    # 计算实际距离
    sum_of_actual_distance_between_edge_and_two_focus = \
        ((x_samples - x_focus_1) ** 2 + (y_samples - y_focus_1) ** 2) ** 0.5 + \
        ((x_samples - x_focus_2) ** 2 + (y_samples - y_focus_2) ** 2) ** 0.5

    # print(np.average(sum_of_actual_distance_between_edge_and_two_focus))
    # 返回方差
    return np.sum(((sum_of_actual_distance_between_edge_and_two_focus
                    - sum_of_target_distance_between_edge_and_two_focus) ** 2) / (len(x_samples) - 1))

def fit_ellipse(x_samples, y_samples):
    import scipy.optimize as so
    # 归一化
    vmax = max(np.max(x_samples), np.max(y_samples))
    x_samples = x_samples / vmax
    y_samples = y_samples / vmax
    # 优化
    res_optimized = so.minimize(fun=my_fun, x0=np.array([-0.1, -0.05, 0.1, 0.1, 1.2]), args=(x_samples, y_samples))
    if res_optimized.success:
        print(res_optimized)
        x1_res, y1_res, x2_res, y2_res, l2_res = res_optimized.x
        # 依据优化得到的函数生成椭圆曲线
        # 计算椭圆偏角
        alpha_res = np.arctan((y2_res - y1_res) / (x2_res - x1_res))
        # 计算两焦点之间的距离
        l_ab = ((y2_res - y1_res) ** 2 + (x2_res - x1_res) ** 2) ** 0.5
        # 计算长（短）轴长度
        a_res = l2_res / 2
        # 计算短（长）轴长度
        b_res = ((l2_res / 2) ** 2 - (l_ab / 2) ** 2) ** 0.5

        # 极坐标轴序列
        theta_res = np.linspace(0.0, 6.28, 100)
        # 生成椭圆上的点
        # x_res = a_res * np.cos(theta_res) * np.cos(alpha_res) \
        #         - b_res * np.sin(theta_res) * np.sin(alpha_res)
        # y_res = b_res * np.sin(theta_res) * np.cos(alpha_res) \
        #         + a_res * np.cos(theta_res) * np.sin(alpha_res)
        x_res = x_samples
        y_res = y_samples

        # plt.style.use("one")
        # plt.axes([0.16, 0.15, 0.75, 0.75])
        plt.scatter(x_samples, y_samples,)
                    # color="magenta", marker="+",
                    # zorder=1, s=80, label="samples")
        plt.plot(x_res, y_res, )
                 # color="deepskyblue", zorder=2,
                 # label="fitted curve")
        plt.scatter(np.array([x1_res, x2_res]), np.array([y1_res, y2_res]),)
                    # zorder=3,
                    # color="r", label="focus point")
        plt.xlabel("$x$")
        plt.ylabel("$y$")
        plt.legend()
        vmax = max(np.max(plt.xlim()), np.max(plt.ylim()))
        vmin = min(np.min(plt.xlim()), np.min(plt.ylim()))
        # plt.ylim([1.1 * vmin - 0.1 * vmax, 1.1 * vmax - 0.1 * vmin])
        # plt.xlim([1.25 * vmin - 0.25 * vmax, 1.25 * vmax - 0.25 * vmin])
        # plt.savefig("Figsave/a={:.3f};b={:.3f};theta={:.2f}deg.svg".format(a_res, b_res, alpha_res))
        plt.show()

def Oval1(points):
    theta_samples = np.linspace(0, 20, 100)
    # 椭圆方位角
    alpha_samples = -45.0 / 180.0 * np.pi
    # 长轴长度
    a_samples = 1.0
    # 短轴长度
    b_samples = 2.0

    # 样本x 序列，并叠加正态分布的随机值
    # x_samples = a_samples * np.cos(theta_samples) * np.cos(alpha_samples) \
    #             - b_samples * np.sin(theta_samples) * np.sin(alpha_samples) \
    #             + np.random.randn(100) * 0.05 * a_samples

    # # 样本y 序列 ，并叠加正态分布的随机值
    # y_samples = b_samples * np.sin(theta_samples) * np.cos(alpha_samples) \
    #             + a_samples * np.cos(theta_samples) * np.sin(alpha_samples) \
    #             + np.random.randn(100) * 0.05 * b_samples

    half = int(len(points)/2)
    x_samples = [i[0] for i in points[:half]]
    y_samples = [i[1] for i in points[:half]]
    fit_ellipse(x_samples, y_samples)

def Oval2():
    import numpy as np
    import numpy.linalg as linalg
    import matplotlib.pyplot as plt

    def fitEllipse(x, y):
        x = x[:, np.newaxis]
        y = y[:, np.newaxis]
        D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
        S = np.dot(D.T, D)
        C = np.zeros([6, 6])
        C[0, 2] = C[2, 0] = 2;
        C[1, 1] = -1
        E, V = linalg.eig(np.dot(linalg.inv(S), C))
        n = np.argmax(np.abs(E))
        a = V[:, n]
        return a

    def ellipse_center(a):
        b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
        num = b * b - a * c
        x0 = (c * d - b * f) / num
        y0 = (a * f - b * d) / num
        return np.array([x0, y0])

    def ellipse_angle_of_rotation(a):
        b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
        return 0.5 * np.arctan(2 * b / (a - c))

    def ellipse_axis_length(a):
        b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
        up = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
        down1 = (b * b - a * c) * ((c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
        down2 = (b * b - a * c) * ((a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
        res1 = np.sqrt(up / down1)
        res2 = np.sqrt(up / down2)
        return np.array([res1, res2])

    def find_ellipse(x, y):
        xmean = x.mean()
        ymean = y.mean()
        x -= xmean
        y -= ymean
        a = fitEllipse(x, y)
        center = ellipse_center(a)
        center[0] += xmean
        center[1] += ymean
        phi = ellipse_angle_of_rotation(a)
        axes = ellipse_axis_length(a)
        x += xmean
        y += ymean
        return center, phi, axes

    if __name__ == '__main__':
        points = [(560036.4495758876, 6362071.890493258),
                  (560036.4495758876, 6362070.890493258),
                  (560036.9495758876, 6362070.890493258),
                  (560036.9495758876, 6362070.390493258),
                  (560037.4495758876, 6362070.390493258),
                  (560037.4495758876, 6362064.890493258),
                  (560036.4495758876, 6362064.890493258),
                  (560036.4495758876, 6362063.390493258),
                  (560035.4495758876, 6362063.390493258),
                  (560035.4495758876, 6362062.390493258),
                  (560034.9495758876, 6362062.390493258),
                  (560034.9495758876, 6362061.390493258),
                  (560032.9495758876, 6362061.390493258),
                  (560032.9495758876, 6362061.890493258),
                  (560030.4495758876, 6362061.890493258),
                  (560030.4495758876, 6362061.390493258),
                  (560029.9495758876, 6362061.390493258),
                  (560029.9495758876, 6362060.390493258),
                  (560029.4495758876, 6362060.390493258),
                  (560029.4495758876, 6362059.890493258),
                  (560028.9495758876, 6362059.890493258),
                  (560028.9495758876, 6362059.390493258),
                  (560028.4495758876, 6362059.390493258),
                  (560028.4495758876, 6362058.890493258),
                  (560027.4495758876, 6362058.890493258),
                  (560027.4495758876, 6362058.390493258),
                  (560026.9495758876, 6362058.390493258),
                  (560026.9495758876, 6362057.890493258),
                  (560025.4495758876, 6362057.890493258),
                  (560025.4495758876, 6362057.390493258),
                  (560023.4495758876, 6362057.390493258),
                  (560023.4495758876, 6362060.390493258),
                  (560023.9495758876, 6362060.390493258),
                  (560023.9495758876, 6362061.890493258),
                  (560024.4495758876, 6362061.890493258),
                  (560024.4495758876, 6362063.390493258),
                  (560024.9495758876, 6362063.390493258),
                  (560024.9495758876, 6362064.390493258),
                  (560025.4495758876, 6362064.390493258),
                  (560025.4495758876, 6362065.390493258),
                  (560025.9495758876, 6362065.390493258),
                  (560025.9495758876, 6362065.890493258),
                  (560026.4495758876, 6362065.890493258),
                  (560026.4495758876, 6362066.890493258),
                  (560026.9495758876, 6362066.890493258),
                  (560026.9495758876, 6362068.390493258),
                  (560027.4495758876, 6362068.390493258),
                  (560027.4495758876, 6362068.890493258),
                  (560027.9495758876, 6362068.890493258),
                  (560027.9495758876, 6362069.390493258),
                  (560028.4495758876, 6362069.390493258),
                  (560028.4495758876, 6362069.890493258),
                  (560033.4495758876, 6362069.890493258),
                  (560033.4495758876, 6362070.390493258),
                  (560033.9495758876, 6362070.390493258),
                  (560033.9495758876, 6362070.890493258),
                  (560034.4495758876, 6362070.890493258),
                  (560034.4495758876, 6362071.390493258),
                  (560034.9495758876, 6362071.390493258),
                  (560034.9495758876, 6362071.890493258),
                  (560036.4495758876, 6362071.890493258)]

        fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
        a_points = np.array(points)
        x = a_points[:, 0]
        y = a_points[:, 1]
        axs[0].plot(x, y)
        center, phi, axes = find_ellipse(x, y)
        print(      "center = ", center)
        print(        "angle of rotation = ", phi)
        print(        "axes = ", axes)

        axs[1].plot(x, y)
        axs[1].scatter(center[0], center[1], color='red', s=100)
        axs[1].set_xlim(x.min(), x.max())
        axs[1].set_ylim(y.min(), y.max())

        plt.show()


if __name__ == '__main__':
    points = [[64.20433436532508, 216.71826625386998], [53.80612244897959, 196.17346938775512],
              [46.40816326530613, 178.57142857142858], [43.091836734693885, 157.14285714285714],
              [42.58163265306122, 135.96938775510205], [48.19387755102041, 114.03061224489797],
              [57.37755102040816, 95.40816326530613], [69.62244897959184, 79.08163265306122],
              [83.65306122448979, 64.28571428571429], [99.9795918367347, 54.59183673469388],
              [121.15306122448979, 47.704081632653065], [142.3265306122449, 44.89795918367347],
              [165.03061224489795, 44.13265306122449], [181.6122448979592, 48.724489795918366],
              [202.78571428571428, 57.90816326530612], [218.6020408163265, 69.38775510204081],
              [230.33673469387753, 82.6530612244898], [244.11224489795921, 100.76530612244898],
              [252.53061224489795, 118.62244897959184], [256.6122448979592, 137.5],
              [256.86734693877554, 160.96938775510205], [252.27551020408163, 180.35714285714286],
              [243.34693877551018, 200.25510204081633], [267.3265306122449, 212.24489795918367],
              [276.2551020408163, 187.75510204081633], [281.6122448979592, 165.56122448979593],
              [282.12244897959187, 138.5204081632653], [277.53061224489795, 112.5],
              [268.60204081632656, 90.56122448979592], [251.51020408163265, 65.05102040816327],
              [235.69387755102042, 49.48979591836735], [215.28571428571428, 33.673469387755105],
              [193.60204081632654, 24.23469387755102], [168.3469387755102, 17.602040816326532],
              [139.26530612244898, 17.602040816326532], [114.01020408163265, 22.448979591836736],
              [92.07142857142858, 30.867346938775512], [69.87755102040816, 43.62244897959184],
              [50.744897959183675, 60.96938775510204], [35.183673469387756, 83.16326530612245],
              [23.448979591836732, 106.88775510204081], [19.112244897959187, 134.18367346938777],
              [18.602040816326536, 158.41836734693877], [22.683673469387756, 183.67346938775512],
              [31.867346938775512, 207.90816326530611], [43.46130030959753, 227.55417956656348]]
    # Oval(points)
    # Oval1(points)
    Oval2()

