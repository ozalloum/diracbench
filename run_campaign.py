from pathlib import Path
import argparse
import json
import shutil
import sys
import time
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.sparse import diags,bmat
from scipy.sparse.linalg import eigsh
from scipy.interpolate import BSpline
from scipy.linalg import eigh
from numpy.polynomial.legendre import leggauss

PACKAGE_ROOT = Path(__file__).resolve().parent


def _parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'Regenerate the DiracBench numerical campaign in a selected output '
            'directory. Existing campaign files may be refreshed; unrelated '
            'files are preserved.'
        )
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=PACKAGE_ROOT / 'generated_campaign',
        help='directory for regenerated CSV files, figures, metadata, and source',
    )
    return parser.parse_args()


args = _parse_args()
root = args.output.expanduser().resolve()
root.mkdir(parents=True, exist_ok=True)
for s in ['src', 'data', 'figures']:
    (root / s).mkdir(parents=True, exist_ok=True)

# Keep a copy of the reusable solver alongside regenerated outputs. The
# previous release reconstructed this file by slicing the campaign script and
# wrote to a machine-specific absolute path; both behaviours made the release
# fragile outside the original execution environment.
package_source = PACKAGE_ROOT / 'src' / 'diracbench_svt.py'
output_source = root / 'src' / 'diracbench_svt.py'
if package_source.exists() and package_source.resolve() != output_source.resolve():
    shutil.copy2(package_source, output_source)
elif not output_source.exists():
    raise FileNotFoundError(f'Missing reusable solver module: {package_source}')
M=1.0

def ws(r,R,a): return 1/(1+np.exp((np.asarray(r)-R)/a))
def pots(r,p):
    f=ws(r,p['R'],p['a']); return p['S0']*f,p['V0']*f,p['U0']*f

def rhs(r,y,E,k,p):
    F,G=y; S,V,U=pots(np.array([r]),p); S,V,U=float(S[0]),float(V[0]),float(U[0])
    Sig,Del=V+S,V-S; K=k/r-U
    return [-K*F+(E+M-Del)*G, K*G-(E-M-Sig)*F]

def det(E,k,p,rmax=25,rm=None,eps=1e-5):
    if rm is None: rm=p['R']
    l=k if k>0 else -k-1; F0=eps**(l+1)
    S,V,U=pots(np.array([eps]),p); Del=float(V[0]-S[0]); U=float(U[0])
    G0=((l+1)*eps**l+(k/eps-U)*F0)/(E+M-Del)
    so=solve_ivp(lambda r,y:rhs(r,y,E,k,p),(eps,rm),[F0,G0],method='DOP853',rtol=3e-10,atol=1e-12)
    lam=np.sqrt(max(1-E*E,1e-14)); Fm=np.exp(-lam*rmax); Gm=-lam/(E+1)*Fm
    si=solve_ivp(lambda r,y:rhs(r,y,E,k,p),(rmax,rm),[Fm,Gm],method='DOP853',rtol=3e-10,atol=1e-12)
    Fo,Go=so.y[:,-1]; Fi,Gi=si.y[:,-1]; no=np.hypot(Fo,Go);ni=np.hypot(Fi,Gi)
    return (Fo*Gi-Go*Fi)/(no*ni)

def shoot(k,p,lo,hi,rmax=25,rm=None): return brentq(lambda E:det(E,k,p,rmax,rm),lo,hi,xtol=2e-12)

def shoot_wave(E,k,p,rmax=25,grid=None,rm=None,eps=1e-5):
    if rm is None:rm=p['R']
    if grid is None:grid=np.linspace(1e-3,rmax,2500)
    l=k if k>0 else -k-1;F0=eps**(l+1);S,V,U=pots(np.array([eps]),p);Del=float(V[0]-S[0]);U=float(U[0])
    G0=((l+1)*eps**l+(k/eps-U)*F0)/(E+1-Del)
    go=grid[grid<=rm];go=np.r_[eps,go[go>eps]]
    so=solve_ivp(lambda r,y:rhs(r,y,E,k,p),(eps,rm),[F0,G0],t_eval=go,method='DOP853',rtol=3e-11,atol=1e-13)
    lam=np.sqrt(1-E*E);Fm=np.exp(-lam*rmax);Gm=-lam/(E+1)*Fm
    gi=grid[grid>=rm];gi=np.r_[gi[gi<rmax],rmax]
    si=solve_ivp(lambda r,y:rhs(r,y,E,k,p),(rmax,rm),[Fm,Gm],t_eval=gi[::-1],method='DOP853',rtol=3e-11,atol=1e-13)
    yo=so.y[:,-1];yi=si.y[:,-1];scale=np.dot(yo,yi)/np.dot(yi,yi);ri=si.t[::-1];Fi=si.y[0][::-1]*scale;Gi=si.y[1][::-1]*scale
    F=np.where(grid<=rm,np.interp(grid,so.t,so.y[0]),np.interp(grid,ri,Fi));G=np.where(grid<=rm,np.interp(grid,so.t,so.y[1]),np.interp(grid,ri,Gi))
    n=np.sqrt(np.trapezoid(F*F+G*G,grid));return grid,F/n,G/n

