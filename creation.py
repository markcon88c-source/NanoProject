# creation.py
# HQ + Unit creation helpers for NanoRunner ecosystem

from HQ import HQ
from Unit import Unit

# ------------------------------------------------------------
# HQ CREATION
# ------------------------------------------------------------

def create_theater_hq(id, pos):
    hq = HQ(id=id, pos=pos, level=0)
    hq.parent = None
    return hq

def create_army_group_hq(id, pos, parent):
    hq = HQ(id=id, pos=pos, level=1)
    hq.parent = parent
    return hq

def create_army_hq(id, pos, parent):
    hq = HQ(id=id, pos=pos, level=2)
    hq.parent = parent
    return hq

def create_corps_hq(id, pos, parent):
    hq = HQ(id=id, pos=pos, level=3)
    hq.parent = parent
    return hq


# ------------------------------------------------------------
# DIVISION / BRIGADE CREATION (FIXED FOR NEW Unit CLASS)
# ------------------------------------------------------------

def create_inf_div(id, name, pos):
    return Unit(id, name, pos, "INF")

def create_mot_div(id, name, pos):
    return Unit(id, name, pos, "MOT")

def create_mech_div(id, name, pos):
    return Unit(id, name, pos, "MECH")

def create_arm_div(id, name, pos):
    return Unit(id, name, pos, "ARM")

def create_panzer_div(id, name, pos):
    return Unit(id, name, pos, "PANZER")

def create_support_brigade(id, name, pos):
    u = Unit(id, name, pos, "SUPPORT")
    u.echelon = "Brigade"
    return u

def create_recon_brigade(id, name, pos):
    u = Unit(id, name, pos, "RECON")
    u.echelon = "Brigade"
    return u

def create_artillery_brigade(id, name, pos):
    u = Unit(id, name, pos, "ARTY")
    u.echelon = "Brigade"
    return u

def create_engineer_brigade(id, name, pos):
    u = Unit(id, name, pos, "ENG")
    u.echelon = "Brigade"
    return u
