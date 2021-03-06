"""
API for accessing LVIS Dataset: https://lvisdataset.org.

LVIS API is a Python API that assists in loading, parsing and visualizing
the annotations in LVIS. In addition to this API, please download
images and annotations from the LVIS website.
"""

import json
import os
import logging
from collections import defaultdict
from urllib.request import urlretrieve

import pycocotools.mask as mask_utils

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import numpy as np

class LVIS:
    def __init__(self, annotation_path):
        """Class for reading and visualizing annotations.
        Args:
            annotation_path (str): location of annotation file
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Loading annotations.")

        self.dataset = self._load_json(annotation_path)

        assert (
            type(self.dataset) == dict
        ), "Annotation file format {} not supported.".format(type(self.dataset))
        self._create_index()

    def _load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    # def _create_index_only_test_on_finetune_classes(self):

    # def _create_index_load_fewshot_classes_anns(self):
    #     fewshot_dataset={}
    #     import pickle
    #     # cls_ids = [834]## cls to load
    #     cls_ids =  [834, 1170, 1077, 1166, 1205, 1141, 1136, 1047, 954, 1010, 1030, 960, 951, 976, 1050, 1000, 956,
    #                     946, 841, 845, 931, 941, 927, 823]
    #     all_anns = []
    #     for id in cls_ids:
    #         all_anns.append(pickle.load(open('./fewshot_pasted_anns/{}_anns.pt'.format(id), 'rb')))
    #     all_anns=[ann for subset in all_anns for ann in subset]## flatten the list
    #     fewshot_dataset['annotations']=all_anns
    #
    #     self.logger.info("Creating index on finetune, overwite existing index.")
    #
    #     self.img_ann_map = defaultdict(list)
    #     self.cat_img_map = defaultdict(list)
    #
    #     self.anns = {}
    #     self.cats = {}
    #     self.imgs = {}
    #
    #     for ann in all_anns:
    #         self.img_ann_map[ann["image_id"]].append(ann)
    #         self.anns[ann["id"]] = ann
    #
    #     id_to_train_imgs = {img_info['id']: img_info for img_info in self.dataset["images"]}
    #     get_orig_img_infos = [id_to_train_imgs[ann['orig_image_id']] for ann in all_anns]
    #     for idx, ann in enumerate(all_anns):## replace image_id and filename with fewshot newly annotated ones
    #         get_orig_img_infos[idx]['id'] = ann['image_id']
    #         get_orig_img_infos[idx]['file_name'] = str(ann['image_id']).zfill(12)+'.jpg'
    #
    #     fewshot_dataset['images']=get_orig_img_infos
    #
    #     for img in fewshot_dataset["images"]:
    #         if img['id'] in self.img_ann_map.keys():
    #             self.imgs[img["id"]] = img
    #
    #     for cat in self.dataset["categories"]:
    #         if cat['id'] in cls_ids:
    #             self.cats[cat["id"]] = cat
    #
    #     for ann in fewshot_dataset["annotations"]:
    #         if ann['category_id'] in cls_ids:
    #             self.cat_img_map[ann["category_id"]].append(ann["image_id"])
    #
    #
    # def _create_index_filter(self):
    #
    #     finetune_class_ids = [1047, 243]
    #     self.logger.info("Creating index on finetune, overwite existing index.")
    #
    #     self.img_ann_map = defaultdict(list)
    #     self.cat_img_map = defaultdict(list)
    #
    #     self.anns = {}
    #     self.cats = {}
    #     self.imgs = {}
    #
    #     for ann in self.dataset["annotations"]:
    #         if ann['category_id'] in finetune_class_ids:
    #             self.img_ann_map[ann["image_id"]].append(ann)
    #             self.anns[ann["id"]] = ann
    #
    #     for img in self.dataset["images"]:
    #         if img['id'] in self.img_ann_map.keys():
    #             self.imgs[img["id"]] = img
    #
    #     for cat in self.dataset["categories"]:
    #         self.cats[cat["id"]] = cat
    #
    #     for ann in self.dataset["annotations"]:
    #         if ann['category_id'] in finetune_class_ids:
    #             self.cat_img_map[ann["category_id"]].append(ann["image_id"])
    #
    #     self.logger.info("Index created.")
    #
    # def _create_index_finetune(self):## when used in evaluation on val set, only eval on finetune classes existed imgs,
    #     #  for speed up evaluation, but also has not count false pos on other imgs, so would be higher than regular result
    #     # can consider add neg imgs, and should be same as normal result
    #
    #     import pickle
    #     zero_ap_classes = pickle.load(open('./zero_ap_classes_mrcnnr50_boxmask_ag.pt', 'rb'))
    #     finetune_class_ids = [item['id'] for item in zero_ap_classes if item['instance_count'] > 100]
    #
    #     # finetune_class_ids = [1047, 243]
    #     finetune_class_ids = [834, 1170, 1077, 1166, 1205, 1141, 1136, 1047, 954, 1010, 1030, 960, 951, 976, 1050, 1000, 956,
    #      946, 841, 845, 931, 941, 927, 823]
    #     self.logger.info("Creating index on finetune, overwite existing index.")
    #
    #     self.img_ann_map = defaultdict(list)
    #     self.cat_img_map = defaultdict(list)
    #
    #     self.anns = {}
    #     self.cats = {}
    #     self.imgs = {}
    #     ## try directly fine tune on val annotation for a sanity check
    #     # self.dataset = self._load_json('data/lvis/lvis_v0.5_val.json')
    #
    #
    #     for ann in self.dataset["annotations"]:
    #         if ann['category_id'] in finetune_class_ids:
    #             self.img_ann_map[ann["image_id"]].append(ann)
    #             self.anns[ann["id"]] = ann
    #
    #     for img in self.dataset["images"]:
    #         if img['id'] in self.img_ann_map.keys():
    #             self.imgs[img["id"]] = img
    #
    #     for cat in self.dataset["categories"]:
    #         # if cat['id'] in finetune_class_ids:
    #         self.cats[cat["id"]] = cat
    #
    #     for ann in self.dataset["annotations"]:
    #         if ann['category_id'] in finetune_class_ids:
    #             self.cat_img_map[ann["category_id"]].append(ann["image_id"])
    #
    #     self.logger.info("Index created.")

    def _create_index(self):
        self.logger.info("Creating index.")

        self.img_ann_map = defaultdict(list)
        self.cat_img_map = defaultdict(list)

        self.anns = {}
        self.cats = {}
        self.imgs = {}

        for ann in self.dataset["annotations"]:
            self.img_ann_map[ann["image_id"]].append(ann)
            self.anns[ann["id"]] = ann

        for img in self.dataset["images"]:
            self.imgs[img["id"]] = img

        for cat in self.dataset["categories"]:
            self.cats[cat["id"]] = cat

        for ann in self.dataset["annotations"]:
            self.cat_img_map[ann["category_id"]].append(ann["image_id"])

        self.logger.info("Index created.")

    def get_ann_ids(self, img_ids=None, cat_ids=None, area_rng=None):
        """Get ann ids that satisfy given filter conditions.

        Args:
            img_ids (int array): get anns for given imgs
            cat_ids (int array): get anns for given cats
            area_rng (float array): get anns for a given area range. e.g [0, inf]

        Returns:
            ids (int array): integer array of ann ids
        """
        anns = []
        if img_ids is not None:
            for img_id in img_ids:
                anns.extend(self.img_ann_map[img_id])
        else:
            anns = self.dataset["annotations"]

        # return early if no more filtering required
        if cat_ids is None and area_rng is None:
            return [_ann["id"] for _ann in anns]

        cat_ids = set(cat_ids)

        if area_rng is None:
            area_rng = [0, float("inf")]

        ann_ids = [
            _ann["id"]
            for _ann in anns
            if _ann["category_id"] in cat_ids
            and _ann["area"] > area_rng[0]
            and _ann["area"] < area_rng[1]
        ]
        return ann_ids

    def get_cat_ids(self):
        """Get all category ids.

        Returns:
            ids (int array): integer array of category ids
        """
        return list(self.cats.keys())

    def get_img_ids(self):
        """Get all img ids.

        Returns:
            ids (int array): integer array of image ids
        """
        return list(sorted(self.imgs.keys()))
        # return list(self.imgs.keys())

    def _load_helper(self, _dict, ids):
        if ids is None:
            return list(_dict.values())
        else:
            return [_dict[id] for id in ids]

    def load_anns(self, ids=None):
        """Load anns with the specified ids. If ids=None load all anns.

        Args:
            ids (int array): integer array of annotation ids

        Returns:
            anns (dict array) : loaded annotation objects
        """
        return self._load_helper(self.anns, ids)

    def load_cats(self, ids):
        """Load categories with the specified ids. If ids=None load all
        categories.

        Args:
            ids (int array): integer array of category ids

        Returns:
            cats (dict array) : loaded category dicts
        """
        return self._load_helper(self.cats, ids)

    def load_imgs(self, ids):
        """Load categories with the specified ids. If ids=None load all images.

        Args:
            ids (int array): integer array of image ids

        Returns:
            imgs (dict array) : loaded image dicts
        """
        return self._load_helper(self.imgs, ids)

    def download(self, save_dir, img_ids=None):
        """Download images from mscoco.org server.
        Args:
            save_dir (str): dir to save downloaded images
            img_ids (int array): img ids of images to download
        """
        imgs = self.load_imgs(img_ids)

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for img in imgs:
            file_name = os.path.join(save_dir, img["file_name"])
            if not os.path.exists(file_name):
                urlretrieve(img["coco_url"], file_name)

    def ann_to_rle(self, ann):
        """Convert annotation which can be polygons, uncompressed RLE to RLE.
        Args:
            ann (dict) : annotation object

        Returns:
            ann (rle)
        """
        img_data = self.imgs[ann["image_id"]]
        h, w = img_data["height"], img_data["width"]
        segm = ann["segmentation"]
        if isinstance(segm, list):
            # polygon -- a single object might consist of multiple parts
            # we merge all parts into one mask rle code
            rles = mask_utils.frPyObjects(segm, h, w)
            rle = mask_utils.merge(rles)
        elif isinstance(segm["counts"], list):
            # uncompressed RLE
            rle = mask_utils.frPyObjects(segm, h, w)
        else:
            # rle
            rle = ann["segmentation"]
        return rle

    def ann_to_mask(self, ann):
        """Convert annotation which can be polygons, uncompressed RLE, or RLE
        to binary mask.
        Args:
            ann (dict) : annotation object

        Returns:
            binary mask (numpy 2D array)
        """
        rle = self.ann_to_rle(ann)
        return mask_utils.decode(rle)

    def showanns(self, anns):
        """
        Display the specified annotations.
        :param anns (array of object): annotations to display
        :return: None
        """
        if len(anns) == 0:
            return 0
        if 'segmentation' in anns[0] or 'keypoints' in anns[0]:
            datasetType = 'instances'
        elif 'caption' in anns[0]:
            datasetType = 'captions'
        else:
            raise Exception('datasetType not supported')
        if datasetType == 'instances':
            ax = plt.gca()
            ax.set_autoscale_on(False)
            polygons = []
            color = []
            for ann in anns:
                c = (np.random.random((1, 3))*0.6+0.4).tolist()[0]
                if 'segmentation' in ann:
                    if type(ann['segmentation']) == list:
                        # polygon
                        for seg in ann['segmentation']:
                            poly = np.array(seg).reshape((int(len(seg)/2), 2))
                            polygons.append(Polygon(poly))
                            color.append(c)
                    else:
                        # mask
                        raise NotImplementedError
            p = PatchCollection(polygons, facecolor=color, linewidths=0, alpha=0.4)
            ax.add_collection(p)
            p = PatchCollection(polygons, facecolor='none', edgecolors=color, linewidths=2)
            ax.add_collection(p)
        elif datasetType == 'captions':
            raise NotImplementedError