def fd(k,p,rmax=25,N=900,nev=12,sigma=.8):
    h=rmax/(N+1);r=np.arange(1,N+1)*h;S,V,U=pots(r,p);Sig=V+S;Del=V-S;K=k/r-U
    D=diags([-np.ones(N-1)/(2*h),np.ones(N-1)/(2*h)],[-1,1],shape=(N,N),format='csr')
    H=bmat([[diags(1+Sig),-D+diags(K)],[D+diags(K),diags(-1+Del)]],format='csr')
    vals,vecs=eigsh(H,k=nev,sigma=sigma,which='LM');idx=np.argsort(vals);return vals[idx],vecs[:,idx],r

def chD(N):
    x=np.cos(np.pi*np.arange(N+1)/N);c=np.ones(N+1);c[0]=c[-1]=2;c*=(-1)**np.arange(N+1);X=np.tile(x,(N+1,1)).T;dX=X-X.T
    D=np.outer(c,1/c)/(dX+np.eye(N+1));D-=np.diag(np.sum(D,axis=1));return D,x

def cheb(k,p,rmax=25,N=120):
    Dx,x=chD(N);r=(1-x)*rmax/2;Dr=-2*Dx/rmax;rr=r[1:N];D=Dr[1:N,1:N];S,V,U=pots(rr,p);Sig=V+S;Del=V-S;K=k/rr-U
    H=np.block([[np.diag(1+Sig),-D+np.diag(K)],[D+np.diag(K),np.diag(-1+Del)]])
    vals,vecs=np.linalg.eig(H);mask=np.abs(np.imag(vals))<1e-8;vals=np.real(vals[mask]);vecs=np.real(vecs[:,mask]);idx=np.argsort(vals);return vals[idx],vecs[:,idx],rr

def basis(rmax,n,deg):
    ni=n-deg-1;inter=np.linspace(0,rmax,ni+2)[1:-1] if ni>0 else np.array([]);kn=np.r_[np.zeros(deg+1),inter,np.full(deg+1,rmax)];bs=[]
    for i in range(n):c=np.zeros(n);c[i]=1;bs.append(BSpline(kn,c,deg,extrapolate=False))
    return kn,bs

def gmesh(kn,q=12):
    xg,wg=leggauss(q);xs=[];ww=[];u=np.unique(kn)
    for a,b in zip(u[:-1],u[1:]):
        if b>a:xs.append((b-a)*xg/2+(a+b)/2);ww.append((b-a)*wg/2)
    return np.concatenate(xs),np.concatenate(ww)

def dkb(k,p,rmax=25,n=46,deg=5,q=12):
    kn,bs=basis(rmax,n,deg);ids=list(range(1,n-1));x,w=gmesh(kn,q);B=np.column_stack([bs[i](x) for i in ids]);dB=np.column_stack([bs[i].derivative(1)(x) for i in ids]);ddB=np.column_stack([bs[i].derivative(2)(x) for i in ids])
    S,V,U=pots(x,p);Sig=V+S;Del=V-S;K=k/x-U;f=ws(x,p['R'],p['a']);Up=p['U0']*(-f*(1-f)/p['a']);Kp=-k/x**2-Up;fac=.5
    Fu=B;Gu=fac*(dB+K[:,None]*B);dFu=dB;dGu=fac*(ddB+Kp[:,None]*B+K[:,None]*dB);Fv=fac*(-dB+K[:,None]*B);Gv=B;dFv=fac*(-ddB+Kp[:,None]*B+K[:,None]*dB);dGv=dB
    F=np.c_[Fu,Fv];G=np.c_[Gu,Gv];dF=np.c_[dFu,dFv];dG=np.c_[dGu,dGv];HF=(1+Sig)[:,None]*F-dG+K[:,None]*G;HG=dF+K[:,None]*F+(-1+Del)[:,None]*G;W=w[:,None]
    Sm=F.T@(W*F)+G.T@(W*G);Hm=F.T@(W*HF)+G.T@(W*HG);Sm=(Sm+Sm.T)/2;Hm=(Hm+Hm.T)/2;return eigh(Hm,Sm,check_finite=False)

