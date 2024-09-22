import xtrack as xt
import xobjects as xo
import xdeps as xd
import numpy as np
import pytest

@pytest.mark.parametrize('container_type', ['env', 'line'])
def test_vars_and_element_access_modes(container_type):

    env = xt.Environment()

    env.vars({
        'k.1': 1.,
        'a': 2.,
        'b': '2 * a + k.1',
    })

    line = env.new_line([])

    ee = {'env': env, 'line': line}[container_type]

    assert ee.vv['b'] == 2 * 2 + 1

    ee.vars['a'] = ee.vars['k.1']
    assert ee.vv['b'] == 2 * 1 + 1

    ee.vars(a=3.)
    ee.vars({'k.1': 'a'})
    assert ee.vv['k.1'] == 3.
    assert ee.vv['b'] == 2 * 3 + 3.

    ee.vars['k.1'] = 2 * ee.vars['a'] + 5
    assert ee.vv['k.1'] == 2 * 3 + 5
    assert ee.vv['b'] == 2 * 3 + 2 * 3 + 5

    ee.vars.set('a', 4.)
    assert ee.vv['k.1'] == 2 * 4 + 5
    assert ee.vv['b'] == 2 * 4 + 2 * 4 + 5

    ee.vars.set('k.1', '2*a + 5')
    assert ee.vv['k.1'] == 2 * 4 + 5
    assert ee.vv['b'] == 2 * 4 + 2 * 4 + 5

    ee.vars.set('k.1', 3 * ee.vars['a'] + 6)
    assert ee.vv['k.1'] == 3 * 4 + 6
    assert ee.vv['b'] == 2 * 4 + 3 * 4 + 6

    env.set('c', '2*b')
    assert env.vv['c'] == 2 * (2 * 4 + 3 * 4 + 6)
    env.set('d', 6)
    assert env.vv['d'] == 6
    env.set('d', '7')
    assert env.vv['d'] == 7

    ee.set('a', 0.)
    assert ee.vv['k.1'] == 3 * 0 + 6
    assert ee.vv['b'] == 2 * 0 + 3 * 0 + 6

    ee.set('a', 2.)
    ee.set('k.1', '2 * a + 5')
    assert ee.vv['k.1'] == 2 * 2 + 5
    assert ee.vv['b'] == 2 * 2 + 2 * 2 + 5

    ee.set('k.1', 3 * ee.vars['a'] + 6)
    assert ee.vv['k.1'] == 3 * 2 + 6
    assert ee.vv['b'] == 2 * 2 + 3 * 2 + 6

    assert hasattr(ee.ref['k.1'], '_value') # is a Ref

    ee.ref['a'] = 0
    assert ee.vv['k.1'] == 3 * 0 + 6
    assert ee.vv['b'] == 2 * 0 + 3 * 0 + 6

    ee.ref['a'] = 2
    ee.ref['k.1'] = 2 * ee.ref['a'] + 5
    assert ee.vv['k.1'] == 2 * 2 + 5
    assert ee.vv['b'] == 2 * 2 + 2 * 2 + 5

    #--------------------------------------------------

    ee.vars({
        'a': 4.,
        'b': '2 * a + 5',
        'k.1': '2 * a + 5',
    })

    env.new('bb', xt.Bend, k0='2 * b', length=3+env.vars['a'] + env.vars['b'],
            h=5.)
    assert env['bb'].k0 == 2 * (2 * 4 + 5)
    assert env['bb'].length == 3 + 4 + 2 * 4 + 5
    assert env['bb'].h == 5.

    env.vars['a'] = 2.
    assert env['bb'].k0 == 2 * (2 * 2 + 5)
    assert env['bb'].length == 3 + 2 + 2 * 2 + 5
    assert env['bb'].h == 5.

    line = env.new_line([
        env.new('bb1', 'bb', length=3*env.vars['a'], at='2*a'),
        env.place('bb', at=10 * env.vars['a'], from_='bb1'),
    ])

    assert hasattr(env.ref['bb1'].length, '_value') # is a Ref
    assert not hasattr(env['bb1'].length, '_value') # a number
    assert env.ref['bb1'].length._value == 3 * 2
    assert env['bb1'].length == 3 * 2

    assert hasattr(env.ref['bb1'].length, '_value') # is a Ref
    assert not hasattr(env['bb1'].length, '_value') # a number
    assert env.ref['bb1'].length._value == 3 * 2
    assert env['bb1'].length == 3 * 2

    assert line.get('bb1') is not env.get('bb')
    assert line.get('bb') is env.get('bb')

    a = env.vv['a']
    assert line['bb1'].length == 3 * a
    assert line['bb1'].k0 == 2 * (2 * a + 5)
    assert line['bb1'].h == 5.

    assert line['bb'].k0 == 2 * (2 * a + 5)
    assert line['bb'].length == 3 + a + 2 * a + 5
    assert line['bb'].h == 5.

    tt = line.get_table(attr=True)
    tt['s_center'] = tt['s'] + tt['length']/2

    assert np.all(tt.name ==  np.array(['drift_1', 'bb1', 'drift_2', 'bb', '_end_point']))

    assert tt['s_center', 'bb1'] == 2*a
    assert tt['s_center', 'bb'] - tt['s_center', 'bb1'] == 10*a

    old_a = a
    line.vars['a'] = 3.
    a = line.vv['a']
    assert line['bb1'].length == 3 * a
    assert line['bb1'].k0 == 2 * (2 * a + 5)
    assert line['bb1'].h == 5.

    assert line['bb'].k0 == 2 * (2 * a + 5)
    assert line['bb'].length == 3 + a + 2 * a + 5
    assert line['bb'].h == 5.

    tt_new = line.get_table(attr=True)

    # Drifts are not changed:
    tt_new['length', 'drift_1'] == tt['length', 'drift_1']
    tt_new['length', 'drift_2'] == tt['length', 'drift_2']

