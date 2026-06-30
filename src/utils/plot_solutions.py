# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 12:51:57 2024.

@author: James Mckenna

~~~ plot_solutions.py ~~~
Control object used to plot flood maps for the final solutions produced by a
evolutionary algorithm.
"""

# load packages
import matplotlib.pyplot as plt
import gc
from osgeo import gdal, osr
from shapely.geometry import LineString
import geopandas as gpd
import pandas as pd
import glob
import os
import rasterio as rio
import matplotlib as mpl
from matplotlib.patches import Patch
from matplotlib.patches import Circle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from rasterio.plot import show
import numpy as np
import csv
from .binary_encoding import binary_coder, binary_to_sim_integer


###############################################################################
# Helper Functions
###############################################################################


def extract_parameters(file_path):
    """Extract parameters from the parameter file.

    Parameters:
    -----------
    file_path : str
        The path to the parameters.txt file.

    Returns:
    --------
    dict
        A dictionary containing the extracted parameters.
    """
    # Initialise variables to hold the extracted values
    parameters = {
        'number_of_pavements': 0,
        'number_of_gardens': 0,
        'number_of_greenareas': 0,
        'number_of_features': 0,
        'feature_lengths': [],
        'characteristic_lengths': [],
        'total_length': 0,
        'binary_coding': '',
        'objective': '',
    }
    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                key, value = parts[0].strip().lower(), parts[1].strip()
                if 'number of pavements' in key:
                    parameters['number_of_pavements'] = int(value)  # integer
                elif 'number of rain gardens' in key:
                    parameters['number_of_gardens'] = int(value)  # integer
                elif 'number of green areas' in key:
                    parameters['number_of_greenareas'] = int(value)  # integer
                elif 'number of features' in key:
                    parameters['number_of_features'] = int(value) # integer
                elif 'total encoding length' in key:
                    parameters['total_length'] = int(value)  # integer
                elif 'binary coding' in key:
                    parameters['binary_coding'] = str(value)  # string
                elif 'objective' in key:
                    parameters['objective'] = str(value)  # string

    return parameters


def read_txt_to_dataframe(file_path):
    """Read a pavements .txt file and extract lines.

    Parameters
    ----------
    file_path : str
        Path to the .txt file containing the coordinates. The file should have
        each line starting with an ID followed by space-separated X and Y
        coordinate pairs.

    Returns
    -------
    df : pandas.DataFrame
        A pandas DataFrame containing the extracted coordinate data with
        columns:
        - 'ID': The ID for each line.
        - 'geometry': Shapely LineString geometry for each line.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Initialize lists to store data
    ids = []
    geometries = []
    for line in lines:
        elements = line.split()
        if not elements:
            continue
        try:
            # Some formats might have ID as first element
            id_ = int(elements[0])
            num_points = int(elements[1])
            # Coordinates start after ID and num_points
            coords = list(map(float, elements[2:]))

            # Check if length matches expected x + y
            if len(coords) != num_points * 2:
                # Fallback for alternative format: num_points x1... y1...
                num_points = int(elements[0])
                coords = list(map(float, elements[1:]))
                id_ = num_points  # Use num_points as ID if ID missing

            x_coords = coords[:num_points]
            y_coords = coords[num_points:]

            points = list(zip(x_coords, y_coords))
            if len(points) >= 2:
                line_geom = LineString(points)
                ids.append(id_)
                geometries.append(line_geom)
        except (ValueError, IndexError):
            continue

    df = pd.DataFrame({'ID': ids, 'geometry': geometries})

    return df


def dataframe_to_shapefile(df, output_path):
    """Convert DataFrame to a shapefile.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame containing coordinate data. The DataFrame must have
        'geometry' column representing the LineString geometries.
    output_path : str
        The file path where the output shapefile will be saved. The path should
        end with '.shp'.

    Returns
    -------
    The function saves the shapefile to the specified location and does not
    return any value.
    """
    if not df.empty:
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        gdf.to_file(output_path, driver='ESRI Shapefile')


