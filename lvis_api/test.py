import logging
from lvis import LVIS, LVISResults, LVISEval

# result and val files for 100 randomly sampled images.
# ANNOTATION_PATH = "./data/lvis_val_100.json"
# RESULT_PATH = "./data/lvis_results_100.json"
ANNOTATION_PATH = "./data/lvis/lvis_v0.5_val.json"
RESULT_PATH = './debug_file.pkl.segm.json'
# RESULT_PATH = './mask_rcnn_r101_fpn_1x_lvis.pkl.segm.json'
ANN_TYPE = 'segm'

lvis_eval = LVISEval(ANNOTATION_PATH, RESULT_PATH, ANN_TYPE)
lvis_eval.run()
lvis_eval.print_results(True)
