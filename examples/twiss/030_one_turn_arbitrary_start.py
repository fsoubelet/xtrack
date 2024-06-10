# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

import xtrack as xt

collider = xt.Multiline.from_json(
    '../../test_data/hllhc15_thick/hllhc15_collider_thick.json')
collider.build_trackers()

collider.lhcb1.twiss_default['method'] = '4d'
collider.lhcb2.twiss_default['method'] = '4d'
collider.lhcb2.twiss_default['reverse'] = True

line = collider.lhcb2 # <- use lhcb2 to test the reverse option

tw8_closed = line.twiss(start='ip8')
tw8_open = line.twiss(start='ip8', betx=1.5, bety=1.5)

tw_part = line.twiss(start='ip8', end='ip2', init='full_periodic')

# Test get strengths (to be moved to another script)
line.get_strengths().rows['mbw\..*l3.b2'].cols['k0l angle_rad']
# is:
# Table: 6 rows, 3 cols
# name                            k0l    angle_rad
# mbw.f6l3.b2            -0.000188729 -0.000188729
# mbw.e6l3.b2            -0.000188729 -0.000188729
# mbw.d6l3.b2            -0.000188729 -0.000188729
# mbw.c6l3.b2             0.000188729  0.000188729
# mbw.b6l3.b2             0.000188729  0.000188729
# mbw.a6l3.b2             0.000188729  0.000188729

line.get_strengths(reverse=False).rows['mbw\..*l3.b2'].cols['k0l angle_rad']
# is:
# Table: 6 rows, 3 cols
# name                            k0l    angle_rad
# mbw.a6l3.b2            -0.000188729 -0.000188729
# mbw.b6l3.b2            -0.000188729 -0.000188729
# mbw.c6l3.b2            -0.000188729 -0.000188729
# mbw.d6l3.b2             0.000188729  0.000188729
# mbw.e6l3.b2             0.000188729  0.000188729
# mbw.f6l3.b2             0.000188729  0.000188729

import xobjects as xo
str_table_rev = line.get_strengths() # Takes reverse from twiss_default
xo.assert_allclose(line['mbw.a6l3.b2'].k0,
        -str_table_rev['k0l', 'mbw.a6l3.b2'] / str_table_rev['length', 'mbw.a6l3.b2'],
        rtol=0, atol=1e-14)
xo.assert_allclose(line['mbw.a6l3.b2'].h,
        -str_table_rev['angle_rad', 'mbw.a6l3.b2'] / str_table_rev['length', 'mbw.a6l3.b2'],
        rtol=0, atol=1e-14)

str_table = line.get_strengths(reverse=False) # Takes reverse from twiss_default
xo.assert_allclose(line['mbw.a6l3.b2'].k0,
        str_table['k0l', 'mbw.a6l3.b2'] / str_table['length', 'mbw.a6l3.b2'],
        rtol=0, atol=1e-14)
xo.assert_allclose(line['mbw.a6l3.b2'].h,
        str_table['angle_rad', 'mbw.a6l3.b2'] / str_table['length', 'mbw.a6l3.b2'],
        rtol=0, atol=1e-14)

tw = line.twiss()
tw8_closed