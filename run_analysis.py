import event
import time


start_time = time.time()
folder = 't/'
event.evelyze(localizations_file=f'{folder}orig58_pf.hdf5',
              photons_file=f'{folder}orig58_index.hdf5',
              drift_file=f'{folder}orig58_drift.txt',
              offset=10,
              diameter=4.5,
              int_time=200,
              suffix='',
              max_dark_frames=1,
              proximity=2,
              filter_single=True,
              norm_brightness=True,
              dt_window=[0,2500],
              more_ms=0)
end_time = time.time()
print(f"Execution time: {end_time-start_time:.3f} seconds")

