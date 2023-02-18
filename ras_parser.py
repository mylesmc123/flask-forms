import glob
import copy
import yaml
import os
import argparse
import geopandas as gpd

def trimKeyValuePairsToDict(lines):

    keyValueList = copy.deepcopy(lines)  
    # Create a pop list of indices to remove because missing key=value pairs.
    popList = []
    
    for i,v in enumerate(keyValueList):
        if '=' not in v:
            popList.append(i)
    
    # Remove indices in popList
    for index in sorted(popList, reverse=True):
        del keyValueList[index]

    # Create dictionary from trimmed list
    keyValues_dict = dict(s.split('=',1) for s in keyValueList)
    
    return keyValues_dict, popList


def parse_prj(prj_file, output_prj_yaml):

    with open(prj_file, "r") as f:
        lines = f.readlines()
    
    lines = [s.strip('\n') for s in lines]
    
    # keyValueList = copy.deepcopy(lines)
    # # Create a pop list of indices to remove because missing key=value pairs.
    # popList = []
    # for i,v in enumerate(lines):
    #     if '=' not in v:
    #         popList.append(i)
    
    # # Remove indices in popList
    # for index in sorted(popList, reverse=True):
    #     del keyValueList[index]
    
    # keyValues_dict = dict(s.split('=',1) for s in keyValueList)
    keyValues_dict, popList = trimKeyValuePairsToDict(lines)

    # Add specific popList lines from prj file to keyValue_dict
    for i,v in enumerate(popList):
        if "BEGIN DESCRIPTION:" in lines[v]:
            description = lines[v+1]

    keyValues_dict['Description'] = description

    with open(output_prj_yaml, 'w+') as f:
        yaml.dump(keyValues_dict, f)


def parse_shp(shp, output_wkt_yaml):
    gdf = gpd.read_file(shp)
    gdf = gdf.to_crs(4326)
    wkt = gdf.to_wkt().geometry[0]
    wkt_dict = {}
    wkt_dict["spatial_extent"] = wkt

    with open(output_wkt_yaml, 'w+') as f:
        yaml.dump(wkt_dict, f)


def get_p_files(prj_dir):
    prj = 'Z:\Amite\Amite_LWI\Models\Amite_RAS\Amite_2022.prj'
    prj_dir, prj_file_tail = os.path.split(prj)
    prj_name = prj_file_tail.split(".")[0]
    pList = []

    for pFile in glob.glob(r'Z:\Amite\Amite_LWI\Models\Amite_RAS\*.p' + '[0-9]' * 2):
        prj_dir, p_file_tail = os.path.split(pFile)
        p_file_prj_name = p_file_tail.split(".")[0]
        if p_file_prj_name == prj_name:
            pList.append(pFile)

    return pList


def parse_p(p_file_list, output_dir):
    for p in p_file_list:
        # print (p)
        prj_dir, p_file_tail = os.path.split(p)
        print (p_file_tail)
        with open(p, "r") as f:
            # print(f.readlines())
            lines = f.readlines()
        
        lines = [s.strip('\n') for s in lines]

        # Create Dictionary
        keyValues_dict, popList = trimKeyValuePairsToDict(lines)

        # Add specific popList lines from prj file to keyValue_dict
        for i,v in enumerate(popList):
            if "BEGIN DESCRIPTION:" in lines[v]:
                description = lines[v+1]
                keyValues_dict['Description'] = description

        # Get associated geometry file
        prj_name = p_file_tail.split(".")[0]
        geom_file_extension = keyValues_dict['Geom File']
        geom_file = os.path.join(prj_dir, prj_name +"."+ geom_file_extension)
        with open(geom_file, "r") as f:
            geom_lines = f.readlines()
        geom_lines = [s.strip('\n') for s in geom_lines]

        # Create Dictionary
        geom_keyValues_dict, geom_popList = trimKeyValuePairsToDict(geom_lines)

        # Add Specified key value pairs from geom file to p file.
        keyValues_dict['Geom Title'] = geom_keyValues_dict['Geom Title']

        # Get associated flow file
        flow_file_extension = keyValues_dict['Flow File']
        flow_file = os.path.join(prj_dir, prj_name +"."+ flow_file_extension)
        with open(flow_file, "r") as f:
            flow_lines = f.readlines()
        flow_lines = [s.strip('\n') for s in flow_lines]

        # Create Dictionary
        flow_keyValues_dict, flow_popList = trimKeyValuePairsToDict(flow_lines)

        # Add Specified key value pairs from geom file to p file.
        keyValues_dict['Flow Title'] = flow_keyValues_dict['Flow Title']

        # Write the output yaml for each .p## file.
        with open(os.path.join(output_dir,f'{p_file_tail}.yml'), 'w+') as f:
            yaml.dump(keyValues_dict, f)

    

def parse_u(prj_file):
    u_yaml = None
    return u_yaml

def create_yaml(prj_yaml, p_yaml, u_yaml):
    return None

def parse(prj, shp):

    output_prj_yaml = 'output/ras_prj.yml'
    print (f'\nParsing prj file to: {output_prj_yaml}\n')
    # parse_prj(prj, output_prj_yaml)
    
    print (f'Extracting Spatial Extent as WKT from shapefile: {shp}') 
    output_wkt_yaml = 'output/ras_wkt.yml'
    # parse_shp(shp, output_wkt_yaml)

    prj_dir, prj_file_tail = os.path.split(prj)

    # get p files in prj_dir
    p_file_list = get_p_files(prj_dir)
    print ('\n.p files found in prj_dir: ',p_file_list)
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'output')
    parse_p(p_file_list, output_dir)

    # u_yaml = parse_u(prj_dir)
    # create_yaml(prj_yaml, p_yaml, u_yaml)

if __name__ == '__main__':
    # Parse Command Line Arguments
    p = argparse.ArgumentParser(description="HEC-RAS metadata extraction.")
    
    p.add_argument(
    "--prj", help="The HEC-RAS project file. (Ex: C:\RAS_Models\Amite\Amite_2022.prj)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--shp", help="The HEC-RAS model boundary spatial extent as ESRI shapefile. (Ex: C:\RAS_Models\Amite\Features\Amite_Optimized_Geometry.shp)", 
    required=True, 
    type=str
    )

    args = p.parse_args()
    parse(args.prj, args.shp)