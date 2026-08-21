import type { QuantumKernelAggregate, QuantumKernelDataset } from "@/lib/types";

type Props = { quantum: QuantumKernelDataset };

const metric = (value: number | null | undefined, digits = 4) =>
  Number.isFinite(value) ? Number(value).toFixed(digits) : "N/D";

const pct = (value: number | null | undefined, digits = 1) =>
  Number.isFinite(value) ? `${(Number(value) * 100).toFixed(digits)}%` : "N/D";

const modelLabel: Record<string, string> = {
  logistic: "Regresión logística",
  rbfSvm: "SVM-RBF",
  quantumZZ: "Kernel cuántico ZZ",
};

function MetricCard({ result }: { result: QuantumKernelAggregate }) {
  const quantum = result.model === "quantumZZ";
  return (
    <article className={`qk-model-card${quantum ? " is-quantum" : ""}`}>
      <header><span>{modelLabel[result.model] ?? result.model}</span><b>{quantum ? "SHADOW" : "BASELINE"}</b></header>
      <strong>{metric(result.brierScore)}</strong>
      <p>Brier score <small>menor es mejor</small></p>
      <dl>
        <div><dt>ROC-AUC</dt><dd>{metric(result.rocAuc, 3)}</dd></div>
        <div><dt>ECE</dt><dd>{metric(result.ece, 3)}</dd></div>
        <div><dt>Balanceada</dt><dd>{pct(result.balancedAccuracy)}</dd></div>
        <div><dt>Folds</dt><dd>{result.folds}</dd></div>
      </dl>
    </article>
  );
}

