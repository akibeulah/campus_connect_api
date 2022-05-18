#! /usr/bin/env python

"""Create "truth" files for the tests contained in test_spectra_from_catalog.py
"""
import os
import astropy.units as u
from mirage.catalogs import spectra_from_catalog as spec
from mirage.catalogs import hdf5_catalog as hdf5
from mirage.utils.constants import FLAMBDA_CGS_UNITS, FNU_CGS_UNITS, MEAN_GAIN_VALUES


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data/hdf5_catalogs')


# for test_hdf5_file_input()
outfile = 'output_spec_from_hdf5_input_including_normalized.hdf5'
catfile = os.path.join(TEST_DATA_DIR, 'point_sources.cat')
sed_file = os.path.join(TEST_DATA_DIR, 'sed_file_with_normalized_dataset.hdf5')
sed_catalog = spec.make_all_spectra(catfile, input_spectra_file=sed_file,
                                    normalizing_mag_column='nircam_f444w_magnitude',
                                    output_filename=outfile, module='A')

# for test_manual_inputs()
catfile = os.path.join(TEST_DATA_DIR, 'point_sources.cat')
output_hdf5 = 'output_spec_from_manual_input.hdf5'
hdf5file = os.path.join(TEST_DATA_DIR, 'sed_file_with_normalized_dataset.hdf5')
sed_dict = hdf5.open(hdf5file)
sed_catalog = spec.make_all_spectra(catfile, input_spectra=sed_dict,
                                    normalizing_mag_column='nircam_f444w_magnitude',
                                    output_filename=output_hdf5, module='A')

# for test_manual_plus_file_inputs()
catfile = os.path.join(TEST_DATA_DIR, 'point_sources.cat')
sed_file = os.path.join(TEST_DATA_DIR, 'sed_file_with_normalized_dataset.hdf5')
output_hdf5 = 'output_spec_from_file_plus_manual_input.hdf5'
manual_sed = {}
manual_sed[7] = {"wavelengths": [0.9, 1.4, 1.9, 3.5, 5.1]*u.micron,
                 "fluxes": [1e-17, 1.1e-17, 1.5e-17, 1.4e-17, 1.1e-17] * FLAMBDA_CGS_UNITS}
sed_catalog = spec.make_all_spectra(catfile, input_spectra=manual_sed, input_spectra_file=sed_file,
                                    normalizing_mag_column='nircam_f444w_magnitude',
                                    output_filename=output_hdf5, module='A')

# for test_multiple_mag_columns()
catfile = os.path.join(TEST_DATA_DIR, 'point_sources.cat')
output_hdf5 = 'output_spec_from_multiple_filter.hdf5'
sed_catalog = spec.make_all_spectra(catfile, output_filename=output_hdf5)

#for test_single_mag_column()
catfile = os.path.join(TEST_DATA_DIR, 'point_sources_one_filter.cat')
output_hdf5 = 'output_spec_from_one_filter.hdf5'
sed_catalog = spec.make_all_spectra(catfile, output_filename=output_hdf5)

# for test_multiple_ascii_catalogs()
catfile = os.path.join(TEST_DATA_DIR, 'point_sources.cat')
galfile = os.path.join(TEST_DATA_DIR, 'galaxies.cat')
catalogs = [catfile, galfile]
output_hdf5 = 'source_sed_file_from_point_sources.hdf5'
sed_catalog = spec.make_all_spectra(catalogs, output_filename=output_hdf5)

