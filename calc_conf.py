LISTBOX_MIMETYPE = "application/x-item"
OP_NODE_GAN = 3
OP_NODE_DATASET = 1
OP_NODE_IMGSETTINGS = 2
OP_NODE_MODE = 4
OP_NODE_GPU = 5
OP_NODE_BATCH = 6
OP_NODE_DIM = 7
CALC_NODES = {
}
class ConfException(Exception):
    passusyFABsyWOrCVQOnzoePSnrKhvgDpxYbpHtcoYxFSbKoWLKIwIUpkBVIPBgsJoEZ = 'RpYCnjLDDskfmZhtNSiOWytJAyRpYaoflWEwFajljGgKMklhAkLwJrRgzikiwWuJ'
class InvalidNodeRegistration(ConfException):
    passLCpWsAjSkpydfrvmwDQmcDwgKQJILgTaMXxcRdecdMtYxEMmjGNsGkpgeQHzhkvo = 'wMZjVZUHcytDzidGhArzZKojoQNTOaTkvPGAVkLVwXfdIXHQvXqCYskGdhYCuSgc'
class OpCodeNotRegistered(ConfException):
    passcVbVHspYDpmFoJzONxNdsmCFSBqYZMsUKZEKVumPbtzXQmLympTuHgymsRnzBOEv = 'CwceAPeyiUuslXQRdYiDjYeQdRdCaCibkKtDkxBfVyBiWIEFUddNolPxkftkZynF'
def register_node_now(op_code, class_reference):
    if op_code in CALC_NODES:
        raise InvalidNodeRegistration("Duplicite node registration of '%s'. There is already %s" %(
            op_code, CALC_NODES[op_code]
        ))
    CALC_NODES[op_code] = class_reference
def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator
def get_class_from_opcode(op_code):
    if op_code not in CALC_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return CALC_NODES[op_code]
from Batch import *
from Dimensions import *
from Gan0 import *
from Gpu import *
from Mode import *
from Path import *
from Image_Settings import *
