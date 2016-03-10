#!/usr/bin/env python
# encoding: utf-8

"""Pezeshk, Zandieh, and Tavakoli (2011) ground motion model."""

from __future__ import division

import numpy as np

from . import model

__author__ = 'Albert Kottke'


class PezeshkZandiehTavakoli2011(model.Model):
    """Pezeshk, Zandieh, and Tavakoli (2011) :cite:`pezeshk11` ground motion
    prediction model.

    Developed for the Eastern North America with a reference velocity of 2000
    m/s.
    """

    NAME = 'Pezeshk et al. (2011)'
    ABBREV = 'Pea11'

    # Reference shear-wave velocity (m/sec)
    V_REF = 2000.

    # Load the coefficients for the model
    COEFF = model.load_data_file('pezeshk_zandieh_tavakoli_2011.csv', 1)
    PERIODS = COEFF['period']

    INDEX_PGA = 0
    INDICES_PSA = np.arange(1, 23)

    PARAMS = [
        model.NumericParameter('mag', True, 5, 8),
        model.NumericParameter('dist_rup', True, None, 1000),
    ]

    def __init__(self, **kwds):
        """Initialize the model.

        Keyword Args:
            mag (float): moment magnitude of the event (:math:`M_w`)
            dist_rup (float): Closest distance to the rupture plane
                (:math:`R_\\text{rup}`, km)
        """
        super(PezeshkZandiehTavakoli2011, self).__init__(**kwds)
        self._ln_resp = self._calc_ln_resp()
        self._ln_std = self._calc_ln_std()

    def _calc_ln_resp(self):
        """Calculate the natural logarithm of the response.

        Returns:
            :class:`np.array`: Natural log of the response.
        """
        p = self.params
        c = self.COEFF

        dist = np.sqrt(p['dist_rup'] ** 2 + c['c11'] ** 2)

        log10_resp = (
            c['c1'] +
            c['c2'] * p['mag'] +
            c['c3'] * p['mag'] ** 2 +
            (c['c4'] + c['c5'] * p['mag']) * np.minimum(
                np.log10(dist),
                np.log10(70.)
            ) +
            (c['c6'] + c['c7'] * p['mag']) *
            np.maximum(
                np.minimum(
                    np.log10(dist / 70.),
                    np.log10(140. / 70.)
                ), 0. ) +
            (c['c8'] + c['c9'] * p['mag']) * np.maximum(
                np.log10(dist / 140.), 0) +
            c['c10'] * dist
        )

        ln_resp = np.log(np.power(10, log10_resp))

        return ln_resp

    def _calc_ln_std(self):
        """Calculate the logarithmic standard deviation.

        Returns:
            :class:`np.array`: Logarithmic standard deviation.
        """
        p = self.params
        c = self.COEFF

        if p['mag'] <= 7.:
            ln_std_mean = c['c12'] * p['mag'] + c['c13']
        else:
            ln_std_mean = -6.95e-3 * p['mag'] + c['c14']

        ln_std = np.sqrt(ln_std_mean ** 2 + c['sigma_reg'] ** 2)

        return ln_std
