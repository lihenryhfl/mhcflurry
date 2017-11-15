import numpy
import pandas

class PercentRankTransform(object):
    """
    Transform arbitrary values into percent ranks.
    """

    def __init__(self):
        self.cdf = None
        self.bin_edges = None

    def fit(self, values, bins):
        """
        Fit the transform using the given values, which are used to
        establish percentiles.
        """
        assert self.cdf is None
        assert self.bin_edges is None
        assert len(values) > 0
        (hist, self.bin_edges) = numpy.histogram(values, bins=bins)
        self.cdf = numpy.ones(len(hist) + 3) * numpy.nan
        self.cdf[0] = 0.0
        self.cdf[1] = 0.0
        self.cdf[-1] = 100.0
        numpy.cumsum(hist * 100.0 / numpy.sum(hist), out=self.cdf[2:-1])
        assert not numpy.isnan(self.cdf).any()

    def transform(self, values):
        """
        Return percent ranks (range [0, 100]) for the given values.
        """
        assert self.cdf is not None
        assert self.bin_edges is not None
        indices = numpy.searchsorted(self.bin_edges, values)
        result = self.cdf[indices]
        assert len(result) == len(values)
        return result

    def to_series(self):
        """
        Serialize the fit to a pandas.Series.

        The index on the series gives the bin edges and the valeus give the CDF.

        Returns
        -------
        pandas.Series

        """
        return pandas.Series(
            self.cdf, index=[numpy.nan] + list(self.bin_edges) + [numpy.nan])

    @staticmethod
    def from_series(series):
        """
        Deseralize a PercentRankTransform the given pandas.Series, as returned
        by `to_series()`.

        Parameters
        ----------
        series : pandas.Series

        Returns
        -------
        PercentRankTransform

        """
        result = PercentRankTransform()
        result.cdf = series.values
        result.bin_edges = series.index.values[1:-1]
        return result





