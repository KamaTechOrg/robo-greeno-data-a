# MuJoCo + PhantomX hexapod runner

A small, self-contained MuJoCo simulation of a PhantomX-class hexapod
(six 3-DOF legs, 18 joints). It loads the robot, solves every leg with
the closed-form inverse kinematics from the Stage A leg explorer, and
makes the robot **stand and walk on command**.

This is the Stage A milestone (due Thu 28 May): wrap the per-leg IK in
MuJoCo and drive all six legs at once.

## Run it

```
pip install -r requirements.txt
python run.py            # viewer: stand -> crouch -> tall -> walk
python run.py --walk     # viewer: straight into a tripod walk
python run.py --check    # headless self-test, no display (for CI)
python run.py --xml      # write hexapod.xml to inspect
```

Drag in the viewer window to orbit the camera. Leg colours: coxa grey,
femur green, tibia blue, foot orange -- the same colour key as the
Stage A leg explorer.

## The files

| file               | what it is                                        |
|--------------------|---------------------------------------------------|
| `config.py`        | **the one geometry file** -- link lengths, leg mounts, joint limits, stance, gait. Edit only this for new hardware. |
| `hexapod_ik.py`    | closed-form per-leg inverse + forward kinematics. |
| `hexapod_model.py` | builds the MuJoCo model (MJCF) from `config.py`.  |
| `run.py`           | the runner -- viewer, poses, tripod walk, self-test. |
| `hexapod.xml`      | a generated copy of the model, for inspection.    |

## How it fits together

```
config.py  ->  hexapod_model.py  ->  MuJoCo model
config.py  ->  hexapod_ik.py     ->  joint angles  ->  servos
```

`run.py` picks six foot targets (a stance, or a moving gait), asks
`hexapod_ik.py` for the joint angles, and writes them to the model's
18 position servos. Because the model and the IK both read their
numbers from `config.py`, swapping in the real PhantomX dimensions
later is a one-file change -- nothing else needs to be touched.

## Self-test

`python run.py --check` verifies, with no display:

1. the MuJoCo model builds and loads
2. the IK round-trips (forward kinematics undoes inverse kinematics)
3. the model agrees with the IK -- feet land exactly on their targets
4. the robot stands up steadily under gravity
5. the robot walks a tripod gait without falling over

All five must print PASS.

## Next: Stage B

Stage B (due 11 Jun) layers proper walking gaits on top of this
runner -- the `walk_targets()` function in `run.py` is the seed.