def test_element_placing_at_s():

    env = xt.Environment()

    env.vars({
        'l.b1': 1.0,
        'l.q1': 0.5,
        's.ip': 10,
        's.left': -5,
        's.right': 5,
        'l.before_right': 1,
        'l.after_left2': 0.5,
    })

    # names, tab_sorted = handle_s_places(seq)
    line = env.new_line(components=[
        env.new('b1', xt.Bend, length='l.b1'),
        env.new('q1', xt.Quadrupole, length='l.q1'),
        env.new('ip', xt.Marker, at='s.ip'),
        (
            env.new('before_before_right', xt.Marker),
            env.new('before_right', xt.Sextupole, length=1),
            env.new('right',xt.Quadrupole, length=0.8, at='s.right', from_='ip'),
            env.new('after_right', xt.Marker),
            env.new('after_right2', xt.Marker),
        ),
        env.new('left', xt.Quadrupole, length=1, at='s.left', from_='ip'),
        env.new('after_left', xt.Marker),
        env.new('after_left2', xt.Bend, length='l.after_left2'),
    ])

    tt = line.get_table(attr=True)
    tt['s_center'] = tt['s'] + tt['length']/2
    assert np.all(tt.name == np.array([
        'b1', 'q1', 'drift_1', 'left', 'after_left', 'after_left2',
        'drift_2', 'ip', 'drift_3', 'before_before_right', 'before_right',
        'right', 'after_right', 'after_right2', '_end_point']))

    xo.assert_allclose(env['b1'].length, 1.0, rtol=0, atol=1e-14)
    xo.assert_allclose(env['q1'].length, 0.5, rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s', 'ip'], 10, rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s', 'before_before_right'], tt['s', 'before_right'],
                    rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'before_right'] - tt['s_center', 'right'],
                    -(1 + 0.8)/2, rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'right'] - tt['s', 'ip'], 5, rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'after_right'] - tt['s_center', 'right'],
                        0.8/2, rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'after_right2'] - tt['s_center', 'right'],
                        0.8/2, rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'left'] - tt['s_center', 'ip'], -5,
                    rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'after_left'] - tt['s_center', 'left'], 1/2,
                        rtol=0, atol=1e-14)
    xo.assert_allclose(tt['s_center', 'after_left2'] - tt['s_center', 'after_left'],
                    0.5/2, rtol=0, atol=1e-14)


    # import matplotlib.pyplot as plt
    # plt.close('all')
    # line.survey().plot()

    # plt.show()