def near(vals,t):
    v=vals[(vals>0)&(vals<1)];return float(v[np.argmin(abs(v-t))])
def nodes(F,thr=.01):
    F=np.asarray(F);s=np.sign(F[np.abs(F)>thr*np.max(abs(F))]);return int(np.sum(s[1:]*s[:-1]<0))
def alt(F):
    s=np.sign(F);return float(np.mean(s[1:]*s[:-1]<0))

sets={'P1':dict(S0=-.60,V0=.20,U0=0.,R=5.,a=.60),'P2':dict(S0=-.60,V0=.20,U0=.08,R=5.,a=.60),'P3':dict(S0=-.70,V0=.25,U0=-.06,R=5.5,a=.75)}
pd.DataFrame([{'set':k,**v} for k,v in sets.items()]).to_csv(root/'data/original_parameter_sets.csv',index=False)
# Angular channels
br={-1:(.75,.85),1:(.95,.99),-2:(.90,.95)};rows=[]
for k in [-1,1,-2]:
    Es=shoot(k,sets['P1'],*br[k]);vf,_,_=fd(k,sets['P1'],N=900,sigma=Es);vc,_,_=cheb(k,sets['P1'],N=120);vd,_=dkb(k,sets['P1'],n=46);vals=[Es,near(vf,Es),near(vc,Es),near(vd,Es)]
    rows.append(dict(kappa=k,shooting=vals[0],finite_difference=vals[1],chebyshev=vals[2],dkb_bspline=vals[3],cross_method_spread=max(vals)-min(vals)))
energy=pd.DataFrame(rows);energy.to_csv(root/'data/four_method_angular_channels.csv',index=False)
# parameter sets
brs={'P1':(.75,.85),'P2':(.80,.86),'P3':(.68,.78)};rows=[]
for name,p in sets.items():
    Es=shoot(-1,p,*brs[name],rmax=30,rm=p['R']);vf,_,_=fd(-1,p,rmax=30,N=1000,sigma=Es);vc,_,_=cheb(-1,p,rmax=30,N=120);vd,_=dkb(-1,p,rmax=30,n=52);vals=[Es,near(vf,Es),near(vc,Es),near(vd,Es)];rows.append(dict(set=name,shooting=vals[0],finite_difference=vals[1],chebyshev=vals[2],dkb_bspline=vals[3],cross_method_spread=max(vals)-min(vals)))
pset=pd.DataFrame(rows);pset.to_csv(root/'data/four_method_parameter_sets.csv',index=False)
# tensor sweep continuation brackets
rows=[]; prev=.798575
for U0 in np.linspace(-.12,.12,7):
    p={**sets['P1'],'U0':float(U0)}; center=.798575+0.34*U0; Es=shoot(-1,p,center-.025,center+.025);vf,_,_=fd(-1,p,N=700,sigma=Es);vc,_,_=cheb(-1,p,N=100);vd,_=dkb(-1,p,n=42);vals=[Es,near(vf,Es),near(vc,Es),near(vd,Es)];rows.append(dict(U0=U0,shooting=vals[0],finite_difference=vals[1],chebyshev=vals[2],dkb_bspline=vals[3],cross_method_spread=max(vals)-min(vals)))
tensor=pd.DataFrame(rows);tensor.to_csv(root/'data/tensor_strength_sweep.csv',index=False)
# rmax
rows=[]
for rx in [15,20,25,30,35]:
    Es=shoot(-1,sets['P1'],.78,.82,rmax=rx);N=36*rx;vf,_,_=fd(-1,sets['P1'],rmax=rx,N=N,sigma=Es);vc,_,_=cheb(-1,sets['P1'],rmax=rx,N=120);nb=round(1.84*rx);vd,_=dkb(-1,sets['P1'],rmax=rx,n=nb);rows.append(dict(rmax=rx,shooting=Es,finite_difference=near(vf,Es),chebyshev=near(vc,Es),dkb_bspline=near(vd,Es),fd_N=N,dkb_basis=nb))
rmdf=pd.DataFrame(rows);rmdf.to_csv(root/'data/rmax_independence.csv',index=False)
# convergence
eref=float(energy[energy.kappa==-1].shooting.iloc[0]);conv=[]
for N in [200,300,450,650,900,1200]:
    t=time.perf_counter();v,_,_=fd(-1,sets['P1'],N=N,sigma=eref);dt=time.perf_counter()-t;E=near(v,eref);conv.append(dict(method='FD',resolution=N,energy=E,abs_error=abs(E-eref),runtime_s=dt))
