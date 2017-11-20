
import json

def read_config():
    config = {}
    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/Wex-Matrix-Last-Trade-Engine-d1a/config.json') as f:
        config = json.load(f)
    for k, v in config.iteritems():
        print '%s: %s' % (k, v)
    return config

'''
class Matrix:
    matrix_filename = ""
    matrixarray = []
    matrix_tradestate_array = []
    martrix_order_id_array = []

    def __init__(self, filename=""):
        self.matrix_filename = filename


    def readFile(self):
'''


# Replace a line in a file.
# For instance used to update Matrix File as we update orders.
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()