from django.db.models import Sum
from image_formats import plot_png, plot_svg, plot_png2, plot_svg2
class Histogram(object):
    def __init__(self):
        from django.contrib.auth.models import User
        self.data = User.objects\
                        .values('id')\
                        .annotate(t=Sum('flight__total'))\
                        .filter(t__isnull=False)\
                        .values_list('t', flat=True)
                        
        #self.data = [706.79999999999905, 2.5, 40.100000000000001, 1319.5999999999999, 282.19999999999999, 452.80000000000001, 179.0, 358.80000000000001, 60.299999999999997, 709.79999999999995, 708.70000000000005, 50.700000000000003, 23.199999999999999, 273.19999999999999, 997.89999999999998, 753.70000000000005, 145.30000000000001, 1554.5999999999999, 45.0, 284.19999999999999, 253.5, 38.100000000000001, 19.0, 5.7000000000000002, 343.10000000000002, 1386.0999999999999, 799.10000000000002, 72.200000000000003, 656.0, 330.39999999999998, 4604.7000000000198, 249.5, 43.700000000000003, 55.799999999999997, 204.69999999999999, 1443.7, 288.39999999999998, 141.40000000000001, 349.39999999999998, 45.399999999999999, 38.600000000000001, 32.0, 747.99999999999898, 648.60000000000002, 1270.5999999999999, 53.200000000000003, 269.10000000000002, 2231.0, 278.8999999999998, 63.100000000000001, 133.40000000000001, 459.30000000000098, 273.10000000000002, 320.89999999999998, 101.2, 171.19999999999999, 337.19999999999999, 150.5, 1358.2, 2.5, 1127.2, 73.0, 57.700000000000003, 1451.3, 1.3999999999999999, 317.19999999999999, 227.5, 15.0, 344.10000000000002, 519.60000000000105, 1117.8, 11.699999999999999, 1.1000000000000001, 1290.7, 197.19999999999999, 17.0, 278.89999999999998, 2.3999999999999999, 13.5, 275.80000000000001, 363.80000000000001, 266.0, 61.100000000000001, 301.60000000000002, 46.600000000000001, 194.5, 7.4000000000000004, 604.0, 51.0, 1.3999999999999999, 332.19999999999999, 362.10000000000002, 1718.3, 423.89999999999998, 3.8999999999999999, 300.10000000000002, 904.00000000000102, 83.099999999999895, 2012.4000000000001, 341.10000000000002, 4602.50000000002, 266.39999999999998, 38.399999999999999, 1514.9000000000001, 731.400000000001, 55.5, 20.699999999999999, 201.69999999999999, 232.90000000000001, 42.100000000000001, 206.5, 759.70000000000095, 257.19999999999999, 115.59999999999999, 416.80000000000001, 1.1000000000000001, 227.09999999999999, 267.39999999999998, 1359.9000000000001, 957.50000000000102, 90.916666666674004, 115.59999999999999, 243.90000000000001, 748.20000000000005, 27.199999999999999, 441.80000000000001, 246.5, 66.099999999999994, 373.60000000000002, 663.400000000001, 144.5, 1.6000000000000001, 30.300000000000001, 309.80000000000001, 198.5, 288.19999999999999, 893.60000000000002, 704.10000000000105, 150.09999999999999, 1577.8, 98.099999999999994, 51.899999999999999, 222.09999999999999, 51.5, 4.7999999999999998]

                        
    def output(self):
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.mlab as mlab

        mu, sigma = 100, 15
        x = self.data
        
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # the histogram of the data
        n, bins, patches = ax.hist(x, 60, normed=1, facecolor='green', alpha=0.75)

        # hist uses np.histogram under the hood to create 'n' and 'bins'.
        # np.histogram returns the bin edges, so there will be 50 probability
        # density values in n, 51 bin edges in bins and 50 patches.  To get
        # everything lined up, we'll compute the bin centers
        bincenters = 0.5*(bins[1:]+bins[:-1])
        # add a 'best fit' line for the normal PDF
        y = mlab.normpdf( bincenters, mu, sigma)
        l = ax.plot(bincenters, y, 'r--', linewidth=1)

        ax.set_xlabel('Hours')
        ax.set_ylabel('Probability')
        #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
        ax.set_xlim(0, 2000)
        ax.set_ylim(0, 0.003)
        ax.grid(True)
        
        return fig
    
    def as_png(self):
        return plot_png(self.output)()