export default function QuantumKernelLab({ quantum }: Props) {
  const isLive = quantum.mode === "live" && quantum.status === "completed";
  const grouped = quantum.horizons.map((horizon) => ({
    horizon,
    results: quantum.aggregateResults.filter((item) => item.horizonSessions === horizon),
    bootstrap: quantum.bootstrap.find((item) => item.horizonSessions === horizon),
  }));

  return (
    <div className="quantum-lab-page">
      <section className="qk-hero">
        <div className="qk-hero-copy">
          <p className="eyebrow">Q1 · experimento cuántico preregistrado</p>
          <h2>Quantum Kernel Lab</h2>
          <p>{quantum.hypothesis}</p>
          <div className="qk-target"><span>OBJETIVO BINARIO</span><strong>{quantum.decisionTarget}</strong></div>
        </div>
        <div className="qk-orbit" aria-label="Cuatro qubits simulados">
          <i /><i /><i /><i /><b>ψ</b>
        </div>
        <span className={`research-status ${isLive ? "is-live" : "is-sample"}`}>
          {isLive ? "Ejecución completada" : "Protocolo · ejecución manual"}
        </span>
      </section>

      <section className="qk-principle-strip">
        <article><span>Rol</span><strong>Shadow Challenger</strong><small>No modifica el Champion</small></article>
        <article><span>Qubits</span><strong>{quantum.design.qubits}</strong><small>{quantum.design.featureMap.name} · reps {quantum.design.featureMap.repetitions}</small></article>
        <article><span>Horizontes</span><strong>{quantum.horizons.join(" · ")}</strong><small>sesiones de mercado</small></article>
        <article><span>Backend</span><strong>Statevector</strong><small>simulación exacta clásica</small></article>
        <article><span>Promoción</span><strong>Manual</strong><small>nunca se autoautoriza</small></article>
      </section>

      <section className="qk-card qk-circuit-card">
        <div className="qk-section-heading"><div><p className="eyebrow">Arquitectura reproducible</p><h3>De 15 variables a una matriz de fidelidad</h3></div><span>{quantum.experimentId}</span></div>
        <div className="qk-pipeline">
          <article><b>15</b><span>variables point-in-time</span><small>mercado y riesgo</small></article><i>→</i>
          <article><b>4</b><span>componentes PCA</span><small>fit únicamente</small></article><i>→</i>
          <article className="quantum-node"><b>|ψ(x)⟩</b><span>ZZFeatureMap</span><small>4 qubits · entrelazado lineal</small></article><i>→</i>
          <article><b>K(x,y)</b><span>fidelidad cuántica</span><small>|⟨ψ(x)|ψ(y)⟩|²</small></article><i>→</i>
          <article><b>P</b><span>SVC + Platt</span><small>probabilidad calibrada</small></article>
        </div>
        <div className="qk-wires" aria-hidden="true">
          {[0, 1, 2, 3].map((wire) => <div key={wire}><span>q{wire}</span><i /><b>H</b><i /><b>RZ</b><i /><b className="entangle">ZZ</b><i /><b>M</b></div>)}
        </div>
      </section>

      {!isLive && <section className="qk-awaiting">
        <div className="qk-pulse"><i /><i /><b /></div>
        <div><p className="eyebrow">Ejecución deliberadamente separada</p><h3>El protocolo está listo; todavía no existen resultados cuánticos</h3><p>El workflow manual construirá el feature store, ejecutará los folds y conservará los JSON como artefacto privado. Solo publicará si se selecciona expresamente <code>publish_results=true</code>.</p></div>
      </section>}

      {isLive && grouped.map(({ horizon, results, bootstrap }) => <section className="qk-card" key={horizon}>
        <div className="qk-section-heading"><div><p className="eyebrow">Comparación fuera de muestra</p><h3>Horizonte de {horizon} sesiones</h3></div><span>{bootstrap ? `${pct(bootstrap.probabilityQuantumBetter)} prob. bootstrap` : "bootstrap pendiente"}</span></div>
        <div className="qk-model-grid">{results.map((result) => <MetricCard result={result} key={result.model} />)}</div>
        {bootstrap && <div className="qk-bootstrap"><span>Δ Brier cuántico - mejor clásico</span><strong>{metric(bootstrap.deltaMean)}</strong><small>IC 95% [{metric(bootstrap.ciLow)}, {metric(bootstrap.ciHigh)}] · {bootstrap.iterations} remuestreos por fecha</small></div>}
      </section>)}

      <section className="qk-two-column">
        <article className="qk-card">
          <p className="eyebrow">Protocolo temporal</p><h3>Controles contra leakage</h3>
          <ul className="qk-checklist">
            <li><b>01</b><span><strong>Walk-forward expansivo</strong>El año de prueba nunca participa en ajuste o calibración.</span></li>
            <li><b>02</b><span><strong>Doble purga</strong>{quantum.design.purge}.</span></li>
            <li><b>03</b><span><strong>Transformación congelada</strong>{quantum.design.preprocessing}.</span></li>
            <li><b>04</b><span><strong>Tres comparadores</strong>Logística, SVM-RBF y kernel ZZ usan exactamente las mismas filas.</span></li>
          </ul>
        </article>
        <article className="qk-card qk-governance">
          <p className="eyebrow">Gobernanza</p><h3>{quantum.governance.eligibleForPromotion ? "Elegible para revisión" : "Champion protegido"}</h3>
          <p>{quantum.governance.decision}</p>
          <div><span><i>✓</i> Huellas y semillas publicadas</span><span><i>✓</i> Historial append-only</span><span><i>✓</i> Artefacto privado por defecto</span><span><i>×</i> Trading automático desactivado</span></div>
        </article>
      </section>

      <section className="qk-card qk-limitations">
        <div><p className="eyebrow">Interpretación honesta</p><h3>Lo que este experimento no demuestra</h3></div>
        <ul>{quantum.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      </section>

      <section className="qk-sources">
        <span>BASE CIENTÍFICA</span>
        {quantum.sources.map((source, index) => <a key={source.url} href={source.url} target="_blank" rel="noreferrer"><b>0{index + 1}</b>{source.title} ↗</a>)}
      </section>
    </div>
  );
}