for N in [40,60,80,100,120,160]:
    t=time.perf_counter();v,_,_=cheb(-1,sets['P1'],N=N);dt=time.perf_counter()-t;E=near(v,eref);conv.append(dict(method='Chebyshev',resolution=N,energy=E,abs_error=abs(E-eref),runtime_s=dt))
for N in [28,34,40,46,52,58]:
    t=time.perf_counter();v,_=dkb(-1,sets['P1'],n=N);dt=time.perf_counter()-t;E=near(v,eref);conv.append(dict(method='DKB B-spline',resolution=N,energy=E,abs_error=abs(E-eref),runtime_s=dt))
conv=pd.DataFrame(conv);conv.to_csv(root/'data/resolution_convergence.csv',index=False)
# spurious
vals,vecs,r=fd(-1,sets['P1'],N=900,sigma=.9,nev=10);bb=[(j,float(E)) for j,E in enumerate(vals) if 0<E<1];sp=[]
for j,E in bb:sp.append(dict(energy=E,nodes_1pct=nodes(vecs[:900,j]),alternation_fraction=alt(vecs[:900,j])))
sp=pd.DataFrame(sp);sp.to_csv(root/'data/fd_spurious_state_diagnostic.csv',index=False)
# runtime 3 reps
bench=[]
for method in ['Shooting','FD','Chebyshev','DKB B-spline']:
    ts=[]
    for _ in range(3):
        t=time.perf_counter()
        if method=='Shooting':shoot(-1,sets['P1'],.75,.85)
        elif method=='FD':fd(-1,sets['P1'],N=900,sigma=.8)
        elif method=='Chebyshev':cheb(-1,sets['P1'],N=120)
        else:dkb(-1,sets['P1'],n=46)
        ts.append(time.perf_counter()-t)
    bench.append(dict(method=method,median_runtime_s=float(np.median(ts)),min_runtime_s=float(min(ts)),max_runtime_s=float(max(ts))))
