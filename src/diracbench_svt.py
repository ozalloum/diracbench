import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.sparse import diags,bmat
from scipy.sparse.linalg import eigsh
from scipy.interpolate import BSpline
from scipy.linalg import eigh
from numpy.polynomial.legendre import leggauss

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

