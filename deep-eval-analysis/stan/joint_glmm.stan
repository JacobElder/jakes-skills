// joint_glmm.stan
// Hierarchical GLMM for eval analysis: IRT + SDT(probit reading) + calibration + G-theory bridge.
// Mirrors scripts/joint_glmm.py (PyMC) exactly. Probit accuracy link; optional latency (van der
// Linden), confidence (calibration), and 4PL upper-asymptote (slip) channels.
//
// COMPATIBILITY: uses the new Stan 2.27+ array syntax ("array[N] int x"). Requires cmdstan >= 2.27
// or RStan >= 2.21 / brms >= 2.17. Run `stanc joint_glmm.stan` first to confirm it parses.
//
// Parameter <-> framework map:
//   b[i], a[i]=exp(loga[i])      -> IRT difficulty / discrimination; SDT sensitivity & criterion (probit)
//   theta[v]                     -> variant latent ability
//   sig_la                       -> adaptive-shrinkage state on discrimination
//   d_up[i]                      -> 4PL upper asymptote (slip); bank-regime only
//   rho                          -> ability<->effort correlation (van der Linden identifiability)
//   cal_slope[v] = g1 + gc[v]    -> per-variant calibration slope
// G-theory empirical reliability is computed from the theta draws in the runner (matches synthesize.py).

data {
  int<lower=1> V;                 // variants (takers)
  int<lower=1> I;                 // items
  int<lower=1> N;                 // observations
  array[N] int<lower=1, upper=V> tv;    // variant index per obs (1-based)
  array[N] int<lower=1, upper=I> iv;    // item index per obs
  array[N] int<lower=0, upper=1> y;     // binary correctness
  int<lower=0, upper=1> use_corr; // estimate theta-tau correlation
  int<lower=0, upper=1> has_lat;  // latency/effort channel on
  int<lower=0, upper=1> has_conf; // confidence channel on
  int<lower=0, upper=1> use_slip; // 4PL upper asymptote
  int<lower=0> N_lat;             // = N if has_lat else 0
  vector[N_lat] lnT;              // log effort/length (CoT tokens, latency, ...)
  int<lower=0> N_conf;            // = N if has_conf else 0
  vector[N_conf] logitc;          // logit(confidence)
  real lnT_center;                // prior center for item time-intensity (0 if no latency)
}

transformed data {
  int I_slip = use_slip ? I : 0;
  int K_corr = use_corr ? 1 : 0;
  int V_te   = (has_lat && use_corr) ? V : 0;
  int V_tf   = (has_lat && (1 - use_corr)) ? V : 0;
  int I_lat  = has_lat ? I : 0;
  int K_lat  = has_lat ? 1 : 0;
  int K_conf = has_conf ? 1 : 0;
  int V_conf = has_conf ? V : 0;
}

parameters {
  vector[V] theta;                     // ability (unit scale: scale-fixing)
  real mu_b;  real<lower=0> sig_b;  vector[I] b;
  real mu_la; real<lower=0> sig_la; vector[I] loga;

  vector<lower=0, upper=1>[I_slip] d_up;

  // latency channel
  vector<lower=-0.95, upper=0.95>[K_corr] rho;
  vector[V_te] tau_e;                  // when correlated
  vector[V_tf] tau_free;               // when decoupled
  vector[I_lat] lam;
  vector[K_lat] mu_lam;
  vector<lower=0>[K_lat] sig_lam;
  vector<lower=0>[K_lat] kappa;
  vector<lower=0>[K_lat] sigT;

  // confidence channel
  vector[K_conf] g0;
  vector[K_conf] g1;
  vector<lower=0>[K_conf] sig_gc;
  vector[V_conf] gc;
  vector<lower=0>[K_conf] sigC;
}

transformed parameters {
  vector[I_lat] tau;                   // length 0 if no latency
  if (has_lat) {
    if (use_corr)
      tau = rho[1] * theta + sqrt(1 - square(rho[1])) * tau_e;
    else
      tau = tau_free;
  }
}

model {
  // ---- priors (match PyMC) ----
  theta ~ std_normal();
  mu_b ~ normal(0, 1);    sig_b ~ normal(0, 1);    b ~ normal(mu_b, sig_b);
  mu_la ~ normal(0, 0.5); sig_la ~ cauchy(0, 0.5); loga ~ normal(mu_la, sig_la);
  if (use_slip) d_up ~ beta(20, 1);

  // ---- accuracy channel (probit; optional 4PL slip) ----
  for (n in 1:N) {
    real eta = exp(loga[iv[n]]) * (theta[tv[n]] - b[iv[n]]);
    real p = Phi(eta);
    if (use_slip) p = d_up[iv[n]] * p;
    p = fmin(fmax(p, 1e-9), 1 - 1e-9);
    y[n] ~ bernoulli(p);
  }

  // ---- latency channel (van der Linden) ----
  if (has_lat) {
    if (use_corr) tau_e ~ std_normal(); else tau_free ~ std_normal();
    mu_lam ~ normal(lnT_center, 1);
    sig_lam ~ normal(0, 1);
    kappa ~ normal(0, 1);
    sigT ~ normal(0, 1);
    lam ~ normal(mu_lam[1], sig_lam[1]);
    for (n in 1:N)
      lnT[n] ~ normal(lam[iv[n]] - kappa[1] * tau[tv[n]], sigT[1]);
  }

  // ---- confidence channel (calibration) ----
  if (has_conf) {
    g0 ~ normal(0, 1);
    g1 ~ normal(1, 1);
    sig_gc ~ normal(0, 1);
    gc ~ normal(0, sig_gc[1]);
    sigC ~ normal(0, 1);
    for (n in 1:N)
      logitc[n] ~ normal(g0[1] + (g1[1] + gc[tv[n]]) * (theta[tv[n]] - b[iv[n]]), sigC[1]);
  }
}

generated quantities {
  vector[I] a = exp(loga);
  vector[V_conf] cal_slope;
  if (has_conf) cal_slope = g1[1] + gc;
}
