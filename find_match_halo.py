import pandas as pd
import numpy as np
from sklearn.neighbors import KDTree
from scipy.spatial import cKDTree
from time import sleep, time

def findin_rs(hal_vr_this, hal_rs_near_in):
    hal_rs_near_this = hal_rs[['X','Y','Z','VX','VY','VZ','Rvir']].copy()
    hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.X-hal_vr_this.Xc)<hal_vr_this.R_BN98]
    hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.Y-hal_vr_this.Yc)<hal_vr_this.R_BN98]
    hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.Z-hal_vr_this.Zc)<hal_vr_this.R_BN98]
#     if match_vel==True:
    hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VX-hal_vr_this.VXc)<np.abs(hal_vr_this.VXc)]
    hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VY-hal_vr_this.VYc)<np.abs(hal_vr_this.VYc)]
    hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VZ-hal_vr_this.VZc)<np.abs(hal_vr_this.VZc)]
    if hal_rs_near_this.shape[0]!=0:
        hal_rs_near['rel_size'] = np.abs(np.log(hal_rs_near_this.Rvir/1e3/hal_vr_this.R_BN98))
        return hal_rs_near_this.rel_size.idxmin()
    

    
def cross_match_old(hal_vr, hal_rs, dist_fac=0.5, match_vel=True):
    t_now = time()
    kdt = KDTree(hal_rs[['X','Y','Z']].to_numpy())
    t_bef, t_now = t_now, time()
    print(t_now-t_bef, 'kdtree constructed')
    neighbr = kdt.query_radius(hal_vr[['Xc','Yc','Zc']].to_numpy(), dist_fac*hal_vr.R_BN98.to_numpy())
    t_bef, t_now = t_now, time()
    print(t_now-t_bef, 'query done for spatial neighbours')
    matched_vr_int_idx = []
    matched_rs_idx = []
    for i in range(hal_vr.shape[0]):
        hal_vr_this_Rvir = hal_vr.R_BN98.iloc[i]
        t_bef, t_now = t_now, time()
#         print(t_now-t_bef, 'for this vr halo')
        hal_rs_near_this = hal_rs[['VX','VY','VZ','Rvir']].iloc[neighbr[i]].copy()
        t_bef, t_now = t_now, time()
#         print(t_now-t_bef, 'for this vr halo, neighbor halos from index')
        if match_vel==True:
            hal_vr_this = hal_vr[['VXc','VYc','VZc','R_BN98']].iloc[i]
            hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VX-hal_vr_this.VXc)<np.abs(hal_vr_this.VXc)]
            hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VY-hal_vr_this.VYc)<np.abs(hal_vr_this.VYc)]
            hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VZ-hal_vr_this.VZc)<np.abs(hal_vr_this.VZc)]
        if hal_rs_near_this.shape[0]!=0:
            hal_rs_near_this_Rvir = hal_rs_near_this.Rvir.to_numpy()
            hal_rs_near_this_idxs = hal_rs_near_this.index.to_numpy()
            hal_rs_near_this_idx = np.argmin(np.abs(np.log(hal_rs_near_this_Rvir/1e3/hal_vr_this_Rvir)))
            matched_rs_idx.append(hal_rs_near_this.index[hal_rs_near_this_idx])
            matched_vr_int_idx.append(i)
            t_bef, t_now = t_now, time()
#             print(t_now-t_bef, 'best match selected')
    matched_vr_idx = hal_vr.index[matched_vr_int_idx]
#     matched_rs_idx = hal_vr.index[matched_rs_int_idx]
    t_bef, t_now = t_now, time()
    print(t_now-t_bef)
    return pd.DataFrame(data={'vr':matched_vr_idx,'rs':matched_rs_idx})

def cross_match_metric(hal_vr, hal_rs, box_size, dist_fac=2, vel_offset=3000, metric_vel=0.01, metric_lograd=1):
    t_now = time()
    hal_rs_phase_sp = hal_rs[['X','Y','Z','VX','VY','VZ','Rvir']].to_numpy()
#     print(hal_rs_phase_sp)
    hal_rs_phase_sp[:,3:6] += vel_offset #hal_rs_phase_sp[:,3:6].min()
    hal_rs_phase_sp[:,3:6] *= metric_vel
    hal_rs_phase_sp[:,6] = np.log10(hal_rs_phase_sp[:,6])+1
    hal_rs_phase_sp[:,6] *= metric_lograd
