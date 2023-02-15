import glob
import copy
import yaml
import os



def parse_prj(prj_file):
    prj_yaml = None
    return prj_yaml

def parse_p(prj_file):
    p_yaml = None
    return p_yaml

def parse_u(prj_file):
    u_yaml = None
    return u_yaml

def create_yaml(prj_yaml, p_yaml, u_yaml):
    return None

def parse(prj_file):
    prj_dir, tail = os.path.split(prj_file)
    prj_yaml = parse_prj(prj_file)
    p_yaml = parse_p(prj_dir)
    u_yaml = parse_u(prj_dir)
    create_yaml(prj_yaml, p_yaml, u_yaml)