bench=pd.DataFrame(bench);bench.to_csv(root/'data/performance_benchmark.csv',index=False)
# wavefunction FD/Cheb vs shooting
grid=np.linspace(1e-3,25,2500);_,Fs,Gs=shoot_wave(eref,-1,sets['P1'],grid=grid);vf,vfd,rfd=fd(-1,sets['P1'],N=900,sigma=eref);jf=np.argmin(abs(vf-eref));Ff=vfd[:900,jf];Gf=vfd[900:,jf];nn=np.sqrt(np.trapezoid(Ff*Ff+Gf*Gf,rfd));Ff/=nn;Gf/=nn;Ffi=np.interp(grid,rfd,Ff,left=0,right=0);Gfi=np.interp(grid,rfd,Gf,left=0,right=0)
if np.trapezoid(Ffi*Fs+Gfi*Gs,grid)<0:Ffi*=-1;Gfi*=-1
vc,vch,rch=cheb(-1,sets['P1'],N=120);jc=np.argmin(abs(vc-eref));nch=len(rch);Fc=vch[:nch,jc];Gc=vch[nch:,jc];o=np.argsort(rch);rr=rch[o];Fc=Fc[o];Gc=Gc[o];nn=np.sqrt(np.trapezoid(Fc*Fc+Gc*Gc,rr));Fc/=nn;Gc/=nn;Fci=np.interp(grid,rr,Fc,left=0,right=0);Gci=np.interp(grid,rr,Gc,left=0,right=0)
if np.trapezoid(Fci*Fs+Gci*Gs,grid)<0:Fci*=-1;Gci*=-1
wm=pd.DataFrame([dict(pair='FD vs shooting',L2_difference=float(np.sqrt(np.trapezoid((Ffi-Fs)**2+(Gfi-Gs)**2,grid))),overlap=float(np.trapezoid(Ffi*Fs+Gfi*Gs,grid))),dict(pair='Chebyshev vs shooting',L2_difference=float(np.sqrt(np.trapezoid((Fci-Fs)**2+(Gci-Gs)**2,grid))),overlap=float(np.trapezoid(Fci*Fs+Gci*Gs,grid)))])
wm.to_csv(root/'data/wavefunction_comparison.csv',index=False)
pd.DataFrame({'r':grid,'shooting_F':Fs,'shooting_G':Gs,'finite_difference_F':Ffi,'finite_difference_G':Gfi,'chebyshev_F':Fci,'chebyshev_G':Gci}).to_csv(root/'data/wavefunction_profiles.csv',index=False)
# figures
plt.figure(figsize=(7,5))
for c,l in [('shooting','Shooting'),('finite_difference','Finite difference'),('chebyshev','Chebyshev'),('dkb_bspline','DKB B-spline')]:plt.plot(tensor.U0,tensor[c],marker='o',label=l)
plt.xlabel('Tensor strength $U_0$');plt.ylabel('Lowest $\\kappa=-1$ energy');plt.legend();plt.tight_layout();plt.savefig(root/'figures/fig_tensor_sweep.pdf');plt.savefig(root/'figures/fig_tensor_sweep.png',dpi=200);plt.close()
plt.figure(figsize=(7,5))
for c,l in [('shooting','Shooting'),('finite_difference','Finite difference'),('chebyshev','Chebyshev'),('dkb_bspline','DKB B-spline')]:plt.plot(rmdf.rmax,rmdf[c],marker='o',label=l)
plt.xlabel('$r_{\\max}$');plt.ylabel('Lowest $\\kappa=-1$ energy');plt.legend();plt.tight_layout();plt.savefig(root/'figures/fig_rmax_independence.pdf');plt.savefig(root/'figures/fig_rmax_independence.png',dpi=200);plt.close()
plt.figure(figsize=(7,5))
for m,g in conv.groupby('method'):plt.semilogy(g.resolution,g.abs_error,marker='o',label=m)
plt.xlabel('Grid/collocation/basis resolution');plt.ylabel('Absolute energy error vs shooting');plt.legend();plt.tight_layout();plt.savefig(root/'figures/fig_resolution_convergence.pdf');plt.savefig(root/'figures/fig_resolution_convergence.png',dpi=200);plt.close()
plt.figure(figsize=(7,5));plt.plot(grid,Fs,label='Shooting F');plt.plot(grid,Ffi,label='FD F');plt.plot(grid,Fci,label='Chebyshev F');plt.xlabel('$r$');plt.ylabel('Normalized large component $F(r)$');plt.legend();plt.tight_layout();plt.savefig(root/'figures/fig_wavefunction_comparison.pdf');plt.savefig(root/'figures/fig_wavefunction_comparison.png',dpi=200);plt.close()
phys=min(bb,key=lambda x:abs(x[1]-eref))[0];others=[x for x in bb if x[0]!=phys];sj=min(others,key=lambda x:abs(x[1]-.97))[0];Fp=vecs[:900,phys]/np.max(abs(vecs[:900,phys]));Fsp=vecs[:900,sj]/np.max(abs(vecs[:900,sj]));pd.DataFrame({'r':r,'physical_F':Fp,'oscillatory_F':Fsp}).to_csv(root/'data/spurious_state_profiles.csv',index=False);plt.figure(figsize=(7,5));plt.plot(r,Fp,label=f'Physical candidate E={vals[phys]:.6f}');plt.plot(r,Fsp,label=f'Oscillatory candidate E={vals[sj]:.6f}');plt.xlim(0,12);plt.xlabel('$r$');plt.ylabel('Scaled large component');plt.legend();plt.tight_layout();plt.savefig(root/'figures/fig_fd_spurious_diagnostic.pdf');plt.savefig(root/'figures/fig_fd_spurious_diagnostic.png',dpi=200);plt.close()
plt.figure(figsize=(7,5));plt.bar(bench.method,bench.median_runtime_s);plt.ylabel('Median runtime (s)');plt.xticks(rotation=20);plt.tight_layout();plt.savefig(root/'figures/fig_performance.pdf');plt.savefig(root/'figures/fig_performance.png',dpi=200);plt.close()
print('ENERGY\n',energy.to_string(index=False));print('TENSOR MAX SPREAD',tensor.cross_method_spread.max());print('SPURIOUS\n',sp.to_string(index=False));print('BENCH\n',bench.to_string(index=False));print('WAVE\n',wm.to_string(index=False))

# The compact numerical campaign above remains the authoritative generator for
# the CSV tables. These two post-processing modules add the publication-facing
# error analysis and consistently styled figures without duplicating solver
# logic in the plotting layer.
sys.path.insert(0, str(PACKAGE_ROOT))
from scripts.analyze_errors import analyze_error_outputs
from scripts.plot_publication_figures import make_publication_figures

analysis_summary = analyze_error_outputs(root)
make_publication_figures(root)
(root / 'data' / 'campaign_metadata.json').write_text(
    json.dumps(
        {
            'program': 'DiracBench',
            'python': sys.version,
            'output_directory': '.',
            'analysis_summary': analysis_summary,
        },
        indent=2,
    ) + '\n',
    encoding='utf-8',
)
print(f'REGENERATED OUTPUT: {root}')
