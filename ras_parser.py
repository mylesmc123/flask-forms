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

def getDSSPaths(lines):
    # Get lines with 'DSS Filename'
    dss_file_lines= [[i,v] for i,v in enumerate(lines) if "DSS File" in v]
    
    # Get dss pathnames for each dss_file_line
    dss_file_and_paths = []
    for dss_file_line in dss_file_lines:
        # The line in the u file with a dss pathname is always +1 lines from the line specifying the DSS File.
        dss_pathname = lines[dss_file_line[0]+1]
        # Create a list of lists containing just the [[DSS Files, DSS Pathnames]]
        dss_file_and_paths.append([dss_file_line[1],dss_pathname])    

    return dss_file_and_paths

def parse_prj(prj_file, prj_name, wkt, plan_titles, output_dir):
    output_prj_yaml = os.path.join(output_dir, f'{prj_name}_ras_prj.yml')

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

    # Add spatial_extent from wkt
    keyValues_dict["spatial_extent"] = wkt

    # Add plan titles
    keyValues_dict["Plans"] = plan_titles


    with open(output_prj_yaml, 'w+') as f:
        yaml.dump(keyValues_dict, f)


def parse_shp(shp, prj_name, output_dir):
    gdf = gpd.read_file(shp)
    gdf = gdf.to_crs(4326)
    wkt = gdf.to_wkt().geometry[0]
    wkt_dict = {}
    wkt_dict["spatial_extent"] = wkt

    with open(os.path.join(output_dir, f'{prj_name}_ras_wkt.yml'), 'w+') as f:
        yaml.dump(wkt_dict, f)
    
    return wkt


def get_p_files(prj_dir, prj_name):
    # prj = 'Z:\Amite\Amite_LWI\Models\Amite_RAS\Amite_2022.prj'
    # prj_dir, prj_file_tail = os.path.split(prj)
    # prj_name = prj_file_tail.split(".")[0]
    pList = []

    for pFile in glob.glob(r'Z:\Amite\Amite_LWI\Models\Amite_RAS\*.p' + '[0-9]' * 2):
        prj_dir, p_file_tail = os.path.split(pFile)
        p_file_prj_name = p_file_tail.split(".")[0]
        if p_file_prj_name == prj_name:
            pList.append(pFile)

    return pList


def parse_p(p_file_list, prj_name, wkt, output_dir):
    plan_titles = []
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
        
        # Add spatial_extent from wkt
        keyValues_dict["spatial_extent"] = wkt

        # Get associated geometry file
        geom_file_extension = keyValues_dict['Geom File']
        geom_file = os.path.join(prj_dir, prj_name +"."+ geom_file_extension)
        with open(geom_file, "r") as f:
            geom_lines = f.readlines()
        geom_lines = [s.strip('\n') for s in geom_lines]

        # Create Dictionary
        geom_keyValues_dict, geom_popList = trimKeyValuePairsToDict(geom_lines)

        # Add Specified key value pairs from geom file to p file.
        keyValues_dict['Geom Title'] = geom_keyValues_dict['Geom Title']

        # Get associated u flow file
        flow_file_extension = keyValues_dict['Flow File']
        flow_file = os.path.join(prj_dir, prj_name +"."+ flow_file_extension)
        with open(flow_file, "r") as f:
            flow_lines = f.readlines()
        flow_lines = [s.strip('\n') for s in flow_lines]

        # Create Dictionary
        flow_keyValues_dict, flow_popList = trimKeyValuePairsToDict(flow_lines)

         # Get Input DSS files and paths from flow file to p file.
        dss_file_and_paths = getDSSPaths(flow_lines)
        keyValues_dict['DSS Input Files'] = dss_file_and_paths

        # Add Specified key value pairs from flow file to p file.
        keyValues_dict['Flow Title'] = flow_keyValues_dict['Flow Title']

        # Append plan title list
        plan_titles.append(keyValues_dict['Plan Title'])   

        # Write the output yaml for each .p## file.
        with open(os.path.join(output_dir,f'{p_file_tail}.yml'), 'w+') as f:
            yaml.dump(keyValues_dict, f)

    return plan_titles

def create_yaml(prj_yaml, p_yaml, u_yaml):
    return None

def parse(prj, shp):
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'output')
    prj_dir, prj_file_tail = os.path.split(prj)
    prj_name = prj_file_tail.split(".")[0]

    print (f'Extracting Spatial Extent as WKT from shapefile: {shp}') 
    wkt = parse_shp(shp, prj_name, output_dir)

    # print (f'\nParsing prj file to: {output_prj_yaml}\n')
   

    # get p files in prj_dir
    p_file_list = get_p_files(prj_dir, prj_name)
    # parse p files and include data from geometry and flow files. returns the plan titles.
    plan_titles = parse_p(p_file_list, prj_name, wkt, output_dir)

    # parse prj and add list of p file titles to prj yaml
    parse_prj(prj, prj_name, wkt, plan_titles, output_dir)

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