def test_assemble_ring():

    env = xt.Environment()
    env.particle_ref = xt.Particles(p0c=2e9)

    n_bends_per_cell = 6
    n_cells_par_arc = 3
    n_arcs = 3

    n_bends = n_bends_per_cell * n_cells_par_arc * n_arcs

    env.vars({
        'l.mq': 0.5,
        'kqf': 0.027,
        'kqd': -0.0271,
        'l.mb': 10,
        'l.ms': 0.3,
        'k2sf': 0.001,
        'k2sd': -0.001,
        'angle.mb': 2 * np.pi / n_bends,
        'k0.mb': 'angle.mb / l.mb',
        'k0l.corrector': 0,
        'k1sl.corrector': 0,
        'l.halfcell': 38,
    })

    env.new('mb', xt.Bend, length='l.mb', k0='k0.mb', h='k0.mb')
    env.new('mq', xt.Quadrupole, length='l.mq')
    env.new('ms', xt.Sextupole, length='l.ms')
    env.new('corrector', xt.Multipole, knl=[0], length=0.1)

    girder = env.new_line(components=[
        env.place('mq', at=1),
        env.place('ms', at=0.8, from_='mq'),
        env.place('corrector', at=-0.8, from_='mq'),
    ])

    girder_f = girder.clone(name='f')
    girder_d = girder.clone(name='d', mirror=True)
    env.set('mq.f', k1='3') # Test string with value
    assert env['mq.f'].k1 == 3.
    env.set('mq.f', k1='kqf')
    env.set('mq.d', k1='kqd')

    halfcell = env.new_line(components=[

        # End of the half cell (will be mid of the cell)
        env.new('mid', xt.Marker, at='l.halfcell'),

        # Bends
        env.new('mb.2', 'mb', at='l.halfcell / 2'),
        env.new('mb.1', 'mb', at='-l.mb - 1', from_='mb.2'),
        env.new('mb.3', 'mb', at='l.mb + 1', from_='mb.2'),

        # Quadrupoles, sextupoles and correctors
        env.place(girder_d, at=1.2),
        env.place(girder_f, at='l.halfcell - 1.2'),

    ])


    hcell_left = halfcell.replicate(name='l', mirror=True)
    hcell_right = halfcell.replicate(name='r')

    cell = env.new_line(components=[
        env.new('start', xt.Marker),
        hcell_left,
        hcell_right,
        env.new('end', xt.Marker),
    ])

    opt = cell.match(
        method='4d',
        vary=xt.VaryList(['kqf', 'kqd'], step=1e-5),
        targets=xt.TargetSet(
            qx=0.333333,
            qy=0.333333,
        ))
    tw_cell = cell.twiss4d()


    env.vars({
        'kqf.ss': 0.027 / 2,
        'kqd.ss': -0.0271 / 2,
    })

    halfcell_ss = env.new_line(components=[

        env.new('mid', xt.Marker, at='l.halfcell'),

        env.new('mq.ss.d', 'mq', k1='kqd.ss', at = '0.5 + l.mq / 2'),
        env.new('mq.ss.f', 'mq', k1='kqf.ss', at = 'l.halfcell - l.mq / 2 - 0.5'),

        env.new('corrector.ss.v', 'corrector', at=0.75, from_='mq.ss.d'),
        env.new('corrector.ss.h', 'corrector', at=-0.75, from_='mq.ss.f')
    ])

    hcell_left_ss = halfcell_ss.replicate(name='l', mirror=True)
    hcell_right_ss = halfcell_ss.replicate(name='r')
    cell_ss = env.new_line(components=[
        env.new('start.ss', xt.Marker),
        hcell_left_ss,
        hcell_right_ss,
        env.new('end.ss', xt.Marker),
    ])

    opt = cell_ss.match(
        solve=False,
        method='4d',
        vary=xt.VaryList(['kqf.ss', 'kqd.ss'], step=1e-5),
        targets=xt.TargetSet(
            betx=tw_cell.betx[-1], bety=tw_cell.bety[-1], at='start.ss',
        ))
    opt.solve()


    arc = env.new_line(components=[
        cell.replicate(name='cell.1'),
        cell.replicate(name='cell.2'),
        cell.replicate(name='cell.3'),
    ])


    ss = env.new_line(components=[
        cell_ss.replicate('cell.1'),
        cell_ss.replicate('cell.2'),
    ])

    ring = env.new_line(components=[
        arc.replicate(name='arc.1'),
        ss.replicate(name='ss.1'),
        arc.replicate(name='arc.2'),
        ss.replicate(name='ss.2'),
        arc.replicate(name='arc.3'),
        ss.replicate(name='ss.3'),
    ])

    ## Insertion

    env.vars({
        'k1.q1': 0.025,
        'k1.q2': -0.025,
        'k1.q3': 0.025,
        'k1.q4': -0.02,
        'k1.q5': 0.025,
    })

    half_insertion = env.new_line(components=[

        # Start-end markers
        env.new('ip', xt.Marker),
        env.new('e.insertion', xt.Marker, at=76),

        # Quads
        env.new('mq.1', xt.Quadrupole, k1='k1.q1', length='l.mq', at = 20),
        env.new('mq.2', xt.Quadrupole, k1='k1.q2', length='l.mq', at = 25),
        env.new('mq.3', xt.Quadrupole, k1='k1.q3', length='l.mq', at=37),
        env.new('mq.4', xt.Quadrupole, k1='k1.q4', length='l.mq', at=55),
        env.new('mq.5', xt.Quadrupole, k1='k1.q5', length='l.mq', at=73),

        # Dipole correctors (will use h and v on the same corrector)
        env.new('corrector.ss.1', 'corrector', at=0.75, from_='mq.1'),
        env.new('corrector.ss.2', 'corrector', at=-0.75, from_='mq.2'),
        env.new('corrector.ss.3', 'corrector', at=0.75, from_='mq.3'),
        env.new('corrector.ss.4', 'corrector', at=-0.75, from_='mq.4'),
        env.new('corrector.ss.5', 'corrector', at=0.75, from_='mq.5'),

    ])

    tw_arc = arc.twiss4d()

    opt = half_insertion.match(
        solve=False,
        betx=tw_arc.betx[0], bety=tw_arc.bety[0],
        alfx=tw_arc.alfx[0], alfy=tw_arc.alfy[0],
        init_at='e.insertion',
        start='ip', end='e.insertion',
        vary=xt.VaryList(['k1.q1', 'k1.q2', 'k1.q3', 'k1.q4'], step=1e-5),
        targets=[
            xt.TargetSet(alfx=0, alfy=0, at='ip'),
            xt.Target(lambda tw: tw.betx[0] - tw.bety[0], 0),
            xt.Target(lambda tw: tw.betx.max(), xt.LessThan(400)),
            xt.Target(lambda tw: tw.bety.max(), xt.LessThan(400)),
            xt.Target(lambda tw: tw.betx.min(), xt.GreaterThan(2)),
            xt.Target(lambda tw: tw.bety.min(), xt.GreaterThan(2)),
        ]
    )
    opt.step(40)
    opt.solve()

    insertion = env.new_line([
        half_insertion.replicate('l', mirror=True),
        half_insertion.replicate('r')])



    ring2 = env.new_line(components=[
        arc.replicate(name='arcc.1'),
        'ss.1',
        'arc.2',
        insertion,
        'arc.3',
        env['ss.3'],
    ])


    # # Check buffer behavior
    ring2_sliced = ring2.select()
    ring2_sliced.cut_at_s(np.arange(0, ring2.get_length(), 0.5))


    # import matplotlib.pyplot as plt
    # plt.close('all')
    # for ii, rr in enumerate([ring, ring2_sliced]):

    #     tw = rr.twiss4d()

    #     fig = plt.figure(ii, figsize=(6.4*1.2, 4.8))
    #     ax1 = fig.add_subplot(2, 1, 1)
    #     pltbet = tw.plot('betx bety', ax=ax1)
    #     ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
    #     pltdx = tw.plot('dx', ax=ax2)
    #     fig.subplots_adjust(right=.85)
    #     pltbet.move_legend(1.2,1)
    #     pltdx.move_legend(1.2,1)

    # ring2.survey().plot()

    # plt.show()