def read_dem(file_path):
    """Read a DEM file for merging.

    Parameters
    ----------
    file_path : string
        Path to DEM file (.asc).

    Returns
    -------
    dem_array : numpy.ndarray
        2D array representing the elevation values of the DEM.
    geotransform : array
        Affine transformation coefficients for transforming pixel/line
        coordinates to georeferenced space.
    projection : string
        Projection information of the DEM in WKT (Well-Known Text) format.
    """
    dataset = gdal.Open(file_path)
    if dataset is None:
        raise FileNotFoundError(f"GDAL could not open file: {file_path}")
    band = dataset.GetRasterBand(1)
    dem_array = band.ReadAsArray()
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    return (dem_array, geotransform, projection)


def load_features_data(feature_data_path, binary_coding='standard'):
    """Load features data from the tab-delimited .txt file into a list.

    Parameters
    ----------
    feature_data_path : string
        Path to the input feature_data.txt file containing information on the
        features to be optimised.
    binary_coding : string, optional
        Key word string describing the choice of binary coding.
        The default is 'standard'. Options are: 'standard', 'gray' or 'unary'.

    Returns
    -------
    features : list of dict
        A list of dictionaries where each dictionary contains the data for a
        single feature. Each dictionary includes:
            - 'x0', 'y0': float
                Coordinates of the feature origin.
            - 'h_min', 'h_max', 'h_len': float, float, int
                Min/max values and binary encoding length for the raised
                height of the feature.
            - 'r_min', 'r_max', 'r_len': float, float, int
                Min/max values and binary encoding length for radius of the
                feature.
            - 'theta_min', 'theta_max', 'theta_len': float, float, int
                Min/max values and binary encoding length for rotation angle.
            - 'beta_min', 'beta_max', 'beta_len': float, float, int
                Min/max values and binary encoding length for arc angle.
            - 'dx_min', 'dx_max', 'dx_len': float, float, int
                Min/max values and binary encoding length for x-translation of
                the feature origin.
            - 'dy_min', 'dy_max', 'dy_len': float, float, int
                Min/max values and binary encoding length for y-translation of
                the feature origin.
    """
    with open(feature_data_path, 'r') as file:
        header = file.readline().strip().split('\t')
        # force data to be 2D, so a single feature can be optimised
        data = np.atleast_2d(np.loadtxt(file, delimiter='\t'))

    if binary_coding == 'unary':
        def calc_combinations(length):
            """Calculate the number of combinations for the binary coding."""
            return length + 1
    elif binary_coding in ['standard', 'gray']:
        def calc_combinations(length):
            """Calculate the number of combinations for the binary coding."""
            return 2**length
    else:
        raise ValueError('Invalid binary coding specified: {binary_coding}.'
                         "Select from: 'unary', 'standard' or 'gray'")

    def calc_delta(max_val, min_val, length):
        """Calculate the discretisation of the variable.

        Delta_val = (max_val - min_val) / (combinations - 1).

        Parameters
        ----------
        max_val : float
            Maximum permissible value for the variable.
        min_val : float
            Minimum permissible value for the variable.
        length : int
            Length of the binary encoding .

        Returns
        -------
        delta_val : float
            The discretisation of the variable, equal to the jump in the value
            of the variable between consecutive codings.
        """
        return (max_val - min_val) / (calc_combinations(length) - 1)

    features = []
    for row in data:
        feature = {
            'x0': row[1],
            'y0': row[2],
            'h_min': row[3],
            'h_max': row[4],
            'h_len': int(row[5]),
            'delta_h': calc_delta(row[4], row[3], int(row[5])),
            'r_min': row[6],
            'r_max': row[7],
            'r_len': int(row[8]),
            'delta_r': calc_delta(row[7], row[6], int(row[8])),
            'dx_min': row[9],
            'dx_max': row[10],
            'dx_len': int(row[11]),
            'delta_dx': calc_delta(row[10], row[9], int(row[11])),
            'dy_min': row[12],
            'dy_max': row[13],
            'dy_len': int(row[14]),
            'delta_dy': calc_delta(row[13], row[12], int(row[14]))
        }
        features.append(feature)

    return features