#     print(hal_rs_phase_sp)
    kdt = cKDTree(hal_rs_phase_sp, boxsize=(box_size,)*6+(1e6,))
    t_bef, t_now = t_now, time()
    print(t_now-t_bef, 'kdtree constructed')
    hal_vr_phase_sp = hal_vr[['Xc','Yc','Zc','VXc','VYc','VZc','R_BN98']].to_numpy(copy=True)
    hal_vr_phase_sp[:,3:6] += vel_offset # hal_vr_phase_sp[:,3:6].min()
    hal_vr_phase_sp[:,3:6] *= metric_vel
    hal_vr_phase_sp[:,6] = np.log10(hal_vr_phase_sp[:,6])+4
    hal_vr_phase_sp[:,6] *= metric_lograd
    neighbr_dist, neighbr = kdt.query(hal_vr_phase_sp, 1, workers=16) # distance_upper_bound=dist_fac*hal_vr.R_BN98.mean(), 
#     print(hal_vr_phase_sp, neighbr_dist)
    t_bef, t_now = t_now, time()
    print(t_now-t_bef, 'query done for spatial neighbours')
    matched_rs_int_idx = neighbr #.T[0]
    match_found_this_vr = np.where(neighbr_dist<dist_fac*hal_vr.R_BN98.to_numpy(copy=True))
    matched_vr_idx = hal_vr.index[match_found_this_vr]
    matched_rs_idx = hal_rs.index[matched_rs_int_idx[match_found_this_vr]]
    t_bef, t_now = t_now, time()
    print(t_now-t_bef)
    return pd.DataFrame(data={'vr':matched_vr_idx.to_numpy(),'rs':matched_rs_idx.to_numpy()})


def cross_match(hal_vr, hal_rs, dist_fac=0.5, match_vel=True):
    t_now = time()
    kdt = cKDTree(hal_rs[['X','Y','Z']].to_numpy())
    t_bef, t_now = t_now, time()
    print(t_now-t_bef, 'kdtree constructed')
    neighbr = kdt.query(hal_vr[['Xc','Yc','Zc']].to_numpy(), 10, distance_upper_bound=dist_fac*hal_vr.R_BN98.mean())[1]
    t_bef, t_now = t_now, time()
    print(t_now-t_bef, 'query done for spatial neighbours')
    matched_vr_int_idx = []
    matched_rs_idx = []
    for i in range(hal_vr.shape[0]):
        hal_vr_this_Rvir = hal_vr.R_BN98.iloc[i]
        t_bef, t_now = t_now, time()
        print(t_now-t_bef, 'for this vr halo')
        neighbr = neighbr[neighbr<hal_vr.shape[0]]
        hal_rs_near_this = hal_rs[['VX','VY','VZ','Rvir']].iloc[neighbr[i]].copy()
        t_bef, t_now = t_now, time()
        print(t_now-t_bef, 'for this vr halo, neighbor halos from index')
        if match_vel==True:
            hal_vr_this = hal_vr[['VXc','VYc','VZc','R_BN98']].iloc[i]
            hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VX-hal_vr_this.VXc)<np.abs(hal_vr_this.VXc)]
            hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VY-hal_vr_this.VYc)<np.abs(hal_vr_this.VYc)]
            hal_rs_near_this = hal_rs_near_this.loc[np.abs(hal_rs_near_this.VZ-hal_vr_this.VZc)<np.abs(hal_vr_this.VZc)]
        if hal_rs_near_this.shape[0]!=0:
            hal_rs_near_this_Rvir = hal_rs_near_this.Rvir.to_numpy()
            hal_rs_near_this_idxs = hal_rs_near_this.index.to_numpy()
            hal_rs_near_this_idx = np.argmin(np.abs(np.log(hal_rs_near_this_Rvir/1e3/hal_vr_this_Rvir)))
            matched_rs_idx.append(hal_rs_near_this.index[hal_rs_near_this_idx])
            matched_vr_int_idx.append(i)
            t_bef, t_now = t_now, time()
            print(t_now-t_bef, 'best match selected')
    matched_vr_idx = hal_vr.index[matched_vr_int_idx]
#     matched_rs_idx = hal_vr.index[matched_rs_int_idx]
    t_bef, t_now = t_now, time()
    print(t_now-t_bef)
    return pd.DataFrame(data={'vr':matched_vr_idx,'rs':matched_rs_idx})

# def select_best_size():
    