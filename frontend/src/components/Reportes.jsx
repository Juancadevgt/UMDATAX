import { useState } from "react";
import { exportarReportePBI } from "../services/api";

const REPORTES = [
  {
    id: 1,
    nombre: "EXISTENCIA POR PRODUCTO Y UBICACION",
    url: "https://app.fabric.microsoft.com/view?r=eyJrIjoiMTNjYTY4MTItZjIxNS00YmQ2LTkwYzctODVhOGFjZmQ2YTJjIiwidCI6ImJiZDI2Mzk1LTI2ZDEtNDk5Zi1hOGExLWVhNWYyZjkxNjU2OSJ9"
  }
];

export default function Reportes({ onVolver }) {
  const [estados, setEstados] = useState({});
  const [errores, setErrores] = useState({});

  const handleExportar = async (reporte) => {
    setEstados(prev => ({ ...prev, [reporte.id]: "cargando" }));
    setErrores(prev => ({ ...prev, [reporte.id]: null }));

    try {
      const blob = await exportarReportePBI(reporte.url, reporte.nombre);

      const urlBlob = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = urlBlob;
      a.download = `${reporte.nombre.replace(/ /g, "_")}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(urlBlob);

      setEstados(prev => ({ ...prev, [reporte.id]: "ok" }));

    } catch (err) {
      setEstados(prev => ({ ...prev, [reporte.id]: "error" }));
      setErrores(prev => ({
        ...prev,
        [reporte.id]: "No se pudo exportar. Verifica que el reporte sea público."
      }));
    }
  };

  const getBadge = (id) => {
    const estado = estados[id];
    if (!estado) return null;
    const estilos = {
      cargando: { bg: "#0d2a3d", color: "#378ADD", texto: "Exportando..." },
      ok:       { bg: "#1a3a1a", color: "#5cb85c", texto: "✓ Descargado" },
      error:    { bg: "#3a1a1a", color: "#e05555", texto: "Error" },
    };
    const s = estilos[estado];
    return (
      <span style={{
        fontSize: 12,
        background: s.bg,
        color: s.color,
        padding: "3px 10px",
        borderRadius: 20,
        marginRight: 10
      }}>
        {s.texto}
      </span>
    );
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      padding: 20,
      maxWidth: 700,
      margin: "0 auto"
    }}>

      {/* Header */}
      <div style={{ marginBottom: 30 }}>
        <button onClick={onVolver} style={{ marginBottom: 20 }}>
          ← Volver
        </button>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 6
        }}>
          <img
            src="/logo2.png"
            alt="logo"
            style={{ width: 30, height: 30, objectFit: "contain" }}
          />
          <h2 style={{ margin: 0, fontSize: 22 }}>UMDATAX</h2>
        </div>
        <h4 style={{ margin: 0, color: "#aaa", fontWeight: 400 }}>
          Reportes Power BI — Exportar a Excel
        </h4>
      </div>

      {/* Lista de reportes */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {REPORTES.map(reporte => (
          <div
            key={reporte.id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              border: "1px solid #444",
              borderRadius: 10,
              padding: "14px 18px",
              gap: 12,
              flexWrap: "wrap"
            }}
          >
            <p style={{
              margin: 0,
              fontWeight: 500,
              fontSize: 14,
              flex: 1
            }}>
              {reporte.nombre}
            </p>

            <div style={{ display: "flex", alignItems: "center" }}>
              {getBadge(reporte.id)}
              <button
                onClick={() => handleExportar(reporte)}
                disabled={estados[reporte.id] === "cargando"}
                style={{
                  background: estados[reporte.id] === "cargando" ? "#333" : "#185FA5",
                  color: estados[reporte.id] === "cargando" ? "#aaa" : "white",
                  border: "none",
                  borderRadius: 8,
                  padding: "7px 16px",
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: estados[reporte.id] === "cargando" ? "not-allowed" : "pointer"
                }}
              >
                {estados[reporte.id] === "cargando" ? "Exportando..." : "Exportar Excel"}
              </button>
            </div>

            {errores[reporte.id] && (
              <p style={{ margin: 0, fontSize: 12, color: "#e05555", width: "100%" }}>
                {errores[reporte.id]}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <footer style={{
        marginTop: 40,
        paddingTop: 15,
        borderTop: "1px solid #333",
        textAlign: "center",
        fontSize: 12,
        color: "#555"
      }}>
        Versión 1.0.0 · Soporte: juan.jimenez@umbralcorp.com
      </footer>

    </div>
  );
}