def get_representation_data(filename):
    """Read feature data and compute total representation length per feature.

    Parameters
    ----------
    filename : str
        Path to feature_data.txt file.

    Returns
    -------
    total_lengths : list of int
        List containing total binary representation length for each feature.
    total_length : int
        Sum of total_lengths.
    characteristic_lengths : nested list of ints
        List i contains the representation lengths for each characteristic for
        feature i.
    """
    total_lengths = []
    # representation length for each characteristic for each feature
    characteristic_lengths = []

    with open(filename, "r") as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            # Convert all representation lengths from strings to integers
            delta_h_len = int(row['h_len'])
            r_len = int(row['r_len'])
            dx_len = int(row['dx_len'])
            dy_len = int(row['dy_len'])

            characteristic_lengths.append([delta_h_len, r_len, dx_len, dy_len])

            total_len = delta_h_len + r_len + dx_len + dy_len

            total_lengths.append(total_len)

    total_length = sum(total_lengths)

    return (total_lengths, total_length, characteristic_lengths)


###############################################################################
# Plotter object
###############################################################################


class plot_handler():
    """Read solution data and plot flood extents."""

    def __init__(self, data_path, output_path,
                 number_of_pavements=None, number_of_gardens=None,
                 number_of_greenareas=None, number_of_features=None,
                 total_length=None, binary_coding='gray', objective=None,
                 extension='pdf'):
        """Load data and initialise file paths.

        Parameters
        ----------
        data_path : string
            Path to the relevant data folder where the simulation data is
            stored.
        output_path : string
            Path to the output folder where the and plots are saved.
        number_of_pavements : int, optional
            Number of pavements included in the optimisation. If parameters.txt
            exists then the value is read from the file. Otherwise the input
            value is used. The default value is None (read from file instead).
        number_of_gardens : int, optional
            Number of rain gardens included in the optimisation. If
            parameters.txt exists then the value is read from the file.
            Otherwise the input value is used. The default value is None
            (read from file instead).
        number_of_greenareas : int, optional
            Number of green areas included in the optimisation. If
            parameters.txt exists then the value is read from the file.
            Otherwise the input value is used. The default value is None
            (read from file instead).
        number_of_features : int, optional
            Number of features included in the optimisation. If parameters.txt
            exists then the value is read from the file. Otherwise the input
            value is used. The default value is None (read from file instead).
        total_length : int, optional
            Total length of the binary encoding. If parameters.txt
            exists then the value is read from the file. Otherwise the input
            value is used. The default value is None (read from file instead).
        binary_coding : string, optional
            Key word string describing the choice of binary coding.
            The default is 'gray'. Options are: 'standard', 'gray' or 'unary'.
            If parameters.txt exists then the value is read from the file.
            Otherwise the input value is used.
        objective : string, optional
            Choice of flood risk metric for optimisation. If parameters.txt
            exists then the value is read from the file. Otherwise the input
            value is used. The default value is None (read from file instead).
        extension : string, optional
            Chosen file extension for the output figure. Default value is 'pdf'.
        """
        self.extension = extension
        self.data_path = data_path
        self.run_path = os.path.join(data_path, 'CityCAT_setup')
        self.output_path = output_path
        parameter_path = os.path.join(self.data_path, 'parameters.txt')
        if os.path.exists(parameter_path):
            parameters = extract_parameters(parameter_path)
            self.number_of_pavements = parameters['number_of_pavements']
            self.number_of_gardens = parameters['number_of_gardens']
            self.number_of_greenareas = parameters['number_of_greenareas']
            self.number_of_features = parameters['number_of_features']
            self.total_length = parameters['total_length']
            self.binary_coding = parameters['binary_coding']
            self.objective = parameters['objective']
        else:
            self.number_of_pavements = number_of_pavements
            self.number_of_gardens = number_of_gardens
            self.number_of_greenareas = number_of_greenareas
            self.number_of_features = number_of_features
            self.total_length = total_length
            self.binary_coding = binary_coding
            self.objective = objective

        self.solution_path = os.path.join(self.data_path, 'solutions.txt')
        dem_file_path = os.path.join(self.data_path, 'DEM.asc')
        dem_array, self.geotransform, _ = read_dem(dem_file_path)
        x_size = dem_array.shape[1]
        y_size = dem_array.shape[0]
        self.dem_size = (x_size, y_size)

        # initialise a binary converter
        self.binary_converter = binary_coder(self.binary_coding)

        # read feature data
        feature_data_path = os.path.join(self.data_path, 'feature_data.txt')
        if not os.path.exists(feature_data_path):
            self.feature_lengths = []
            self.total_length = 0
            self.characteristic_lengths = []
            self.features_data = []
            self.feature_masks = {}
        else:
            self.features_data = load_features_data(
                feature_data_path, self.binary_converter.binary_coding)
            rep_data = get_representation_data(feature_data_path)
            self.feature_lengths = rep_data[0]
            self.characteristic_lengths = rep_data[2]

            if self.number_of_features != len(self.feature_lengths):
                raise ValueError(
                    f'Input number of features ({self.number_of_features}) '
                     'does not match the input feature data at: '
                    f'{feature_data_path} ({len(self.feature_lengths)}).')

        # read solutions (from solutions.txt)
        self.solution_genotypes = []
        if not os.path.exists(self.solution_path):
            raise FileNotFoundError(
                "solutions.txt not found at: {self.solution_path}")

        else:
            # eMOEA produces a tab-separated file
            try:
                df = pd.read_csv(self.solution_path, sep='\t',
                                 dtype={'Genotype': str})
            except pd.errors.EmptyDataError:
                df = pd.DataFrame()

            if "Genotype" not in df.columns and not df.empty:
                raise ValueError("solutions.txt missing 'Genotype' column.")

            if not df.empty:
                # Clean the genotype string: remove brackets, commas, spaces
                df["Genotype_clean"] = df["Genotype"].astype(str).str.replace(
                    r"[\s\[\],]", "", regex=True)

                # Validate and convert to numpy arrays
                for _, row in df.iterrows():
                    g_str = row["Genotype_clean"]

                    if len(g_str) != self.total_length:
                        continue

                    # Convert string '0101' to numpy array [0, 1, 0, 1]
                    self.solution_genotypes.append(
                        np.array([int(c) for c in g_str], dtype=int)
                    )

        # pre-load shapefiles

        # 1. Pre-load Pavements
        self.pavement_gdfs = {}
        pavements_folder = os.path.join(self.data_path, '03.Pavements')
        for i in range(self.number_of_pavements):
            shp_path = os.path.join(pavements_folder, f'zone_{i}.shp')
            if os.path.exists(shp_path):
                self.pavement_gdfs[i] = gpd.read_file(shp_path)

        # 2. Pre-load Rain Gardens
        self.raingarden_gdfs = {}
        gardens_folder = os.path.join(self.data_path, '05.RainGardens')
        for i in range(self.number_of_gardens):
            shp_path = os.path.join(gardens_folder, f'raingarden_{i}.shp')
            if os.path.exists(shp_path):
                self.raingarden_gdfs[i] = gpd.read_file(shp_path)

        # 3. Pre-load Green Areas
        self.greenarea_gdfs = {}
        greenarea_folder = os.path.join(self.data_path, '02.GreenAreas')
        for i in range(self.number_of_greenareas):
            shp_path = os.path.join(greenarea_folder, f'greenarea_{i}.shp')
            if os.path.exists(shp_path):
                self.greenarea_gdfs[i] = gpd.read_file(shp_path)

        # 4. Pre-load Exclusion Zone
        self._load_exclusion_zone()  # load exclusion zone .shp

        # 5. Pre-load Buildings Shapefile
        self._load_buildings_shapefile()

        # 6. Pre-load Pavements Shapefile
        self._load_pavements_shapefile()

    def prepare_and_plot_solutions(self):
        """Prepare solutions for plotting and then plot solutions.

        Prepare solutions for plotting by:
            1) Identifying SurfaceMap folders for the final solutions.
            2) Re-run exposure analyses.
        Exposure analysis must be re-run since the data required for plotting
        is deleted during the main loop of the algorithm to save memory.
        """
        # identify the folders for the final solutions
        self.solution_folders = self._identify_solution_folders()
        # plot solutions
        self._plot(self.solution_folders)

    def _load_buildings_shapefile(self):
        buildings_shp_path = os.path.join(self.data_path, '01.Buildings',
                                          'buildings.shp')

        if os.path.exists(buildings_shp_path):
            self.buildings_data = gpd.read_file(buildings_shp_path)
        else:
            self.buildings_data = None

    def _load_pavements_shapefile(self):
        pavements_shp_path = os.path.join(self.data_path, 'pavement-data',
                                          'pavements.shp')

        if os.path.exists(pavements_shp_path):
            self.pavements_data = gpd.read_file(pavements_shp_path)
        else:
            self.pavements_data = None

    def _identify_solution_folders(self):
        """Identify SurfaceMap folders for the final solutions."""
        solution_folders = []

        for genotype_array in self.solution_genotypes:
            genotype_id = str(binary_to_sim_integer(genotype_array))
            folder_name = f"Sim_{genotype_id}"
            folder_path = os.path.join(self.run_path, folder_name)

            solution_folders.append(folder_path)
            self._rasterize_exposure_output(folder_path)

        return solution_folders

    def _rasterize_exposure_output(self, folder_path):
        """Rasterize the max depth output data (csv -> asc)."""
        for name in os.listdir(folder_path):
            if not name.endswith("_max_depth.csv"):
                continue
            input_csv = os.path.join(folder_path, name)
            if not os.path.isfile(input_csv):
                continue
            print('Rasterising (.csv -> .tiff) max depth data')
            base = os.path.splitext(name)[0]  # strips .csv
            output_tiff = os.path.join(folder_path, f"{base}_max_depth.tiff")
            if not os.path.exists(output_tiff):
                self._csv_to_tiff(input_csv, output_tiff, self.geotransform,
                                self.dem_size)
                print(f"Max depth data {name} rasterised", )
            else:
                print(f"Max depth data already {name} rasterised")
            break
        else:
            raise FileNotFoundError(
                f"No '*_max_depth.csv' file found in {folder_path}")

    def _csv_to_tiff(self, input_csv, output_tiff, geotransform, dem_size,
                     projection=27700):
        """Convert a .csv file to GeoTIFF format.

        Parameters
        ----------
        input_csv : string
            Path to the input .csv file.
        output_tiff : string
            Path to the output GeoTIFF file.
        geotransform : array
            Affine transformation coefficients for transforming pixel/line
            coordinates to georeferenced space.
        size : tuple
            Tuple containing the size of the baseline DEM (x_size, y_size).
        projection : int, optional
            EPSG projection code (default is 27700 for British National Grid).
        """
        # Load the .csv file into a pandas DataFrame
        df = pd.read_csv(input_csv)
        dem_resolution = geotransform[1]
        # Determine the extent of the grid
        x_min = geotransform[0]  # Origin of X
        y_max = geotransform[3]  # Origin of Y (top of the image)
        # Determine the number of rows and columns
        x_count = dem_size[0]
        y_count = dem_size[1]
        # Create a numpy array to hold the elevation data
        nodata_value = -99999  # (initialize with NoData values)
        elevation_data = np.full((y_count, x_count), nodata_value,
                                 dtype=np.float32)
        # Populate the elevation data array
        for _, row in df.iterrows():
            x_idx = int((row['XCen'] - x_min) / dem_resolution)
            y_idx = -int((row['YCen'] - y_max) / dem_resolution)
            elevation_data[y_idx, x_idx] = row['Depth']
        # Create the output GeoTIFF file
        driver = gdal.GetDriverByName('GTiff')
        output_raster = driver.Create(output_tiff, x_count, y_count, 1,
                                      gdal.GDT_Float32)
        # Set the geotransform and projection
        output_raster.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(projection)
        output_raster.SetProjection(srs.ExportToWkt())
        # Write the elevation data to the raster
        output_raster.GetRasterBand(1).WriteArray(elevation_data)
        output_raster.GetRasterBand(1).SetNoDataValue(nodata_value)
        output_raster.FlushCache()
        # Close the dataset
        output_raster = None

        print(f"Successfully created GeoTIFF: {output_tiff}")

    def _load_exclusion_zone(self):
        exclusion_dir = os.path.join(self.data_path, "exclusion-data")
        exclusion_shp_path = os.path.join(exclusion_dir, 'exclusion_zone.shp')

        if os.path.exists(exclusion_shp_path):
            self.exclusion_zone = gpd.read_file(exclusion_shp_path)
        else:
            self.exclusion_zone = None

    def _plot(self, solution_folders):
        """Plot all solutions."""
        # Read solution data
        solution_num, cost, risk = None, None, None
        df = self._process_solution_data(self.total_length)

        if not df.empty:
            # Ensure Genotype column exists
            if "Genotype" not in df.columns:
                raise ValueError("Solutions.txt has no 'Genotype' column")

        for count, (folder_path, genotype) in enumerate(
                            zip(solution_folders, self.solution_genotypes)):
            solution_id = binary_to_sim_integer(np.array(genotype))
            try:
                genotype_flat = "".join(str(b) for b in genotype)
                row = df.loc[df["Genotype"] == genotype_flat]

                if not row.empty:
                    solution_num = row.index[0]
                    cost = row["Cost"].values[0]
                    risk = row["Risk"].values[0]
            except (KeyError, IndexError, AttributeError, TypeError) as e:
                raise ValueError(
                    f"Genotype {genotype} not found in Solutions.txt: {e}")

            # plot flood depths
            tiff_files = glob.glob(os.path.join(folder_path, "*.tiff"))
            if not tiff_files:
                continue
            flood_area_files = [rio.open(tiff_file, mode='r')
                                for tiff_file in tiff_files]

            # Global plotting settings
            fsize_w = 16
            fsize_h = 8
            dpi = 800
            plt.rc('font', size=10)
            plt.rc('axes', titlesize=16)
            plt.rc('axes', labelsize=12)
            plt.rc('xtick', labelsize=12)
            plt.rc('ytick', labelsize=12)
            plt.rc('legend', fontsize=10)

            # Extents for flood map
            xmin = self.geotransform[0]
            xmax = self.geotransform[0] + (
                self.geotransform[1] * self.dem_size[0])
            ymin = self.geotransform[3] + (
                self.geotransform[5] * self.dem_size[1])
            ymax = self.geotransform[3]

            # initialise plot
            _, ax_flood = plt.subplots(1, 1, figsize=(fsize_w, fsize_h),
                                       dpi=dpi)
            ax_flood.set_xlim(xmin, xmax)
            ax_flood.set_ylim(ymin, ymax)
            if solution_num is None:
                plot_title = (f'Solution ({solution_id}) ')
            else:
                plot_title = (f'Solution {solution_num} ({solution_id}) \n'
                              f'Cost = £{cost:.2f}, Risk = {risk:.3f}')
            ax_flood.set_title(plot_title)

            cmap = mpl.cm.Blues
            bounds_depth = [0.01, 0.05, 0.10, 0.15, 0.30, 0.50, 0.80]
            norm = mpl.colors.BoundaryNorm(bounds_depth, cmap.N)

            axins = inset_axes(
                ax_flood,
                width="2%",  # width of colorbar in % of plot width
                height="45%",  # height of colorbar in % of plot height
                loc=2,  # topright location
                bbox_to_anchor=(1.01, 0, 1, 1),  # space relative to plot
                bbox_transform=ax_flood.transAxes,
                borderpad=0)

            if self.exclusion_zone is not None:
                self.exclusion_zone.plot(ax=ax_flood, alpha=0.05, color='r')
            if self.buildings_data is not None:
                self.buildings_data.plot(color='grey', lw=0.05, alpha=0.25,
                                         edgecolor='grey', linewidth=0.05,
                                         legend=False, ax=ax_flood)
            if self.pavements_data is not None:
                self.pavements_data.boundary.plot(color='grey', linewidth=0.05,
                                                  ax=ax_flood)

            # plot the tiff files
            for flood_area_file in flood_area_files:
                show(flood_area_file, ax=ax_flood, title=plot_title,
                     cmap=cmap, norm=norm)

            # plot pavements
            start = 0
            end = self.number_of_pavements
            pavements_genotype = genotype[start:end]

            active_pavements = [
                self.pavement_gdfs[i]
                for i, bit in enumerate(pavements_genotype)
                if bit == 1 and i in self.pavement_gdfs
            ]

            if active_pavements:
                # Concatenate the pre-loaded dataframes
                pavements = gpd.GeoDataFrame(
                    pd.concat(active_pavements, ignore_index=True)
                )
                pavements.plot(color='springgreen', edgecolor='springgreen',
                               ax=ax_flood, lw=0.75)

            # plot rain gardens
            start = end
            end = start + self.number_of_gardens
            gardens_genotype = genotype[start:end]

            active_gardens = [
                self.raingarden_gdfs[i]
                for i, bit in enumerate(gardens_genotype)
                if bit == 1 and i in self.raingarden_gdfs
            ]

            if active_gardens:
                gardens = gpd.GeoDataFrame(
                    pd.concat(active_gardens, ignore_index=True)
                )
                gardens.plot(color='darkviolet', edgecolor='darkviolet',
                             ax=ax_flood, lw=1.5)

            # plot green areas
            start = end
            end = start + self.number_of_greenareas
            greenareas_genotype = genotype[start:end]

            active_greenareas = [
                self.greenarea_gdfs[i]
                for i, bit in enumerate(greenareas_genotype)
                if bit == 1 and i in self.greenarea_gdfs
            ]

            if active_greenareas:
                greenareas = gpd.GeoDataFrame(
                    pd.concat(active_greenareas, ignore_index=True)
                )
                greenareas.plot(color='darkolivegreen',
                                edgecolor='darkolivegreen', ax=ax_flood,
                                lw=0.75)

            # plot features
            for feat_idx, feat_len in enumerate(self.feature_lengths):
                start = end
                end = start + feat_len
                feature_genotype = genotype[start:end]
                # ensure list
                lengths = list(self.characteristic_lengths[feat_idx])
                # sanity check
                if sum(lengths) != len(feature_genotype):
                    raise ValueError(
                        f"Feature {feat_idx}: expected {sum(lengths)} bits, "
                        f"got {len(feature_genotype)}.")

                cumsum = np.cumsum([0] + lengths[:-1])
                binary_ints = [self.binary_converter.binary_to_integer(
                    feature_genotype[s:s + length]) if length > 0
                    else 0 for s, length in zip(cumsum, lengths)]

                fd = self.features_data[feat_idx]
                x_0, y_0 = fd['x0'], fd['y0']
                h = fd['h_min'] + binary_ints[0] * fd['delta_h']

                if h == 0:
                    # if pond depth is 0 then it is not included
                    # skip plotting this pond
                    pass
                else:
                    r = fd['r_min'] + binary_ints[1] * fd['delta_r']
                    dx = fd['dx_min'] + binary_ints[2] * fd['delta_dx']
                    dy = fd['dy_min'] + binary_ints[3] * fd['delta_dy']

                    # Calculate shifted origin
                    x_center = x_0 + dx
                    y_center = y_0 + dy

                    # Draw the Circle patch
                    circle_patch = Circle(
                        (x_center, y_center),
                        radius=r,           # Circle takes radius directly
                        edgecolor='black',
                        facecolor='none',   # Set to 'none' to draw only outline
                        lw=0.5
                    )
                    ax_flood.add_patch(circle_patch)
                    # Origin markers, size set to 10
                    # ax_flood.scatter(x_0, y_0, c='r', marker='x', s=5,
                    #                  label='Origin')
                    ax_flood.scatter(x_center, y_center, c='r', marker='+',
                                     s=1, label='Shifted Origin')

            # plot the colorbar of water depth
            plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                         ax=ax_flood, cax=axins, extend='both',
                         format='%.2f', boundaries=bounds_depth,
                         spacing='uniform', orientation='vertical',
                         label='Water Depth (m)')

            # Create custom legend using Patch
            legend_elements = [
                Patch(color='grey', label='Buildings'),
                Patch(facecolor='None', edgecolor='grey', linewidth=0.05,
                      label='Pavements'),
                Patch(facecolor='springgreen', alpha=0.4,
                      label='Permeable Paving'),
                Patch(facecolor='darkviolet', alpha=0.75, label='Rain Garden'),
                Patch(facecolor='darkolivegreen', alpha=0.4,
                      label='Green Area'),
                Patch(facecolor='black', label='Feature Footprint'),
                Patch(facecolor='red', alpha=0.1, label='Exclusion Zone')
            ]
            ax_flood.legend(handles=legend_elements, loc='upper right',
                            fontsize='10')

            plot_path = os.path.join(self.output_path,
                                     f'Solution {count}.{self.extension}')
            plt.savefig(plot_path, dpi=dpi)
            # plt.show(block=False)
            # plt.pause(0.1)
            plt.close()
            # Force garbage collection
            gc.collect()
            print('Flood map plotted for solution '
                  f'{solution_num} ({solution_id}).')

    def _process_solution_data(self, total_length):
        """Read Solutions.txt and return a dataframe.

        Construct a new dataframe accounting for long genotypes that span over
        multiple lines/rows.

        Parameters
        ----------
        total_length : int
            Total length of the genotype.

        Returns
        -------
        df : pandas dataframe
            A pandas dataframe containing data from Solutions.txt with columns
            "Genotype", "Cost", "Risk".
        """
        summary_data_path = os.path.join(self.data_path, 'solutions.txt')

        if not os.path.exists(summary_data_path):
            return pd.DataFrame()

        try:
            # Read the tab-separated file
            df = pd.read_csv(summary_data_path, sep="\t",
                             dtype={'Genotype': str})
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

        # Check if required columns are present
        required_cols = ["Genotype", "Cost", "Risk"]
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()

        df["Genotype"] = df["Genotype"].astype(str).str.replace(
            r"[\s\[\],]", "", regex=True)

        # Validate genotype lengths
        valid_mask = df["Genotype"].str.len() == total_length
        if not valid_mask.all():
            df = df[valid_mask].copy()

        # Ensure Cost and Risk are numeric and drop errors
        df["Cost"] = pd.to_numeric(df["Cost"], errors='coerce')
        df["Risk"] = pd.to_numeric(df["Risk"], errors='coerce')
        df.dropna(subset=["Cost", "Risk"], inplace=True)

        return df[["Genotype", "Cost", "Risk"]]


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    pass
