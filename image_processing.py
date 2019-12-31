# Reclassifying Image with Green,Red,NIR band into Image containing Blue,Green and Red Band.


import argparse
import gdal,osr,ogr,glob,os,sys
from tqdm import tqdm
import numpy as np



class main():

    def __init__(self):
        self.input_directory_path=opt.dataset_path
        self.output_directory_path=opt.output_directory_path
        self.output_file_format=opt.output_file_format
        self.datatype={'Byte':gdal.GDT_Byte,'UInt16':gdal.GDT_UInt16,'Int16':gdal.GDT_Int16,'UInt32':gdal.GDT_UInt32,'Int32':gdal.GDT_Int32,'Float32':gdal.GDT_Float32,'Float64':gdal.GDT_Float64}
        self.file_datatype={}
        self.output_file_datatype=None
        self.no_value=0


    def file_creator(self):


        try:
            if opt.output_file_datatype not in ['Byte','UInt16','Int16','UInt32','Int32','Float32','Float64']:
                raise ValueError("output_file_datatype is not valid")

        except ValueError as ve:
            print(ve)
            sys.exit(0)

        try:
            if opt.output_file_datatype in self.datatype.keys():
                self.output_file_datatype = self.datatype[opt.output_file_datatype]
            else:
                raise ValueError("output_file_datatype is not valid")

        except ValueError as ve:
            print (ve)
            sys.exit(0)


        try:
            if os.path.exists(self.input_directory_path):
                os.chdir(self.input_directory_path)
            else:
                raise ValueError("Specified Path Does Not Exist")
        except ValueError as ve:
            print(self.input_directory_path," : ",ve)
            sys.exit(0)



        for i in tqdm(glob.glob('*.img')):

            try:
                if i is None:
                    raise ValueError("FOLDER DOES NOT CONTAIN FILE WITH IMG EXTENSION")

            except ValueError as ve:
                print(ve)
                sys.exit(0)

            try:
                raster = gdal.Open(os.path.join(self.input_directory_path,i))
            except ValueError ("DATA is invalid"):
                continue
            geotransform = raster.GetGeoTransform()
            originX = geotransform[0]
            originY = geotransform[3]
            pixelWidth = geotransform[1]
            pixelHeight = geotransform[5]
            li = [raster.GetRasterBand(i + 1).ReadAsArray() for i in range(raster.RasterCount)]
            li[0][np.isnan(li[0])] = 0 # Replace all Nan values in the band with 0
            li[1][np.isnan(li[1])] = 0 # Replace all Nan values in the band with 0
            li[2][np.isnan(li[2])] = 0 # Replace all Nan values in the band with 0

            # green band in the original image is replaced as Blue band (BAND 1)

            # formulae for changing NIR band in the original image as green band (in converted image) is [(3*Green band)+NIR]/4 ((BAND 2)

            # Red band in the original image is kept as it is in the new image (BAND 3)

            mi = [li[0], (3 * li[0] + li[2]) / 4, li[1]]
            rows = li[0].shape[0]
            cols = li[0].shape[1]
            driver = gdal.GetDriverByName(self.output_file_format)
            outpath=self.output_directory_path+"/"+i.split('.')[0]+'.tif'
            outRaster = driver.Create(outpath, cols, rows, 3, self.output_file_datatype)
            outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
            for i in range(len(mi)):
                outband = outRaster.GetRasterBand(i + 1)
                outband.WriteArray(mi[i])
                outRasterSRS = osr.SpatialReference()
                outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
                outRaster.SetProjection(outRasterSRS.ExportToWkt())
                outband.FlushCache()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default=None,
                        help="path of the directory where image dataset is stored")
    parser.add_argument("--output_directory_path", type=str, default=None,
                        help="path of the directory where converted dataset is to be stored")
    parser.add_argument("--output_file_format", type=str, default='GTiff', help="GTiff")
    parser.add_argument("--output_file_datatype", type=str, default='Byte', help="Byte,UInt16,Int16,UInt32,Int32,Float32,Float64")
    opt = parser.parse_args()
    a=main()
    a.file_creator()