@pytest.mark.parametrize('container_type', ['env', 'line'])
def test_element_views(container_type):

    env = xt.Environment()
    line = env.new_line()

    if container_type == 'env':
        ee = env
    elif container_type == 'line':
        ee = line

    ee['a']  = 3.
    ee['b1']  = 3 * ee['a'] # done by value
    ee['b2']  = 3 * ee.ref['a'] # done by reference
    ee['c']  = '4 * a'

    assert isinstance(ee['a'], float)
    assert isinstance(ee['b1'], float)
    assert isinstance(ee['b2'], float)
    assert isinstance(ee['c'], float)

    assert ee['a'] == 3
    assert ee['b1'] == 9
    assert ee['b2'] == 9
    assert ee['c'] == 12

    assert ee.ref['a']._value == 3
    assert ee.ref['b1']._value == 9
    assert ee.ref['b2']._value == 9
    assert ee.ref['c']._value == 12

    assert ee.get('a') == 3
    assert ee.get('b1') == 9
    assert ee.get('b2') == 9
    assert ee.get('c') == 12

    env.new('mb', 'Bend', extra={'description': 'Hello Riccarco'},
            k1='3*a', h=4*ee.ref['a'], knl=[0, '5*a', 6*ee.ref['a']])
    assert isinstance(ee['mb'].k1, float)
    assert isinstance(ee['mb'].h, float)
    assert isinstance(ee['mb'].knl[0], float)
    assert ee['mb'].k1 == 9
    assert ee['mb'].h == 12
    assert ee['mb'].knl[0] == 0
    assert ee['mb'].knl[1] == 15
    assert ee['mb'].knl[2] == 18

    ee['a'] = 4
    assert ee['a'] == 4
    assert ee['b1'] == 9
    assert ee['b2'] == 12
    assert ee['c'] == 16
    assert ee['mb'].k1 == 12
    assert ee['mb'].h == 16
    assert ee['mb'].knl[0] == 0
    assert ee['mb'].knl[1] == 20
    assert ee['mb'].knl[2] == 24

    ee['mb'].k1 = '30*a'
    ee['mb'].h = 40 * ee.ref['a']
    ee['mb'].knl[1] = '50*a'
    ee['mb'].knl[2] = 60 * ee.ref['a']
    assert ee['mb'].k1 == 120
    assert ee['mb'].h == 160
    assert ee['mb'].knl[0] == 0
    assert ee['mb'].knl[1] == 200
    assert ee['mb'].knl[2] == 240

    assert isinstance(ee['mb'].k1, float)
    assert isinstance(ee['mb'].h, float)
    assert isinstance(ee['mb'].knl[0], float)

    assert ee.ref['mb'].k1._value == 120
    assert ee.ref['mb'].h._value == 160
    assert ee.ref['mb'].knl[0]._value == 0
    assert ee.ref['mb'].knl[1]._value == 200
    assert ee.ref['mb'].knl[2]._value == 240

    assert ee.get('mb').k1 == 120
    assert ee.get('mb').h == 160
    assert ee.get('mb').knl[0] == 0
    assert ee.get('mb').knl[1] == 200
    assert ee.get('mb').knl[2] == 240

    # Some interesting behavior
    assert type(ee['mb']) is xd.madxutils.View
    assert ee['mb'].__class__ is xt.Bend
    assert type(ee.ref['mb']._value) is xt.Bend
    assert type(ee.get('mb')) is xt.Bend
