#!/user/bin/env python3
# -*- encoding: utf-8 -*-
'''
Created on Wed March 17 18:41:55 2021

@Author: LewisLiu
@Description: It is to build a sample of iris excel format data based on turbine data.
'''

import json_op
import copy
from pandas import DataFrame, read_csv
import pandas as pd
import math
import argparse

STANDARDIMGWIDTH = 300
STANDARDIMGHEIGHT = 200
K_IMG_WIDTH = 640 #* 640
K_IMG_HEIGHT = 426 #* 426
K_PIX_PER_METER = 300  #* from 3D part
FULLIMAGEWIDTH = 5456
FULLIMAGEHEIGHT = 3632

COMPONENT_SIDE=["PS_LE", "PS_TE", "SS_TE", "SS_LE", "LE", "PS", "TE", "SS"]


class DataFormatGenerate:
    def __init__(self):
        self.turbine_dto = None
        self.output_xlsx_path = None

        self.images_format_data = None
        self.defects_format_data = None

        self.images_data_frame = None
        self.defects_data_frame = None


    def load(self, turbine_dto, output_xlsx_path):
        self.turbine_dto = turbine_dto
        self.output_xlsx_path = output_xlsx_path
        self.paths = turbine_dto["turbine"]["paths"]

        self._init_data()

    def run(self):
        cur_image_format_data = {}
        cur_defect_format_data = {}

        #* windfarm and turbine information
        cur_image_format_data["Site_name"] = self.turbine_dto["turbine"]["windFarmName"] if "windFarmName" in self.turbine_dto["turbine"] else ""
        cur_image_format_data["Site GPS coordinate"] = self._get_site_gps()
        cur_image_format_data["Site country"] = ""
        cur_image_format_data["Asset Serial no."] = ""
        cur_image_format_data["Asset_ID"] = ""
        cur_image_format_data["Asset GPS koordinate"] = ""
        cur_image_format_data["RDS PP code"] = ""
        cur_image_format_data["Asset type"] = ""
        cur_image_format_data["Asset/Tower height"] = ""

        for cur_path in self.paths:
            self._format_path(cur_path, cur_image_format_data, cur_defect_format_data)

        #* build images data frame
        self._build_images_data_frame()
        images_df = pd.DataFrame(self.images_data_frame)

        #* build defects data frame
        self._build_defects_data_frame()
        defects_df = pd.DataFrame(self.defects_data_frame)

        #* store to xlsx
        with pd.ExcelWriter(self.output_xlsx_path) as writer:
            images_df.to_excel(writer, sheet_name="Processed image data", index=False)
            defects_df.to_excel(writer, sheet_name="defects data", index=False)


    def _format_path(self, path, cur_image_format_data, cur_defect_format_data):
        #* blade information
        cur_image_format_data["Asset_ID"] = path["path"]["turbineId"]
        cur_image_format_data["Component_ID_abc/123"] = path["path"]["bladeName"]
        cur_image_format_data["Component Serial Number"] = path["path"]["bladeId"]
        cur_image_format_data["Component type"] = ""
        cur_image_format_data["Component length"] = self.turbine_dto["turbine"]["bladeRealLenth"]
        cur_image_format_data["Component max width"] = self._get_chord_max_length(path)
        cur_image_format_data["Component_side"] = COMPONENT_SIDE[path["path"]["viewIndex"]-1]
        cur_image_format_data["Inspection company"] = ""
        cur_image_format_data["Requestor of inspecton"] = ""
        cur_image_format_data["inspection company Project reference no."] = path["path"]["inspectionId"]
        cur_image_format_data["Inspector name"] = ""
        cur_image_format_data["Inspection Type"] = ""
        cur_image_format_data["Equipment serial no."] = ""
        cur_image_format_data["date"] = path["path"]["inspectionDate"]

        path["images"].sort(key=lambda img_info: img_info["sortIndex"], reverse=True)
        for image in path["images"]:
            self._format_image(image, cur_image_format_data, cur_defect_format_data)
            self.images_format_data.append(copy.deepcopy(cur_image_format_data))

    def _format_image(self, image, cur_image_format_data, cur_defect_format_data):
        #* image information
        tf_2D = {
            "x": image["stitchingData"]["x"] + image["stitchingData"]["panoramaOffsetX"] if image["stitchingData"]["panoramaOffsetX"] is not None else image["stitchingData"]["x"],
            "y": image["stitchingData"]["y"] + image["stitchingData"]["panoramaOffsetY"] if image["stitchingData"]["panoramaOffsetY"] is not None else image["stitchingData"]["y"],
            "scale": image["stitchingData"]["scale"],
            "rotation": image["stitchingData"]["rotation"],
            "imgWidth": image["stitchingData"]["imgWidth"],
            "imgHeight": image["stitchingData"]["imgHeight"]
            }
        tf_3D = self._change_2DTF_to_3DTF(tf_2D)

        cur_image_format_data["Y axis (vertical)"] = round(tf_3D["y"], 3)
        cur_image_format_data["X axis (horizontal)"] = round(tf_3D["x"], 3)
        cur_image_format_data["Rotation of image"] = round(tf_3D["rotation"],2)
        cur_image_format_data["Pixel size"] = round(1.0 * FULLIMAGEWIDTH / (tf_3D["imgWidth"] * 1000), 2)
        cur_image_format_data["Image ID"] = image["imgId"]
        cur_image_format_data["Image URL"] = image["uri"]

        #* defects information
        for defect in image["defects"]:
            self._format_defect(defect, cur_image_format_data, cur_defect_format_data)
            self.defects_format_data.append(copy.deepcopy(cur_defect_format_data))

    def _format_defect(self, defect, cur_image_format_data, cur_defect_format_data):
        cur_defect_format_data["Unique Defect ID"] = defect["defectLocalId"]
        cur_defect_format_data["Defect type"] = defect["defectTypeName"]
        cur_defect_format_data["Affected Layer"] = defect["defectLayer"]
        cur_defect_format_data["Severity Category"] = int(defect["defectLevel"].split("Lv")[-1])
        cur_defect_format_data["Y axis (vertical)"] = cur_image_format_data["Y axis (vertical)"]
        cur_defect_format_data["X axis (horizontal)"] = cur_image_format_data["X axis (horizontal)"]
        cur_defect_format_data["Rotation of image"] = cur_image_format_data["Rotation of image"]
        cur_defect_format_data["Pixel size"] = cur_image_format_data["Pixel size"]
        cur_defect_format_data["Coordinates of label corners"] = self._get_label_corners(defect)
        cur_defect_format_data["Width of defect [mm]"], cur_defect_format_data["Length of defect [mm]"] = self._get_defect_size(defect)
        cur_defect_format_data["Image ID reference"] = cur_image_format_data["Image ID"]


    def _init_data(self):
        self.images_format_data = []
        self.defects_format_data = []
        #*init processed image data
        self.images_data_frame = {
            "Site_name":[],
            "Site GPS coordinate":[],
            "Site country":[],
            "Asset Serial no.":[],
            "Asset_ID":[],
            "Asset GPS koordinate":[],
            "RDS PP code":[],
            "Asset type":[],
            "Asset/Tower height":[],
            "Component_ID_abc/123":[],
            "Component Serial Number":[],
            "Component type":[],
            "Component length":[],
            "Component max width":[],
            "Component_side":[],
            "Inspection company":[],
            "Requestor of inspecton":[],
            "inspection company Project reference no.":[],
            "Inspector name":[],
            "Inspection Type":[],
            "Equipment serial no.":[],
            "date":[],
            "Y axis (vertical)":[],
            "X axis (horizontal)":[],
            "Rotation of image":[],
            "Pixel size":[],
            "Image ID":[],
            "Image URL":[]
        }

        #* init defect data
        self.defects_data_frame = {
            "Unique Defect ID":[],
            "Defect type":[],
            "Affected Layer":[],
            "Severity Category":[],
            "Y axis (vertical)":[],
            "X axis (horizontal)":[],
            "Rotation of image":[],
            "Pixel size":[],
            "Coordinates of label corners":[],
            "Width of defect [mm]":[],
            "Length of defect [mm]":[],
            "Image ID reference":[]
        }

    def _build_images_data_frame(self):
        for i, image_format_data in enumerate(self.images_format_data):
            for key in self.images_data_frame.keys():
                self.images_data_frame[key].append(image_format_data[key])

    def _build_defects_data_frame(self):
        for i, defect_format_data in enumerate(self.defects_format_data):
            for key in self.defects_data_frame.keys():
                self.defects_data_frame[key].append(defect_format_data[key])

    def _get_site_gps(self):
        if len(self.turbine_dto["turbine"]["paths"]) <= 0: return ""
        if len(self.turbine_dto["turbine"]["paths"][0]["images"]) <= 0: return ""
        image_0 = self.turbine_dto["turbine"]["paths"][0]["images"][0]
        
        longitude = image_0["metadata"]["drone"]["longitude"]
        latitude = image_0["metadata"]["drone"]["latitude"]
        if longitude <= 0 and latitude <= 0:
            return ""
        else:
            return "{},{}".format(longitude, latitude)

    def _get_chord_max_length(self, path):
        '''
        Only V4.0 Data has it now.
        It is stored in  path["bladeHyperParaUri"] -> bladeHyper["A"]["hyperPara"] -> Array of ChordLen"
        It's better to calculate the max length directly and store the max length into one key directly.
        '''
        return ""


    def _change_2DTF_to_3DTF(self, tf_2D):
        '''
        -- Change 2D's tf to 3D's tf
        -- For 3D result's tf, the scale is the width of image (meters), the x,y is the center of image.
        -- For 2D's tf, the scale is the scale ratio of image, the x,y is the zero point(left-top) of image
        '''
        tf_3D = copy.deepcopy(tf_2D)
        tf_3D['rotation'] = tf_2D['rotation']

        # * change from pixels to meters
        tf_2D['x'] = 1.0 * tf_2D['x'] * K_IMG_WIDTH / (K_PIX_PER_METER * STANDARDIMGWIDTH)
        tf_2D['y'] = 1.0 * tf_2D['y'] * K_IMG_WIDTH / (K_PIX_PER_METER * STANDARDIMGWIDTH)

        tf_3D['imgWidth'] = 1.0 * tf_2D['imgWidth'] * K_IMG_WIDTH / (K_PIX_PER_METER * STANDARDIMGWIDTH)
        tf_3D['imgHeight'] = 1.0 * tf_2D['imgHeight'] * K_IMG_WIDTH / (K_PIX_PER_METER * STANDARDIMGWIDTH)

        dst_pt = self._cal_dstpt_from_refpt(tf_3D["imgWidth"], tf_3D["imgHeight"], tf_2D["rotation"], [tf_2D['x'], tf_2D['y']],
                                            [0.5, 0.5], [0, 0])
        tf_3D['x'] = dst_pt[0]
        tf_3D['y'] = dst_pt[1]

        tf_3D['scale'] = 1.0

        return tf_3D
    
    #* calculate dstPT in transformation image based on center pt who has been transferred.
    def _cal_dstpt_from_refpt(self, img_width, img_height, rotation, ref_pt, dst_pt_in_img=[0, 0], ref_pt_in_img=[0.5, 0.5]):
        cos = math.cos(math.radians(rotation))
        sin = math.sin(math.radians(rotation))

        dst_pt = [0, 0]
        dst_pt[0] = ref_pt[0] + (dst_pt_in_img[0] - ref_pt_in_img[0]) * (img_width * cos - img_height * sin)
        dst_pt[1] = ref_pt[1] + (dst_pt_in_img[1] - ref_pt_in_img[1]) * (img_width * sin + img_height * cos)

        return dst_pt
    
    def _get_label_corners(self, defect):
        points = []
        for i, point in enumerate(defect["polygonalPoints"]):
            cur_x = int(point["x"] * FULLIMAGEWIDTH)
            cur_y = int(point["y"] * FULLIMAGEHEIGHT)
            points.append([cur_x, cur_y])

        return points

    def _get_defect_size(self, defect):
        if defect["bboxSize"]["w"] > 0 and defect["bboxSize"]["l"] > 0:
            return defect["bboxSize"]["w"] * 1000, defect["bboxSize"]["l"] * 1000

        defect_size = defect["defectSize"]
        defect_size_lw = defect_size.split("*")
        defect_size_l, defect_size_w = defect_size_lw[0].split("m")[0], defect_size_lw[1].split("m")[0]
        print(defect_size_w, defect_size_l)
        return defect_size_w, defect_size_l

def file_2_json(file_path):
    json_data = None
    with open(file_path, "r") as fp:
        json_data = json.load(fp)

    fp.close()

    return json_data

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("json_path", help="the turbine json from which to generate Excel Format Data.")
    p.add_argument("-o", "--output_xlsx_path", default="iris_4.0_excel_format_data.xlsx")
    args = p.parse_args()

    data_format_generate = DataFormatGenerate()
    
    turbine_json_path = args.json_path
    output_xlsx_path = args.output_xlsx_path

    turbine_json = json_op.file_2_json(turbine_json_path)    
    data_format_generate.load(turbine_json, output_xlsx_path)
    data_format_generate.run()